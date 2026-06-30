"""Shared helpers for portable hook guards."""

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


def add_context(event: str, context: str) -> None:
    write_json(
        {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}
    )


def deny_pre_tool(reason: str) -> None:
    write_json(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )


def continue_turn(reason: str) -> None:
    write_json({"decision": "block", "reason": reason})
