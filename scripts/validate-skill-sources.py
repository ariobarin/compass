#!/usr/bin/env python3
"""Validate canonical skill ownership and installation provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any, Sequence

ALLOWED_RECORD_FIELDS = {"name", "owner", "source", "profile", "targets", "upstream"}
ALLOWED_TARGET_FIELDS = {"codex", "claude"}
ALLOWED_CODEX_MODES = {"copy"}
ALLOWED_CLAUDE_MODES = {"none", "direct", "derived"}
PROFILE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"missing skill source manifest: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid skill source manifest at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error
    if not isinstance(value, dict):
        raise ValueError("skill source manifest must be a JSON object")
    return value


def load_portable_manifest(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            value = tomllib.load(handle)
    except FileNotFoundError as error:
        raise ValueError(f"missing portable manifest: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"invalid portable manifest: {error}") from error
    if not isinstance(value, dict):
        raise ValueError("portable manifest must be a TOML table")
    return value


def string_array(value: object, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{label} must be a string array")
    return [item.strip() for item in value]


def portable_sets(manifest: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    agents = manifest.get("agents")
    claude = manifest.get("claude")
    if not isinstance(agents, dict) or not isinstance(claude, dict):
        raise ValueError("portable manifest requires [agents] and [claude] tables")
    installed = set(string_array(agents.get("skills"), "[agents].skills"))
    direct = set(string_array(claude.get("skills"), "[claude].skills"))
    derived = set(string_array(claude.get("derived_skills"), "[claude].derived_skills"))
    if direct & derived:
        overlap = ", ".join(sorted(direct & derived))
        raise ValueError(f"Claude skills cannot be both direct and derived: {overlap}")
    return installed, direct, derived


def safe_source(root: Path, raw: object) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("source must be a non-empty repository-relative path")
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"source must stay under the repository root: {raw}")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"source escapes the repository root: {raw}") from error
    return resolved


def skill_frontmatter_name(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^name:\s*(.*?)\s*$", line)
        if match:
            value = match.group(1).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            return value.strip() or None
    return None


def validate_upstream(record_name: str, value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, dict):
        return [f"skill {record_name}: upstream must be an object"]
    unknown = sorted(set(value) - {"repository", "reviewed_ref", "source_sha256"})
    problems = [f"skill {record_name}: unsupported upstream fields: {', '.join(unknown)}"] if unknown else []
    repository = value.get("repository")
    reviewed_ref = value.get("reviewed_ref")
    source_sha256 = value.get("source_sha256")
    if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
        problems.append(f"skill {record_name}: upstream.repository must use owner/name")
    if not isinstance(reviewed_ref, str) or not reviewed_ref.strip():
        problems.append(f"skill {record_name}: upstream.reviewed_ref must be a non-empty string")
    if not isinstance(source_sha256, str) or not SHA256_RE.fullmatch(source_sha256):
        problems.append(f"skill {record_name}: upstream.source_sha256 must be 64 lowercase hex characters")
    return problems


def source_tree_sha256(path: Path) -> str:
    """Hash a source directory deterministically for reviewed external snapshots."""
    digest = hashlib.sha256()
    files = sorted(
        (
            candidate.relative_to(path).as_posix(),
            candidate,
        )
        for candidate in path.rglob("*")
        if candidate.is_file()
    )
    for relative_path, file in files:
        relative = relative_path.encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content = file.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def validate(root: Path, source_manifest_path: Path, portable_manifest_path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    source_manifest = load_json(source_manifest_path)
    portable_manifest = load_portable_manifest(portable_manifest_path)
    installed, direct, derived = portable_sets(portable_manifest)
    problems: list[str] = []

    if source_manifest.get("schema_version") != 1:
        problems.append("skill source manifest requires schema_version 1")
    unknown_top = sorted(set(source_manifest) - {"schema_version", "skills"})
    if unknown_top:
        problems.append(f"skill source manifest has unsupported fields: {', '.join(unknown_top)}")
    raw_records = source_manifest.get("skills")
    if not isinstance(raw_records, list) or not raw_records:
        problems.append("skill source manifest requires a non-empty skills array")
        return problems, []

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_records, start=1):
        if not isinstance(raw, dict):
            problems.append(f"skill source record {index} must be an object")
            continue
        name = raw.get("name")
        record_label = name if isinstance(name, str) and name.strip() else str(index)
        unknown = sorted(set(raw) - ALLOWED_RECORD_FIELDS)
        if unknown:
            problems.append(f"skill {record_label}: unsupported fields: {', '.join(unknown)}")
        if not isinstance(name, str) or not name.strip():
            problems.append(f"skill source record {index}: name must be a non-empty string")
            continue
        name = name.strip()
        if name in seen:
            problems.append(f"skill {name}: duplicate source record")
            continue
        seen.add(name)

        owner = raw.get("owner")
        if not isinstance(owner, str) or not owner.strip():
            problems.append(f"skill {name}: owner must be a non-empty string")
            owner = ""
        else:
            owner = owner.strip()

        profile = raw.get("profile")
        if not isinstance(profile, str) or not PROFILE_RE.fullmatch(profile):
            problems.append(f"skill {name}: profile must be a lowercase slug")
            profile = ""

        try:
            source = safe_source(root, raw.get("source"))
            relative_source = source.relative_to(root).as_posix()
        except ValueError as error:
            problems.append(f"skill {name}: {error}")
            source = root
            relative_source = str(raw.get("source", ""))

        skill_file = source / "SKILL.md"
        if source != root:
            if not source.is_dir():
                problems.append(f"skill {name}: source directory is missing: {relative_source}")
            elif not skill_file.is_file():
                problems.append(f"skill {name}: source lacks SKILL.md: {relative_source}")
            else:
                declared_name = skill_frontmatter_name(skill_file)
                if declared_name != name:
                    problems.append(
                        f"skill {name}: SKILL.md name is {declared_name!r} in {relative_source}"
                    )
                if source.name != name:
                    problems.append(f"skill {name}: source directory name must match skill name")

        targets = raw.get("targets")
        codex_mode = None
        claude_mode = None
        if not isinstance(targets, dict):
            problems.append(f"skill {name}: targets must be an object")
        else:
            unknown_targets = sorted(set(targets) - ALLOWED_TARGET_FIELDS)
            if unknown_targets:
                problems.append(f"skill {name}: unsupported target fields: {', '.join(unknown_targets)}")
            codex_mode = targets.get("codex")
            claude_mode = targets.get("claude")
            if codex_mode not in ALLOWED_CODEX_MODES:
                problems.append(f"skill {name}: targets.codex must be copy")
            if claude_mode not in ALLOWED_CLAUDE_MODES:
                problems.append(f"skill {name}: targets.claude must be none, direct, or derived")

        expected_claude = "derived" if name in derived else "direct" if name in direct else "none"
        if codex_mode != "copy":
            pass
        elif name not in installed:
            problems.append(f"skill {name}: source record is not listed in [agents].skills")
        if claude_mode in ALLOWED_CLAUDE_MODES and claude_mode != expected_claude:
            problems.append(
                f"skill {name}: targets.claude is {claude_mode}, expected {expected_claude} from portable manifest"
            )

        upstream = raw.get("upstream")
        problems.extend(validate_upstream(name, upstream))
        if owner != "compass" and upstream is None:
            problems.append(f"skill {name}: non-Compass ownership requires reviewed upstream provenance")
        if (
            isinstance(upstream, dict)
            and isinstance(upstream.get("source_sha256"), str)
            and SHA256_RE.fullmatch(upstream["source_sha256"])
            and source.is_dir()
        ):
            actual_hash = source_tree_sha256(source)
            if actual_hash != upstream["source_sha256"]:
                problems.append(
                    f"skill {name}: upstream.source_sha256 does not match {relative_source}"
                )
        normalized.append(
            {
                "name": name,
                "owner": owner,
                "source": relative_source,
                "profile": profile,
                "targets": {"codex": codex_mode, "claude": claude_mode},
                **({"upstream": upstream} if upstream is not None else {}),
            }
        )

    missing = sorted(installed - seen)
    extra = sorted(seen - installed)
    if missing:
        problems.append(f"portable skills missing source records: {', '.join(missing)}")
    if extra:
        problems.append(f"source records not installed by portable manifest: {', '.join(extra)}")
    return problems, sorted(normalized, key=lambda item: item["name"])


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--portable-manifest", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--hash-source", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    if args.hash_source:
        source = args.hash_source.expanduser().resolve()
        try:
            source.relative_to(root)
        except ValueError:
            print("hash source must stay under the repository root", file=sys.stderr)
            return 2
        if not source.is_dir():
            print(f"hash source is not a directory: {source}", file=sys.stderr)
            return 2
        print(source_tree_sha256(source))
        return 0

    source_manifest_path = (args.manifest or root / "manifests" / "skill-sources.json").resolve()
    portable_manifest_path = (
        args.portable_manifest or root / "manifests" / "portable-files.toml"
    ).resolve()
    try:
        problems, records = validate(root, source_manifest_path, portable_manifest_path)
    except ValueError as error:
        problems = [str(error)]
        records = []

    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "valid": not problems,
                    "problems": problems,
                    "skills": records,
                },
                indent=2,
                sort_keys=True,
            )
        )
    elif problems:
        for problem in problems:
            print(problem, file=sys.stderr)
    else:
        print(f"validated {len(records)} skill source record(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
