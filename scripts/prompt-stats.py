#!/usr/bin/env python3
"""Report deterministic statistics for repository-owned prompt surfaces."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

DEFAULT_CHARS_PER_TOKEN = 4.0
DEFAULT_DUPLICATE_THRESHOLD = 0.9
DEFAULT_DUPLICATE_MIN_WORDS = 8
DEFAULT_DUPLICATE_MAX_RESULTS = 50
DEFAULT_GLOBAL_BUDGET = 4_000
DEFAULT_AGENT_TOTAL_BUDGET = 12_000
DEFAULT_AGENT_FILE_BUDGET = 2_500
DEFAULT_SKILL_ROUTING_BUDGET = 2_000
DEFAULT_SELECTED_SKILL_BUDGET = 4_000
PROMPT_TEXT_SUFFIXES = {".json", ".md", ".toml", ".txt", ".yaml", ".yml"}
TERM_PATTERNS = {
    "must": re.compile(r"\bmust\b", re.IGNORECASE),
    "always": re.compile(r"\balways\b", re.IGNORECASE),
    "never": re.compile(r"\bnever\b", re.IGNORECASE),
    "required": re.compile(r"\brequired\b", re.IGNORECASE),
    "spawn": re.compile(r"\bspawn(?:s|ed|ing)?\b", re.IGNORECASE),
    "launch": re.compile(r"\blaunch(?:es|ed|ing)?\b", re.IGNORECASE),
    "dispatch": re.compile(r"\bdispatch(?:es|ed|ing)?\b", re.IGNORECASE),
    "review": re.compile(r"\breview(?:s|ed|ing|er|ers)?\b", re.IGNORECASE),
    "verify": re.compile(r"\bverif(?:y|ies|ied|ying|ication|ications|ier|iers)\b", re.IGNORECASE),
}
NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+", re.MULTILINE)
FRONTMATTER_FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
MARKDOWN_PREFIX_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|#{1,6}\s+|>\s*)+")
WORD_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Clause:
    text: str
    normalized: str
    numbered: bool


@dataclass(frozen=True)
class SurfaceSource:
    path: Path
    category: str
    activation: str
    prompt_text: str
    name: str | None = None
    model: str | None = None
    reasoning_effort: str | None = None
    skill_name: str | None = None
    routing_description: str | None = None


def normalize_words(text: str) -> str:
    return " ".join(WORD_RE.findall(text.lower()))


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


def parse_frontmatter_text(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    closing = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), -1)
    if closing < 0:
        return {}, text

    fields: dict[str, str] = {}
    index = 1
    while index < closing:
        match = FRONTMATTER_FIELD_RE.match(lines[index])
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
    return fields, "\n".join(lines[closing + 1 :])


def require_repo_path(root: Path, path: Path) -> Path:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"prompt path escapes repository: {path.name}") from error
    return path


def load_portable_skill_names(root: Path) -> list[str]:
    manifest_path = require_repo_path(root, root / "manifests" / "portable-files.toml")
    with manifest_path.open("rb") as handle:
        manifest = tomllib.load(handle)
    raw = manifest.get("agents", {}).get("skills")
    if not isinstance(raw, list) or any(not isinstance(item, str) or not item.strip() for item in raw):
        raise ValueError("portable manifest requires [agents].skills as a string array")
    names = list(dict.fromkeys(item.strip() for item in raw))
    if any(Path(name).name != name or name in {".", ".."} or "\\" in name for name in names):
        raise ValueError("portable skill names must be single path components")
    return names


def read_text(root: Path, path: Path) -> str:
    return require_repo_path(root, path).read_text(encoding="utf-8")


def relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def parse_agent(root: Path, path: Path) -> SurfaceSource:
    raw = read_text(root, path)
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    name = data.get("name") if isinstance(data.get("name"), str) else path.stem
    description = data.get("description") if isinstance(data.get("description"), str) else ""
    instructions = data.get("developer_instructions") if isinstance(data.get("developer_instructions"), str) else ""
    model = data.get("model") if isinstance(data.get("model"), str) else None
    effort = data.get("model_reasoning_effort") if isinstance(data.get("model_reasoning_effort"), str) else None
    prompt_text = "\n".join(part for part in (description, instructions) if part)
    return SurfaceSource(
        path=path,
        category="agent",
        activation="routed",
        prompt_text=prompt_text or raw,
        name=name,
        model=model,
        reasoning_effort=effort,
        routing_description=description or None,
    )


def parse_config(root: Path, path: Path) -> SurfaceSource:
    raw = read_text(root, path)
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    model = data.get("model") if isinstance(data.get("model"), str) else None
    effort = data.get("model_reasoning_effort") if isinstance(data.get("model_reasoning_effort"), str) else None
    return SurfaceSource(
        path=path,
        category="config",
        activation="manually_selected",
        prompt_text=raw,
        name=path.stem,
        model=model,
        reasoning_effort=effort,
    )


def discover_skill_files(root: Path, skill_name: str) -> list[SurfaceSource]:
    skill_root = root / "codex" / "skills" / skill_name
    skill_file = skill_root / "SKILL.md"
    if not skill_file.is_file():
        raise ValueError(f"manifest skill is missing SKILL.md: {skill_name}")

    raw = read_text(root, skill_file)
    fields, body = parse_frontmatter_text(raw)
    name = fields.get("name", skill_name).strip() or skill_name
    description = re.sub(r"\s+", " ", fields.get("description", "")).strip()
    prompt_text = "\n".join(part for part in (description, body) if part)
    surfaces = [
        SurfaceSource(
            path=skill_file,
            category="skill",
            activation="routed",
            prompt_text=prompt_text,
            name=name,
            skill_name=skill_name,
            routing_description=description or None,
        )
    ]

    for folder_name, category in (("references", "reference"), ("templates", "template"), ("assets", "template")):
        folder = skill_root / folder_name
        if not folder.is_dir():
            continue
        for path in sorted(candidate for candidate in folder.rglob("*") if candidate.is_file()):
            if path.suffix.lower() not in PROMPT_TEXT_SUFFIXES:
                continue
            surfaces.append(
                SurfaceSource(
                    path=path,
                    category=category,
                    activation="manually_selected",
                    prompt_text=read_text(root, path),
                    skill_name=skill_name,
                )
            )
    return surfaces


def discover_surfaces(root: Path) -> list[SurfaceSource]:
    surfaces: list[SurfaceSource] = []
    for path in (root / "AGENTS.md", root / "codex" / "AGENTS.md"):
        if path.is_file():
            surfaces.append(
                SurfaceSource(
                    path=path,
                    category="global",
                    activation="always_loaded",
                    prompt_text=read_text(root, path),
                    name=path.name,
                )
            )

    agents_root = root / "codex" / "agents"
    if agents_root.is_dir():
        surfaces.extend(parse_agent(root, path) for path in sorted(agents_root.glob("*.toml")))

    config_path = root / "codex" / "config.review.toml"
    if config_path.is_file():
        surfaces.append(parse_config(root, config_path))

    for skill_name in load_portable_skill_names(root):
        surfaces.extend(discover_skill_files(root, skill_name))

    return sorted(surfaces, key=lambda item: relative_path(root, item.path))


def clauses_from_text(text: str) -> list[Clause]:
    clauses: list[Clause] = []
    seen: set[str] = set()
    buffer: list[str] = []

    def flush_buffer() -> None:
        if not buffer:
            return
        paragraph = " ".join(part.strip() for part in buffer if part.strip()).strip()
        buffer.clear()
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
            add_clause(sentence, False)

    def add_clause(raw: str, numbered: bool) -> None:
        cleaned = MARKDOWN_PREFIX_RE.sub("", raw).strip().strip("`*")
        normalized = normalize_words(cleaned)
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        clauses.append(Clause(cleaned, normalized, numbered))

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_buffer()
            continue
        if stripped.startswith("#"):
            flush_buffer()
            continue
        if re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|>\s+)", line):
            flush_buffer()
            add_clause(line, bool(NUMBERED_RE.match(line)))
            continue
        buffer.append(stripped)
    flush_buffer()
    return clauses


def steering_counts(text: str) -> dict[str, Any]:
    counts = {name: len(pattern.findall(text)) for name, pattern in TERM_PATTERNS.items()}
    counts["numbered"] = len(NUMBERED_RE.findall(text))
    clauses = clauses_from_text(text)
    strong_clauses = 0
    for clause in clauses:
        if clause.numbered or any(pattern.search(clause.text) for pattern in TERM_PATTERNS.values()):
            strong_clauses += 1
    return {
        "clauses": strong_clauses,
        "terms": {name: counts[name] for name in sorted(counts)},
        "total_matches": sum(counts.values()),
    }


def estimate_tokens(characters: int, chars_per_token: float) -> int:
    return math.ceil(characters / chars_per_token) if characters else 0


def surface_record(root: Path, source: SurfaceSource, chars_per_token: float) -> dict[str, Any]:
    raw = read_text(root, source.path)
    encoded = raw.encode("utf-8")
    record: dict[str, Any] = {
        "path": relative_path(root, source.path),
        "category": source.category,
        "activation": source.activation,
        "bytes": len(encoded),
        "characters": len(raw),
        "estimated_tokens": estimate_tokens(len(raw), chars_per_token),
        "strong_steering": steering_counts(source.prompt_text),
    }
    if source.name is not None:
        record["name"] = source.name
    if source.model is not None:
        record["model"] = source.model
    if source.reasoning_effort is not None:
        record["reasoning_effort"] = source.reasoning_effort
    if source.skill_name is not None:
        record["skill"] = source.skill_name
    return record


def short_label(normalized: str, max_words: int = 14, max_chars: int = 96) -> str:
    words = normalized.split()[:max_words]
    return " ".join(words)[:max_chars].rstrip()


def duplicate_pairs(
    root: Path,
    sources: Sequence[SurfaceSource],
    threshold: float,
    min_words: int,
    max_results: int,
) -> tuple[int, list[dict[str, Any]]]:
    clause_inventory: list[tuple[str, Clause]] = []
    for source in sources:
        path = relative_path(root, source.path)
        for clause in clauses_from_text(source.prompt_text):
            word_count = len(clause.normalized.split())
            if min_words <= word_count <= 80:
                clause_inventory.append((path, clause))

    matches: list[dict[str, Any]] = []
    total = 0
    for index, (left_path, left_clause) in enumerate(clause_inventory):
        left_words = word_set(left_clause.normalized)
        for right_path, right_clause in clause_inventory[index + 1 :]:
            if left_path == right_path:
                continue
            right_words = word_set(right_clause.normalized)
            if abs(len(left_words) - len(right_words)) > max(len(left_words), len(right_words)) * 0.35:
                continue
            similarity = jaccard(left_clause.normalized, right_clause.normalized)
            if similarity < threshold:
                continue
            total += 1
            matches.append(
                {
                    "left": left_path,
                    "right": right_path,
                    "similarity": round(similarity, 3),
                    "label": short_label(min(left_clause.normalized, right_clause.normalized)),
                }
            )

    matches.sort(key=lambda item: (-item["similarity"], item["left"], item["right"], item["label"]))
    return total, matches[:max_results]


def skill_routing_tokens(root: Path, sources: Iterable[SurfaceSource], chars_per_token: float) -> int:
    total_characters = 0
    for source in sources:
        if source.category != "skill":
            continue
        description = source.routing_description or ""
        locator = relative_path(root, source.path)
        total_characters += len(f"- {source.name}: {description} (file: {locator})\n")
    return estimate_tokens(total_characters, chars_per_token)


def budget_report(
    root: Path,
    sources: Sequence[SurfaceSource],
    surfaces: Sequence[dict[str, Any]],
    args: argparse.Namespace,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    warnings: list[dict[str, Any]] = []
    global_tokens = sum(surface["estimated_tokens"] for surface in surfaces if surface["category"] == "global")
    agent_surfaces = [surface for surface in surfaces if surface["category"] == "agent"]
    agent_tokens = sum(surface["estimated_tokens"] for surface in agent_surfaces)
    routing_tokens = skill_routing_tokens(root, sources, args.chars_per_token)

    skill_payloads: dict[str, int] = {}
    for surface in surfaces:
        skill_name = surface.get("skill")
        if skill_name:
            skill_payloads[skill_name] = skill_payloads.get(skill_name, 0) + surface["estimated_tokens"]
    selected_skill = max(skill_payloads, key=lambda name: (skill_payloads[name], name)) if skill_payloads else None
    selected_skill_tokens = skill_payloads.get(selected_skill, 0) if selected_skill else 0

    def warn(name: str, actual: int, limit: int, path: str | None = None) -> None:
        if actual <= limit:
            return
        item: dict[str, Any] = {"budget": name, "actual": actual, "limit": limit, "over": actual - limit}
        if path is not None:
            item["path"] = path
        warnings.append(item)

    warn("global_prompt", global_tokens, args.global_budget)
    warn("agent_prompts_aggregate", agent_tokens, args.agent_total_budget)
    for surface in agent_surfaces:
        warn("agent_prompt_individual", surface["estimated_tokens"], args.agent_file_budget, surface["path"])
    warn("skill_routing", routing_tokens, args.skill_routing_budget)
    warn(
        "selected_skill_payload",
        selected_skill_tokens,
        args.selected_skill_budget,
        f"codex/skills/{selected_skill}" if selected_skill else None,
    )
    warnings.sort(key=lambda item: (item["budget"], item.get("path", ""), item["actual"]))

    budgets = {
        "global_prompt": {
            "actual": global_tokens,
            "limit": args.global_budget,
            "exceeded": global_tokens > args.global_budget,
        },
        "agent_prompts_aggregate": {
            "actual": agent_tokens,
            "limit": args.agent_total_budget,
            "exceeded": agent_tokens > args.agent_total_budget,
        },
        "agent_prompt_individual": {
            "limit": args.agent_file_budget,
            "exceeded_files": [
                surface["path"] for surface in agent_surfaces if surface["estimated_tokens"] > args.agent_file_budget
            ],
        },
        "skill_routing": {
            "actual": routing_tokens,
            "limit": args.skill_routing_budget,
            "exceeded": routing_tokens > args.skill_routing_budget,
        },
        "selected_skill_payload": {
            "actual": selected_skill_tokens,
            "limit": args.selected_skill_budget,
            "skill": selected_skill,
            "exceeded": selected_skill_tokens > args.selected_skill_budget,
        },
    }
    return budgets, warnings


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    sources = discover_surfaces(root)
    surfaces = [surface_record(root, source, args.chars_per_token) for source in sources]
    duplicate_count, duplicates = duplicate_pairs(
        root,
        sources,
        args.duplicate_threshold,
        args.duplicate_min_words,
        args.max_duplicate_results,
    )
    budgets, budget_warnings = budget_report(root, sources, surfaces, args)

    routing = [
        {
            "name": source.name,
            "path": relative_path(root, source.path),
            "model": source.model,
            "reasoning_effort": source.reasoning_effort,
        }
        for source in sources
        if source.category == "agent"
    ]
    routing.sort(key=lambda item: (item["name"] or "", item["path"]))

    hotspots = [
        {
            "path": surface["path"],
            "clauses": surface["strong_steering"]["clauses"],
            "total_matches": surface["strong_steering"]["total_matches"],
            "terms": surface["strong_steering"]["terms"],
        }
        for surface in surfaces
        if surface["strong_steering"]["clauses"]
    ]
    hotspots.sort(key=lambda item: (-item["clauses"], -item["total_matches"], item["path"]))

    report = {
        "schema_version": 1,
        "estimator": {
            "kind": "character_ratio",
            "chars_per_token": args.chars_per_token,
            "note": "Token counts are deterministic estimates from Unicode characters.",
        },
        "summary": {
            "files": len(surfaces),
            "estimated_tokens": sum(surface["estimated_tokens"] for surface in surfaces),
            "strong_steering_clauses": sum(
                surface["strong_steering"]["clauses"] for surface in surfaces
            ),
            "duplicate_pairs": duplicate_count,
        },
        "surfaces": surfaces,
        "routing": routing,
        "budgets": budgets,
        "findings": {
            "steering_hotspots": hotspots,
            "duplicate_pairs": duplicates,
            "duplicate_pairs_truncated": duplicate_count > len(duplicates),
            "budget_warnings": budget_warnings,
        },
        "check_failed": bool(budget_warnings),
    }
    return report


def render_text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    estimator = report["estimator"]
    warnings = report["findings"]["budget_warnings"]
    lines = [
        "static prompt statistics",
        f"files: {summary['files']}",
        (
            f"estimated tokens: {summary['estimated_tokens']} "
            f"({estimator['chars_per_token']:g} characters per token)"
        ),
        f"strong steering clauses: {summary['strong_steering_clauses']}",
        f"duplicate pairs: {summary['duplicate_pairs']}",
        f"budget warnings: {len(warnings)}",
        "",
        "surfaces",
        "tokens steering category activation path",
    ]
    for surface in sorted(
        report["surfaces"], key=lambda item: (-item["estimated_tokens"], item["path"])
    ):
        lines.append(
            f"{surface['estimated_tokens']:>6} "
            f"{surface['strong_steering']['clauses']:>8} "
            f"{surface['category']:<9} "
            f"{surface['activation']:<17} "
            f"{surface['path']}"
        )

    hotspots = report["findings"]["steering_hotspots"]
    if hotspots:
        lines.extend(["", "steering hotspots", "clauses matches path"])
        for item in hotspots[:10]:
            lines.append(f"{item['clauses']:>7} {item['total_matches']:>7} {item['path']}")

    lines.extend(["", "agent routing", "name model reasoning path"])
    for item in report["routing"]:
        lines.append(
            f"{item['name']} {item['model'] or '-'} {item['reasoning_effort'] or '-'} {item['path']}"
        )

    if warnings:
        lines.extend(["", "budget warnings"])
        for warning in warnings:
            path = f" path={warning['path']}" if warning.get("path") else ""
            lines.append(
                f"{warning['budget']}: {warning['actual']}/{warning['limit']} tokens{path}"
            )

    duplicates = report["findings"]["duplicate_pairs"]
    if duplicates:
        lines.extend(["", "duplicate findings"])
        for item in duplicates[:10]:
            lines.append(
                f"{item['similarity']:.3f} {item['left']} <> {item['right']} label={item['label']}"
            )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--chars-per-token", type=float, default=DEFAULT_CHARS_PER_TOKEN)
    parser.add_argument("--duplicate-threshold", type=float, default=DEFAULT_DUPLICATE_THRESHOLD)
    parser.add_argument("--duplicate-min-words", type=int, default=DEFAULT_DUPLICATE_MIN_WORDS)
    parser.add_argument("--max-duplicate-results", type=int, default=DEFAULT_DUPLICATE_MAX_RESULTS)
    parser.add_argument("--global-budget", type=int, default=DEFAULT_GLOBAL_BUDGET)
    parser.add_argument("--agent-total-budget", type=int, default=DEFAULT_AGENT_TOTAL_BUDGET)
    parser.add_argument("--agent-file-budget", type=int, default=DEFAULT_AGENT_FILE_BUDGET)
    parser.add_argument("--skill-routing-budget", type=int, default=DEFAULT_SKILL_ROUTING_BUDGET)
    parser.add_argument("--selected-skill-budget", type=int, default=DEFAULT_SELECTED_SKILL_BUDGET)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.chars_per_token <= 0:
        parser.error("chars per token must be positive")
    if not 0 < args.duplicate_threshold <= 1:
        parser.error("duplicate threshold must be within (0, 1]")
    if args.duplicate_min_words <= 0 or args.max_duplicate_results < 0:
        parser.error("duplicate limits must be nonnegative and minimum words must be positive")
    budgets = (
        args.global_budget,
        args.agent_total_budget,
        args.agent_file_budget,
        args.skill_routing_budget,
        args.selected_skill_budget,
    )
    if any(value <= 0 for value in budgets):
        parser.error("budgets must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(args)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
        print(f"prompt stats failed: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 1 if args.check and report["check_failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
