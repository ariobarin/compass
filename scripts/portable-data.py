#!/usr/bin/env python3
"""Parse and validate Compass TOML with the Python standard library."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

MANIFEST_SECTIONS = (
    "codex",
    "agents",
    "claude",
    "config",
    "repo_only",
    "local_only",
)
MANIFEST_ARRAYS = {
    "codex": ("files", "dirs"),
    "agents": ("skills",),
    "claude": ("derived_skills", "agents", "derived_agents"),
    "repo_only": ("files", "dirs"),
    "local_only": ("files", "dirs", "patterns"),
}
MANIFEST_STRINGS = {
    "codex": ("home",),
    "agents": ("home", "skills_dir"),
    "claude": ("home", "skills_dir", "agents_dir"),
    "config": ("review_file", "reason"),
    "repo_only": ("reason",),
}
MANIFEST_BOOLEANS = {"config": ("install_automatically",)}
AGENT_STRING_FIELDS = ("name", "description", "developer_instructions")


def read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except FileNotFoundError as error:
        raise ValueError(f"missing TOML file: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"invalid TOML in {path}: {error}") from error

    if not isinstance(data, dict):
        raise ValueError(f"TOML root must be a table: {path}")
    return data


def parse_stdin() -> dict[str, Any]:
    text = sys.stdin.buffer.read().decode("utf-8-sig")
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"invalid TOML from stdin: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("TOML root from stdin must be a table")
    return data


def require_string_array(
    table: dict[str, Any], section: str, key: str
) -> list[str]:
    if key not in table:
        raise ValueError(f"manifest [{section}] requires {key}")
    value = table[key]
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"manifest [{section}].{key} must be a string array")
    if len(value) != len(set(value)):
        raise ValueError(f"manifest [{section}].{key} contains duplicates")
    return value


def require_string(table: dict[str, Any], section: str, key: str) -> str:
    if key not in table:
        raise ValueError(f"manifest [{section}] requires {key}")
    value = table[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"manifest [{section}].{key} must be a non-empty string")
    return value


def require_boolean(table: dict[str, Any], section: str, key: str) -> bool:
    if key not in table:
        raise ValueError(f"manifest [{section}] requires {key}")
    value = table[key]
    if not isinstance(value, bool):
        raise ValueError(f"manifest [{section}].{key} must be a boolean")
    return value


def validate_manifest(manifest: dict[str, Any]) -> None:
    unknown_sections = sorted(set(manifest) - set(MANIFEST_SECTIONS))
    if unknown_sections:
        raise ValueError(
            "manifest contains unsupported sections: " + ", ".join(unknown_sections)
        )

    for section in MANIFEST_SECTIONS:
        table = manifest.get(section)
        if not isinstance(table, dict):
            raise ValueError(f"manifest requires [{section}] table")

        allowed_keys = set(MANIFEST_ARRAYS.get(section, ()))
        allowed_keys.update(MANIFEST_STRINGS.get(section, ()))
        allowed_keys.update(MANIFEST_BOOLEANS.get(section, ()))
        unknown_keys = sorted(set(table) - allowed_keys)
        if unknown_keys:
            raise ValueError(
                f"manifest [{section}] contains unsupported keys: "
                + ", ".join(unknown_keys)
            )

        for key in MANIFEST_ARRAYS.get(section, ()):
            require_string_array(table, section, key)
        for key in MANIFEST_STRINGS.get(section, ()):
            require_string(table, section, key)
        for key in MANIFEST_BOOLEANS.get(section, ()):
            require_boolean(table, section, key)


def validate_agent(path: Path, data: dict[str, Any]) -> None:
    for field in AGENT_STRING_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"agent {path.name} requires non-empty {field}")
    if data["name"] != path.stem:
        raise ValueError(
            f"agent name {data['name']!r} must match filename {path.stem!r}"
        )


def load_repository(root: Path) -> dict[str, Any]:
    manifest = read_toml(root / "manifests" / "portable-files.toml")
    validate_manifest(manifest)

    agents: dict[str, dict[str, Any]] = {}
    agent_root = root / "codex" / "agents"
    for path in sorted(agent_root.glob("*.toml")):
        data = read_toml(path)
        validate_agent(path, data)
        name = data["name"]
        if name in agents:
            raise ValueError(f"duplicate agent name: {name}")
        agents[name] = data

    manifest_agents = set(manifest["claude"]["derived_agents"])
    missing_agents = sorted(manifest_agents - set(agents))
    if missing_agents:
        raise ValueError(
            "manifest derived agents missing from codex/agents: "
            + ", ".join(missing_agents)
        )

    return {"schema_version": 1, "manifest": manifest, "agents": agents}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--root", type=Path, help="Compass repository root")
    source.add_argument(
        "--stdin", action="store_true", help="parse one TOML document from stdin"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = parse_stdin() if args.stdin else load_repository(args.root.resolve())
    except (UnicodeDecodeError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
