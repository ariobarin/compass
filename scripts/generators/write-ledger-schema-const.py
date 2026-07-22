#!/usr/bin/env python3
"""Bind the orchestration-ledger schema_version const to the Python model.

The canonical source is SCHEMA_VERSION in scripts/_orchestration_ledger_core.py.
This generator writes that value into the schema_version.const field of
manifests/orchestration-ledger.schema.json so the JSON Schema and the Python
model cannot drift. Pass --check to verify the committed file is fresh; pass no
flag to write the canonical value in place.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "manifests" / "orchestration-ledger.schema.json"
CORE_PATH = ROOT / "scripts" / "_orchestration_ledger_core.py"

_CONST_PATTERN = re.compile(r'("schema_version":\s*\{\s*"const":\s*)(\d+)(\s*\})')


def current_schema_version() -> int:
    match = re.search(
        r"^SCHEMA_VERSION\s*=\s*(\d+)\s*$",
        CORE_PATH.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise SystemExit(f"SCHEMA_VERSION not found in {CORE_PATH}")
    return int(match.group(1))


def canonical_text() -> str:
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    version = current_schema_version()

    def replace_value(match: "re.Match[str]") -> str:
        return match.group(1) + str(version) + match.group(3)

    new_text, count = _CONST_PATTERN.subn(replace_value, text)
    if count != 1:
        raise SystemExit(f"schema_version const not found exactly once in {SCHEMA_PATH}")
    return new_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    desired = canonical_text()
    current = SCHEMA_PATH.read_text(encoding="utf-8")
    if desired == current:
        return 0
    if args.check:
        print(str(SCHEMA_PATH))
        return 1
    with SCHEMA_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(desired)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
