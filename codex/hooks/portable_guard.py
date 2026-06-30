#!/usr/bin/env python3
"""Portable Codex hook guard for local workflow checks."""

from __future__ import annotations

import json
import os
import sys


def env_enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def read_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}


def write_json(value: dict) -> None:
    print(json.dumps(value, separators=(",", ":")))


def main() -> int:
    read_input()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
