#!/usr/bin/env python3
"""Validate narrow, non-negotiable policy text contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"missing policy contract manifest: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid policy contract manifest at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error

    if not isinstance(data, dict):
        raise ValueError("policy contract manifest must be a JSON object")
    if data.get("schema_version") != 1:
        raise ValueError("policy contract manifest requires schema_version 1")
    if not isinstance(data.get("contracts"), list) or not data["contracts"]:
        raise ValueError("policy contract manifest requires a non-empty contracts array")
    return data


def safe_repo_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("contract path must be a non-empty string")

    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"contract path must stay under the repository root: {value}")

    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"contract path escapes the repository root: {value}") from error
    return resolved


def string_list(contract_id: str, field: str, value: object, *, required: bool) -> list[str]:
    if value is None and not required:
        return []
    if not isinstance(value, list) or (required and not value):
        qualifier = "non-empty " if required else ""
        raise ValueError(f"contract {contract_id}: {field} must be a {qualifier}string array")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"contract {contract_id}: {field} must contain only non-empty strings")
    return value


def validate(root: Path, manifest_path: Path) -> list[str]:
    manifest = load_manifest(manifest_path)
    problems: list[str] = []
    seen_ids: set[str] = set()

    for index, raw_contract in enumerate(manifest["contracts"], start=1):
        if not isinstance(raw_contract, dict):
            problems.append(f"contract {index}: entry must be an object")
            continue

        contract_id = raw_contract.get("id")
        if not isinstance(contract_id, str) or not contract_id.strip():
            problems.append(f"contract {index}: id must be a non-empty string")
            continue
        if contract_id in seen_ids:
            problems.append(f"contract {contract_id}: duplicate id")
            continue
        seen_ids.add(contract_id)

        unknown = sorted(set(raw_contract) - {"id", "path", "required", "forbidden"})
        if unknown:
            problems.append(f"contract {contract_id}: unsupported fields: {', '.join(unknown)}")
            continue

        try:
            path = safe_repo_path(root, raw_contract.get("path"))
            required_phrases = string_list(
                contract_id, "required", raw_contract.get("required"), required=True
            )
            forbidden_phrases = string_list(
                contract_id, "forbidden", raw_contract.get("forbidden"), required=False
            )
        except ValueError as error:
            problems.append(str(error))
            continue

        try:
            content = normalize(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            problems.append(f"contract {contract_id}: missing file: {path.relative_to(root)}")
            continue
        except UnicodeDecodeError as error:
            problems.append(f"contract {contract_id}: file is not UTF-8: {error}")
            continue

        for phrase in required_phrases:
            if normalize(phrase) not in content:
                problems.append(
                    f"contract {contract_id}: required text missing from {path.relative_to(root)}: {phrase}"
                )
        for phrase in forbidden_phrases:
            if normalize(phrase) in content:
                problems.append(
                    f"contract {contract_id}: forbidden text present in {path.relative_to(root)}: {phrase}"
                )

    return problems


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="manifest path, defaults to <root>/manifests/policy-contracts.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    manifest = (
        args.manifest.resolve()
        if args.manifest
        else root / "manifests" / "policy-contracts.json"
    )

    try:
        problems = validate(root, manifest)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
