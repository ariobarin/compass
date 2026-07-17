from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("orchestration-ledger.py")
SPEC = importlib.util.spec_from_file_location("orchestration_ledger", MODULE_PATH)
assert SPEC and SPEC.loader
ledger_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ledger_module
SPEC.loader.exec_module(ledger_module)


def run_cli(*arguments: str) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        result = ledger_module.main(list(arguments))
    return result, stdout.getvalue(), stderr.getvalue()


def current_revision(root: Path) -> int:
    path = root / ".local" / "orchestration-ledger.json"
    if not path.exists():
        return 1
    return json.loads(path.read_text(encoding="utf-8"))["goals"][0]["control_revision"]


def run_mutation(
    root: Path,
    *arguments: str,
    actor: str = "controller",
) -> tuple[int, str, str]:
    return run_cli(
        "--root",
        str(root),
        *arguments,
        "--actor",
        actor,
        "--expected-revision",
        str(current_revision(root)),
    )


def init_goal(root: Path, goal_id: str = "goal") -> None:
    code, _, error = run_cli(
        "--root",
        str(root),
        "init",
        "--goal-id",
        goal_id,
        "--goal",
        "Deliver verified work",
        "--execution-owner",
        "worker",
        "--control-writer",
        "controller",
        "--state",
        "active",
    )
    if code != 0:
        raise AssertionError(error)
