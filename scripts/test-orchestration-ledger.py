#!/usr/bin/env python3
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


class OrchestrationLedgerTests(unittest.TestCase):
    def test_status_reports_absent_without_creating_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, stdout, stderr = run_cli("--root", str(root), "status", "--json")
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertFalse(payload["present"])
            self.assertFalse((root / ".local").exists())

    def test_init_and_full_control_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            common = ("--root", str(root))
            code, _, error = run_cli(
                *common,
                "init",
                "--goal-id",
                "release-42",
                "--goal",
                "Ship the reviewed release",
                "--execution-owner",
                "release-worker",
                "--worker-id",
                "thread-123",
                "--state",
                "active",
            )
            self.assertEqual(code, 0, error)
            self.assertEqual(
                run_cli(
                    *common,
                    "set-owner",
                    "--goal-id",
                    "release-42",
                    "--execution-owner",
                    "release-worker-2",
                    "--worker-id",
                    "thread-456",
                )[0],
                0,
            )
            self.assertEqual(
                run_cli(*common, "set-next", "--goal-id", "release-42", "--action", "Run final proof", "--check-at", "2026-07-12T12:00:00Z")[0],
                0,
            )
            self.assertEqual(
                run_cli(*common, "add-evidence", "--goal-id", "release-42", "--kind", "test", "--summary", "Portable checks passed", "--locator", "run:835")[0],
                0,
            )
            self.assertEqual(
                run_cli(
                    *common,
                    "set-gate",
                    "--goal-id",
                    "release-42",
                    "--gate",
                    "authorized",
                    "--action",
                    "merge PR 42",
                )[0],
                0,
            )
            self.assertEqual(
                run_cli(
                    *common,
                    "set-decision",
                    "--goal-id",
                    "release-42",
                    "--question",
                    "Which release channel?",
                    "--option",
                    "stable",
                    "--option",
                    "beta",
                )[0],
                0,
            )
            code, stdout, error = run_cli(*common, "status", "--goal-id", "release-42", "--json")
            self.assertEqual(code, 0, error)
            goal = json.loads(stdout)["goals"][0]
            self.assertEqual(goal["state"], "active")
            self.assertEqual(goal["execution_owner"], "release-worker-2")
            self.assertEqual(goal["worker_id"], "thread-456")
            self.assertEqual(goal["next_action"], "Run final proof")
            self.assertEqual(goal["next_check_at"], "2026-07-12T12:00:00Z")
            self.assertEqual(goal["public_mutation_gate"], "authorized")
            self.assertEqual(goal["public_mutation_action"], "merge PR 42")
            self.assertEqual(goal["completion_evidence"][0]["locator"], "run:835")
            self.assertEqual(goal["decision_needed"]["options"], ["stable", "beta"])
            self.assertEqual(run_cli(*common, "validate")[0], 0)
            self.assertEqual(run_cli(*common, "clear-decision", "--goal-id", "release-42")[0], 0)
            self.assertEqual(run_cli(*common, "set-next", "--goal-id", "release-42", "--clear")[0], 0)
            disk = json.loads((root / ".local" / "orchestration-ledger.json").read_text(encoding="utf-8"))
            self.assertIsNone(disk["goals"][0]["decision_needed"])
            self.assertIsNone(disk["goals"][0]["next_action"])
            if os.name != "nt":
                mode = stat.S_IMODE((root / ".local" / "orchestration-ledger.json").stat().st_mode)
                self.assertEqual(mode, 0o600)

    def test_complete_state_requires_evidence_and_no_open_work(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            common = ("--root", str(root))
            self.assertEqual(
                run_cli(
                    *common,
                    "init",
                    "--goal-id",
                    "proof",
                    "--goal",
                    "Prove completion",
                    "--execution-owner",
                    "worker",
                )[0],
                0,
            )
            code, _, error = run_cli(
                *common, "set-state", "--goal-id", "proof", "--state", "complete"
            )
            self.assertEqual(code, 1)
            self.assertIn("requires completion evidence", error)
            self.assertEqual(
                run_cli(
                    *common,
                    "add-evidence",
                    "--goal-id",
                    "proof",
                    "--kind",
                    "test",
                    "--summary",
                    "The completion condition passed",
                )[0],
                0,
            )
            self.assertEqual(
                run_cli(*common, "set-state", "--goal-id", "proof", "--state", "complete")[0],
                0,
            )

    def test_duplicate_goal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            arguments = (
                "--root",
                str(root),
                "init",
                "--goal-id",
                "same",
                "--goal",
                "Do one thing",
                "--execution-owner",
                "worker",
            )
            self.assertEqual(run_cli(*arguments)[0], 0)
            code, _, error = run_cli(*arguments)
            self.assertEqual(code, 1)
            self.assertIn("goal already exists", error)

    def test_ledger_path_cannot_escape_local_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, _, error = run_cli(
                "--root",
                str(root),
                "--ledger",
                str(root / "outside.json"),
                "status",
            )
            self.assertEqual(code, 1)
            self.assertIn("must stay under", error)

    def test_ledger_path_dot_dot_cannot_escape_local_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, _, error = run_cli(
                "--root",
                str(root),
                "--ledger",
                ".local/../outside.json",
                "status",
            )
            self.assertEqual(code, 1)
            self.assertIn("must stay under", error)

    def test_authorized_gate_requires_named_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            common = ("--root", str(root))
            self.assertEqual(
                run_cli(
                    *common,
                    "init",
                    "--goal-id",
                    "gate",
                    "--goal",
                    "Guard publication",
                    "--execution-owner",
                    "worker",
                )[0],
                0,
            )
            code, _, error = run_cli(
                *common,
                "set-gate",
                "--goal-id",
                "gate",
                "--gate",
                "authorized",
            )
            self.assertEqual(code, 1)
            self.assertIn("public mutation action", error)
            disk = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            self.assertEqual(disk["goals"][0]["public_mutation_gate"], "closed")
            self.assertIsNone(disk["goals"][0]["public_mutation_action"])

    def test_invalid_timestamp_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(
                run_cli(
                    "--root",
                    str(root),
                    "init",
                    "--goal-id",
                    "time-check",
                    "--goal",
                    "Check time",
                    "--execution-owner",
                    "worker",
                )[0],
                0,
            )
            code, _, error = run_cli(
                "--root",
                str(root),
                "set-next",
                "--goal-id",
                "time-check",
                "--action",
                "Wake later",
                "--check-at",
                "tomorrow",
            )
            self.assertEqual(code, 1)
            self.assertIn("ISO 8601", error)
            disk = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            self.assertIsNone(disk["goals"][0]["next_action"])

    def test_symlinked_local_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "repo"
            target = parent / "target"
            root.mkdir()
            target.mkdir()
            try:
                (root / ".local").symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest("symlinks are unavailable")
            code, _, error = run_cli("--root", str(root), "status")
            self.assertEqual(code, 1)
            self.assertIn("must not traverse a symlink", error)

    def test_validator_rejects_unknown_fields(self) -> None:
        now = "2026-07-11T12:00:00Z"
        invalid = {
            "schema_version": 1,
            "updated_at": now,
            "goals": [
                {
                    "id": "bad",
                    "goal": "Bad goal",
                    "execution_owner": "worker",
                    "worker_id": None,
                    "state": "active",
                    "next_action": None,
                    "next_check_at": None,
                    "completion_evidence": [],
                    "public_mutation_gate": "closed",
                    "public_mutation_action": None,
                    "decision_needed": None,
                    "created_at": now,
                    "updated_at": now,
                    "secret": "not allowed",
                }
            ],
        }
        with self.assertRaisesRegex(ledger_module.LedgerError, "unsupported fields"):
            ledger_module.validate_ledger(invalid)


if __name__ == "__main__":
    unittest.main()
