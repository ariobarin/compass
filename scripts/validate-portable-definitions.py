#!/usr/bin/env python3
"""Validate the identity and syntax of manifest-selected definitions."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    print("portable definition validation requires Python 3.11 or newer", file=sys.stderr)
    raise SystemExit(2)


def selected(manifest: dict[str, Any], section: str, key: str) -> list[str]:
    table = manifest.get(section)
    if not isinstance(table, dict):
        raise ValueError(f"manifest {section} must be an object")
    value = table.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"manifest {section}.{key} must be a string array")
    return value


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("frontmatter must start on the first line")
    try:
        closing = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("frontmatter is missing its closing delimiter") from error

    values: dict[str, str] = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not separator or not key or not value:
            raise ValueError(f"frontmatter entry is not a non-empty scalar: {line!r}")
        if key in values:
            raise ValueError(f"frontmatter field is duplicated: {key}")
        if value[:1] in {'"', "'"}:
            if len(value) < 2 or value[-1] != value[0]:
                raise ValueError(f"frontmatter scalar has an unmatched quote: {key}")
            value = value[1:-1].strip()
        values[key] = value
    return values


def validate_markdown(path: Path, expected_name: str, kind: str) -> list[str]:
    try:
        values = frontmatter(path)
    except (OSError, UnicodeError, ValueError) as error:
        return [f"{kind} {expected_name}: {error}"]

    errors = []
    if values.get("name") != expected_name:
        errors.append(f"{kind} {expected_name}: name must match its manifest entry")
    if not values.get("description"):
        errors.append(f"{kind} {expected_name}: description must be a non-empty scalar")
    return errors


def validate_agent(path: Path, expected_name: str) -> list[str]:
    try:
        with path.open("rb") as handle:
            values = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        return [f"Codex agent {expected_name}: invalid TOML: {error}"]

    errors = []
    for field in ("name", "description", "developer_instructions"):
        if not isinstance(values.get(field), str) or not values[field].strip():
            errors.append(f"Codex agent {expected_name}: {field} must be a non-empty string")
    if isinstance(values.get("name"), str) and values["name"] != expected_name:
        errors.append(f"Codex agent {expected_name}: name must match its manifest entry")
    return errors


def validate(root: Path) -> list[str]:
    manifest_path = root / "manifests" / "portable-files.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if not isinstance(manifest, dict):
            raise ValueError("root must be an object")
        codex_agents = selected(manifest, "codex", "agents")
        shared_skills = selected(manifest, "agents", "skills")
        claude_skills = selected(manifest, "claude", "skills")
        claude_agents = selected(manifest, "claude", "agents")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return [f"portable manifest: {error}"]

    errors = []
    for name in codex_agents:
        errors.extend(validate_agent(root / "codex" / "agents" / f"{name}.toml", name))
    for name in shared_skills:
        path = root / "codex" / "skills" / name / "SKILL.md"
        errors.extend(validate_markdown(path, name, "shared skill"))
    for name in claude_skills:
        path = root / "claude" / "skills" / name / "SKILL.md"
        errors.extend(validate_markdown(path, name, "Claude skill"))
    for name in claude_agents:
        path = root / "claude" / "agents" / f"{name}.md"
        errors.extend(validate_markdown(path, name, "Claude agent"))
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate-portable-definitions.py REPO_ROOT", file=sys.stderr)
        return 2

    errors = validate(Path(sys.argv[1]).resolve())
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("portable definitions: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
