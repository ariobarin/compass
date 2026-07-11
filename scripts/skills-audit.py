#!/usr/bin/env python3
"""Measure the skill routing surface without retaining raw session content."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

DEFAULT_CONTEXT_TOKENS = 272_000
DEFAULT_BUDGET_PERCENT = 2.0
DEFAULT_CHARS_PER_TOKEN = 4.0
DEFAULT_DUPLICATE_THRESHOLD = 0.85
DEFAULT_DESCRIPTION_CANDIDATE_CHARS = 120
SKILL_LINE_RE = re.compile(r"^-\s+(\S+):(?:\s+(.*?))?\s+\(file:\s+(.+)\)$")
ROOT_LINE_RE = re.compile(r"^-\s+`(r\d+)`\s+=\s+`([^`]+)`$")
SENSITIVE_LOG_NAMES = {"auth.json", "credentials.json", ".env"}


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    file: str
    real_file: str
    root: str
    scope: str
    body_key: str
    description_key: str
    live: bool = False
    order: int | None = None
    render_path: str | None = None


@dataclass(frozen=True)
class DuplicatePair:
    left: str
    right: str
    kind: str
    similarity: float


@dataclass(frozen=True)
class UsageSummary:
    scanned_files: int
    scanned_bytes: int
    truncated: bool
    hits: dict[str, int]


def normalize_words(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def word_set(text: str) -> set[str]:
    return {word for word in normalize_words(text).split() if len(word) >= 2}


def jaccard(left: str, right: str) -> float:
    a = word_set(left)
    b = word_set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def parse_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> Skill | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    closing = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), -1)
    if closing < 0:
        return None

    fields: dict[str, str] = {}
    index = 1
    while index < closing:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[index])
        if not match:
            index += 1
            continue
        key, raw = match.groups()
        if raw.strip() in {"|", ">"}:
            block: list[str] = []
            index += 1
            while index < closing and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                block.append(lines[index].strip())
                index += 1
            fields[key] = " ".join(part for part in block if part).strip()
            continue
        fields[key] = parse_scalar(raw)
        index += 1

    name = fields.get("name", path.parent.name).strip()
    description = re.sub(r"\s+", " ", fields.get("description", "")).strip()
    if not name:
        return None
    body = "\n".join(lines[closing + 1 :])
    real_file = str(path.resolve())
    return Skill(
        name=name,
        description=description,
        file=str(path),
        real_file=real_file,
        root=str(path.parent.parent),
        scope="filesystem",
        body_key=normalize_words(body),
        description_key=normalize_words(description),
    )


def load_portable_names(root: Path) -> list[str]:
    manifest_path = root / "manifests" / "portable-files.toml"
    with manifest_path.open("rb") as handle:
        manifest = tomllib.load(handle)
    raw = manifest.get("agents", {}).get("skills")
    if not isinstance(raw, list) or any(not isinstance(item, str) or not item.strip() for item in raw):
        raise ValueError("portable manifest requires [agents].skills as a string array")
    return list(dict.fromkeys(item.strip() for item in raw))


def parse_root_argument(raw: str) -> tuple[str, Path]:
    if "=" in raw:
        label, value = raw.split("=", 1)
        if label.strip() and value.strip():
            return label.strip(), Path(value).expanduser()
    path = Path(raw).expanduser()
    return path.name or "external", path


def discover_root(root: Path, scope: str) -> list[Skill]:
    skills: list[Skill] = []
    if not root.is_dir():
        return skills
    for skill_file in sorted(root.glob("*/SKILL.md")):
        parsed = parse_frontmatter(skill_file)
        if parsed is None:
            continue
        skills.append(
            Skill(
                **{
                    **asdict(parsed),
                    "root": str(root.resolve()),
                    "scope": scope,
                }
            )
        )
    return skills


def find_prompt_string(value: Any) -> str | None:
    if isinstance(value, str):
        if "<skills_instructions>" in value and "### Available skills" in value:
            return value
        return None
    if isinstance(value, list):
        for item in value:
            found = find_prompt_string(item)
            if found:
                return found
        return None
    if isinstance(value, dict):
        for item in value.values():
            found = find_prompt_string(item)
            if found:
                return found
    return None


def parse_live_prompt(raw: str) -> tuple[list[Skill], dict[str, str]]:
    parsed = json.loads(raw)
    prompt = find_prompt_string(parsed)
    if prompt is None:
        raise ValueError("prompt input did not contain skills instructions")

    roots: dict[str, str] = {}
    skill_lines: list[str] = []
    section = ""
    for line in prompt.splitlines():
        if line == "### Skill roots":
            section = "roots"
            continue
        if line == "### Available skills":
            section = "skills"
            continue
        if line == "### How to use skills":
            section = ""
            continue
        if section == "roots":
            match = ROOT_LINE_RE.match(line)
            if match:
                roots[match.group(1)] = match.group(2)
        elif section == "skills" and line.startswith("- "):
            skill_lines.append(line)

    live: list[Skill] = []
    for order, line in enumerate(skill_lines):
        match = SKILL_LINE_RE.match(line)
        if not match:
            continue
        name, rendered_description, locator = match.groups()
        resolved = locator
        locator_match = re.match(r"^(r\d+)/(.*)$", locator)
        if locator_match and locator_match.group(1) in roots:
            resolved = str(Path(roots[locator_match.group(1)]) / locator_match.group(2))
        path = Path(os.path.expanduser(resolved))
        parsed_skill = parse_frontmatter(path) if path.is_file() else None
        description = parsed_skill.description if parsed_skill else (rendered_description or "").strip()
        body_key = parsed_skill.body_key if parsed_skill else ""
        description_key = normalize_words(description)
        live.append(
            Skill(
                name=name,
                description=description,
                file=str(path),
                real_file=str(path.resolve()) if path.exists() else str(path),
                root=str(path.parent.parent),
                scope="live",
                body_key=body_key,
                description_key=description_key,
                live=True,
                order=order,
                render_path=locator,
            )
        )
    if not live:
        raise ValueError("prompt input contained no parseable skills")
    return live, roots


def get_live_prompt(prompt_file: Path | None, no_live: bool) -> tuple[list[Skill] | None, str | None]:
    if no_live:
        return None, "disabled by --no-live"
    try:
        raw = (
            prompt_file.read_text(encoding="utf-8")
            if prompt_file
            else subprocess.run(
                ["codex", "debug", "prompt-input"],
                check=True,
                capture_output=True,
                text=True,
                timeout=45,
            ).stdout
        )
        live, _ = parse_live_prompt(raw)
        return live, None
    except (OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError) as error:
        return None, str(error)


def rendered_line(skill: Skill) -> str:
    locator = skill.render_path or skill.file
    return f"- {skill.name}: {skill.description} (file: {locator})\n"


def near_duplicates(skills: Sequence[Skill], threshold: float) -> list[DuplicatePair]:
    pairs: list[DuplicatePair] = []
    unique: dict[str, Skill] = {}
    for skill in skills:
        unique.setdefault(skill.real_file, skill)
    values = list(unique.values())
    for index, left in enumerate(values):
        for right in values[index + 1 :]:
            if left.name == right.name:
                continue
            desc = jaccard(left.description_key, right.description_key)
            body = jaccard(left.body_key, right.body_key) if left.body_key and right.body_key else 0.0
            if desc >= threshold and len(word_set(left.description_key) | word_set(right.description_key)) >= 4:
                pairs.append(DuplicatePair(left.name, right.name, "description", round(desc, 3)))
            elif body >= threshold and len(word_set(left.body_key) | word_set(right.body_key)) >= 12:
                pairs.append(DuplicatePair(left.name, right.name, "body", round(body, 3)))
    return sorted(pairs, key=lambda item: (-item.similarity, item.left, item.right))


def exact_collisions(skills: Sequence[Skill]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Skill]] = {}
    for skill in skills:
        grouped.setdefault(skill.name, {})[skill.real_file] = skill
    return [
        {
            "name": name,
            "sources": [
                {"scope": skill.scope, "file": skill.file, "real_file": skill.real_file}
                for skill in sorted(sources.values(), key=lambda item: (item.scope, item.file))
            ],
        }
        for name, sources in sorted(grouped.items())
        if len(sources) > 1
    ]


def iter_usage_files(paths: Iterable[Path], cutoff: float) -> Iterable[Path]:
    for path in paths:
        path = path.expanduser()
        if path.is_file():
            candidates = [path]
        elif path.is_dir():
            candidates = sorted(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file() and candidate.suffix.lower() in {".jsonl", ".log", ".txt"}
            )
        else:
            continue
        for candidate in candidates:
            try:
                stat = candidate.stat()
            except OSError:
                continue
            if stat.st_mtime < cutoff or candidate.name.lower() in SENSITIVE_LOG_NAMES:
                continue
            yield candidate


def scan_usage(
    paths: Sequence[Path],
    names: Sequence[str],
    usage_days: int,
    max_bytes: int,
) -> UsageSummary:
    hits = {name: 0 for name in names}
    scanned_files = 0
    scanned_bytes = 0
    truncated = False
    cutoff = time.time() - max(0, usage_days) * 24 * 60 * 60
    escaped = sorted((re.escape(name) for name in names), key=len, reverse=True)
    explicit_re = re.compile(r"\$(" + "|".join(escaped) + r")\b", re.IGNORECASE) if escaped else None
    path_re = re.compile(
        r"(?:^|[\\/])skills[\\/](" + "|".join(escaped) + r")[\\/]SKILL\.md\b",
        re.IGNORECASE,
    ) if escaped else None

    canonical = {name.lower(): name for name in names}
    for path in iter_usage_files(paths, cutoff):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if scanned_bytes + size > max_bytes:
            truncated = True
            break
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        scanned_files += 1
        scanned_bytes += size
        for regex in (explicit_re, path_re):
            if regex is None:
                continue
            for match in regex.finditer(text):
                name = canonical.get(match.group(1).lower())
                if name:
                    hits[name] += 1
    return UsageSummary(scanned_files, scanned_bytes, truncated, hits)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    portable_names = load_portable_names(root)
    canonical_root = root / "codex" / "skills"
    discovered = discover_root(canonical_root, "compass")
    for raw_root in args.skill_root:
        label, path = parse_root_argument(raw_root)
        discovered.extend(discover_root(path, label))

    live, live_error = get_live_prompt(args.live_prompt, args.no_live)
    canonical_by_name = {skill.name: skill for skill in discovered if skill.scope == "compass"}
    inventory = live if live is not None else [canonical_by_name[name] for name in portable_names if name in canonical_by_name]
    inventory_names = [skill.name for skill in inventory]
    line_bytes = [len(rendered_line(skill).encode("utf-8")) for skill in inventory]
    tokens = [math.ceil(value / args.chars_per_token) for value in line_bytes]
    budget_tokens = math.floor(args.context_tokens * args.budget_percent / 100)

    usage = scan_usage(
        args.usage_log,
        portable_names,
        args.usage_days,
        math.floor(args.max_usage_mb * 1024 * 1024),
    ) if args.usage_log else UsageSummary(0, 0, False, {name: 0 for name in portable_names})

    missing_manifest_skills = sorted(name for name in portable_names if name not in canonical_by_name)
    loaded_unowned = sorted(name for name in inventory_names if name not in portable_names)
    description_candidates = [
        {
            "name": skill.name,
            "chars": len(skill.description),
            "description": skill.description,
            "estimated_tokens": math.ceil(len(rendered_line(skill).encode("utf-8")) / args.chars_per_token),
        }
        for skill in inventory
        if len(skill.description) > args.description_candidate_chars
    ]
    description_candidates.sort(key=lambda item: (-item["chars"], item["name"]))
    unused_candidates = sorted(name for name, count in usage.hits.items() if count == 0) if args.usage_log else []

    report = {
        "schema_version": 1,
        "root": str(root),
        "inventory_mode": "live" if live is not None else "manifest-fallback",
        "live_error": live_error,
        "budget": {
            "context_tokens": args.context_tokens,
            "budget_percent": args.budget_percent,
            "budget_tokens": budget_tokens,
            "estimated_tokens": sum(tokens),
            "remaining_tokens": budget_tokens - sum(tokens),
            "used_ratio": round(sum(tokens) / budget_tokens, 4) if budget_tokens else None,
            "chars_per_token": args.chars_per_token,
            "included_skills": len(inventory),
        },
        "skills": [
            {
                "name": skill.name,
                "description": skill.description,
                "source": skill.file,
                "scope": skill.scope,
                "live": skill.live,
                "order": skill.order,
                "render_path": skill.render_path,
                "line_bytes": line_bytes[index],
                "estimated_tokens": tokens[index],
                "usage_hits": usage.hits.get(skill.name, 0),
            }
            for index, skill in enumerate(inventory)
        ],
        "usage": asdict(usage),
        "findings": {
            "missing_manifest_skills": missing_manifest_skills,
            "loaded_unowned": loaded_unowned,
            "exact_name_collisions": exact_collisions(discovered),
            "near_duplicates": [asdict(item) for item in near_duplicates(discovered, args.duplicate_threshold)],
            "description_candidates": description_candidates,
            "unused_candidates": unused_candidates,
        },
    }
    report["check_failed"] = bool(
        missing_manifest_skills
        or report["findings"]["exact_name_collisions"]
        or report["budget"]["remaining_tokens"] < 0
    )
    return report


def render_text(report: dict[str, Any], plain: bool) -> str:
    budget = report["budget"]
    findings = report["findings"]
    lines = [
        f"skill inventory: {report['inventory_mode']} ({budget['included_skills']} skills)",
        (
            "prompt budget: "
            f"{budget['estimated_tokens']}/{budget['budget_tokens']} estimated tokens "
            f"({budget['used_ratio']:.1%} used)"
        ),
        f"remaining budget: {budget['remaining_tokens']} tokens",
    ]
    if report.get("live_error"):
        lines.append(f"live inventory unavailable: {report['live_error']}")
    lines.extend(
        [
            f"missing manifest skills: {len(findings['missing_manifest_skills'])}",
            f"loaded unowned skills: {len(findings['loaded_unowned'])}",
            f"same-name collisions: {len(findings['exact_name_collisions'])}",
            f"near duplicates: {len(findings['near_duplicates'])}",
            f"description candidates: {len(findings['description_candidates'])}",
        ]
    )
    if report["usage"]["scanned_files"]:
        lines.append(
            "usage evidence: "
            f"{report['usage']['scanned_files']} files, {report['usage']['scanned_bytes']} bytes, "
            f"{len(findings['unused_candidates'])} no-hit candidates"
        )
    for collision in findings["exact_name_collisions"]:
        lines.append(f"collision={collision['name']} sources={','.join(item['file'] for item in collision['sources'])}")
    for item in findings["description_candidates"][:10]:
        lines.append(f"description={item['name']} chars={item['chars']} tokens={item['estimated_tokens']}")
    for pair in findings["near_duplicates"][:10]:
        lines.append(
            f"duplicate={pair['left']},{pair['right']} kind={pair['kind']} similarity={pair['similarity']:.3f}"
        )
    if findings["unused_candidates"]:
        lines.append("unused_candidates=" + ",".join(findings["unused_candidates"]))
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skill-root", action="append", default=[], metavar="[LABEL=]DIR")
    parser.add_argument("--live-prompt", type=Path)
    parser.add_argument("--no-live", action="store_true")
    parser.add_argument("--usage-log", action="append", type=Path, default=[])
    parser.add_argument("--usage-days", type=int, default=90)
    parser.add_argument("--max-usage-mb", type=float, default=64.0)
    parser.add_argument("--context-tokens", type=int, default=DEFAULT_CONTEXT_TOKENS)
    parser.add_argument("--budget-percent", type=float, default=DEFAULT_BUDGET_PERCENT)
    parser.add_argument("--chars-per-token", type=float, default=DEFAULT_CHARS_PER_TOKEN)
    parser.add_argument("--duplicate-threshold", type=float, default=DEFAULT_DUPLICATE_THRESHOLD)
    parser.add_argument(
        "--description-candidate-chars",
        type=int,
        default=DEFAULT_DESCRIPTION_CANDIDATE_CHARS,
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--plain", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.json and args.plain:
        parser.error("choose either --json or --plain")
    if args.context_tokens <= 0 or args.budget_percent <= 0 or args.chars_per_token <= 0:
        parser.error("context, budget percent, and chars per token must be positive")
    if not 0 < args.duplicate_threshold <= 1:
        parser.error("duplicate threshold must be within (0, 1]")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(args)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
        print(f"skill audit failed: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report, args.plain))
    return 1 if args.check and report["check_failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
