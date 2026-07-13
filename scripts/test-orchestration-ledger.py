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


def run_mutation(root: Path, *arguments: str, actor: str = "controller") -> tuple[int, str, str]:
    ledger_path = root / ".local" / "orchestration-ledger.json"
    revision = 1
    if ledger_path.exists():
        payload = json.loads(ledger_path.read_text(encoding="utf-8"))
        revision = payload["goals"][0]["control_revision"]
    return run_cli(
        "--root",
        str(root),
        *arguments,
        "--actor",
        actor,
        "--expected-revision",
        str(revision),
    )


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
                "--control-writer",
                "controller",
                "--worker-id",
                "thread-123",
                "--state",
                "active",
            )
            self.assertEqual(code, 0, error)
            self.assertEqual(
                run_mutation(
                    root,
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
                run_mutation(root, "set-next", "--goal-id", "release-42", "--action", "Run final proof", "--check-at", "2026-07-12T12:00:00Z")[0],
                0,
            )
            self.assertEqual(
                run_mutation(root, "add-evidence", "--goal-id", "release-42", "--kind", "test", "--summary", "Portable checks passed", "--locator", "run:835")[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root,
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
                run_mutation(
                    root,
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
            self.assertEqual(run_mutation(root, "clear-decision", "--goal-id", "release-42")[0], 0)
            self.assertEqual(run_mutation(root, "set-next", "--goal-id", "release-42", "--clear")[0], 0)
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
                    "--control-writer",
                    "controller",
                )[0],
                0,
            )
            code, _, error = run_mutation(root, "set-state", "--goal-id", "proof", "--state", "complete")
            self.assertEqual(code, 1)
            self.assertIn("requires completion evidence", error)
            self.assertEqual(
                run_mutation(
                    root,
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
                run_mutation(root, "set-state", "--goal-id", "proof", "--state", "complete")[0],
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
                    "--control-writer",
                    "controller",
                )[0],
                0,
            )
            code, _, error = run_mutation(
                root,
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
                    "--control-writer",
                    "controller",
                )[0],
                0,
            )
            code, _, error = run_mutation(
                root,
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

    def test_legacy_schema_is_migrated_on_successful_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            now = "2026-07-11T12:00:00Z"
            legacy = {
                "schema_version": 1,
                "updated_at": now,
                "goals": [
                    {
                        "id": "legacy",
                        "goal": "Migrate this goal",
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
                    }
                ],
            }
            path = root / ".local" / "orchestration-ledger.json"
            path.parent.mkdir()
            path.write_text(json.dumps(legacy), encoding="utf-8")
            self.assertEqual(
                run_cli(
                    "--root", str(root), "set-state", "--goal-id", "legacy", "--state", "waiting",
                    "--actor", "worker", "--expected-revision", "1",
                )[0],
                0,
            )
            migrated = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(migrated["schema_version"], 2)
            self.assertEqual(migrated["goals"][0]["control_writer"], "worker")
            self.assertEqual(migrated["goals"][0]["control_revision"], 2)
            self.assertEqual(migrated["goals"][0]["recovery_circuits"], [])

    def test_current_schema_requires_control_fields(self) -> None:
        now = "2026-07-11T12:00:00Z"
        current_without_control = {
            "schema_version": 2,
            "updated_at": now,
            "goals": [
                {
                    "id": "missing-control",
                    "goal": "Missing control state",
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
                }
            ],
        }
        with self.assertRaisesRegex(ledger_module.LedgerError, "missing required control fields"):
            ledger_module.validate_ledger(current_without_control)

    def test_recovery_slice_labels_must_be_unique(self) -> None:
        duplicate = {
            "slice_label": "slice-a",
            "consecutive_successor_failures": 0,
            "state": "closed",
        }
        with self.assertRaisesRegex(ledger_module.LedgerError, "slice_label values must be unique"):
            ledger_module.validate_recovery_circuits([duplicate, dict(duplicate)], "circuits")

    def test_missing_claim_owner_migrates_claimed_slice_to_open(self) -> None:
        migrated = ledger_module.validate_recovery_circuit(
            {
                "slice_label": "legacy-slice",
                "consecutive_successor_failures": 1,
                "state": "claimed",
            },
            "circuit",
        )
        self.assertEqual(migrated["state"], "open")
        self.assertIsNone(migrated["claimed_by"])
        closed = ledger_module.validate_recovery_circuit(
            {
                "slice_label": "legacy-closed",
                "consecutive_successor_failures": 0,
                "state": "closed",
            },
            "circuit",
        )
        self.assertIsNone(closed["claimed_by"])

    def test_unauthorized_actor_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(
                run_cli(
                    "--root", str(root), "init", "--goal-id", "auth", "--goal", "Check auth",
                    "--execution-owner", "worker", "--control-writer", "controller",
                )[0],
                0,
            )
            code, _, error = run_cli(
                "--root", str(root), "set-state", "--goal-id", "auth", "--state", "active",
                "--actor", "intruder", "--expected-revision", "1",
            )
            self.assertEqual(code, 1)
            self.assertIn("not authorized", error)

    def test_stale_revision_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(
                run_cli(
                    "--root", str(root), "init", "--goal-id", "revision", "--goal", "Check revision",
                    "--execution-owner", "worker", "--control-writer", "controller",
                )[0],
                0,
            )
            self.assertEqual(run_mutation(root, "set-state", "--goal-id", "revision", "--state", "active")[0], 0)
            code, _, error = run_cli(
                "--root", str(root), "set-state", "--goal-id", "revision", "--state", "waiting",
                "--actor", "controller", "--expected-revision", "1",
            )
            self.assertEqual(code, 1)
            self.assertIn("stale control revision", error)
            payload = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            self.assertEqual(payload["goals"][0]["state"], "active")
            self.assertEqual(payload["goals"][0]["control_revision"], 2)

    def test_delegated_grant_allows_exact_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(
                run_cli(
                    "--root", str(root), "init", "--goal-id", "delegate", "--goal", "Delegate one edit",
                    "--execution-owner", "worker", "--control-writer", "controller",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "set-grant", "--goal-id", "delegate", "--grant-actor", "recovery",
                    "--mutation", "set-state",
                )[0],
                0,
            )
            code, _, error = run_cli(
                "--root", str(root), "set-state", "--goal-id", "delegate", "--state", "active",
                "--actor", "recovery", "--expected-revision", "2",
            )
            self.assertEqual(code, 0, error)
            payload = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            self.assertEqual(payload["goals"][0]["state"], "active")
            self.assertEqual(payload["goals"][0]["control_revision"], 3)

    def test_successor_state_machine_and_atomic_claims(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(
                run_cli(
                    "--root", str(root), "init", "--goal-id", "circuit", "--goal", "Guard recovery",
                    "--execution-owner", "worker", "--control-writer", "controller",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "set-grant", "--goal-id", "circuit", "--grant-actor", "other",
                    "--mutation", "record-successor-failure",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "claim-successor", "--goal-id", "circuit", "--slice-label", "slice-a",
                )[0],
                0,
            )
            payload = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            self.assertEqual(payload["goals"][0]["recovery_circuits"][0]["claimed_by"], "controller")
            code, _, error = run_mutation(
                root,
                "record-successor-failure",
                "--goal-id",
                "circuit",
                "--slice-label",
                "slice-a",
                actor="other",
            )
            self.assertEqual(code, 1)
            self.assertIn("does not own the claim", error)
            code, _, error = run_mutation(
                root, "claim-successor", "--goal-id", "circuit", "--slice-label", "slice-a",
            )
            self.assertEqual(code, 1)
            self.assertIn("already claimed", error)
            self.assertEqual(
                run_mutation(
                    root, "record-successor-failure", "--goal-id", "circuit", "--slice-label", "slice-a",
                )[0],
                0,
            )
            payload = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            circuit = payload["goals"][0]["recovery_circuits"][0]
            self.assertEqual(circuit["consecutive_successor_failures"], 1)
            self.assertEqual(circuit["state"], "closed")
            self.assertIsNone(circuit["claimed_by"])
            self.assertEqual(
                run_mutation(
                    root, "claim-successor", "--goal-id", "circuit", "--slice-label", "slice-a",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "record-successor-failure", "--goal-id", "circuit", "--slice-label", "slice-a",
                )[0],
                0,
            )
            payload = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            circuit = payload["goals"][0]["recovery_circuits"][0]
            self.assertEqual(circuit["consecutive_successor_failures"], 2)
            self.assertEqual(circuit["state"], "open")

    def test_success_resets_claimed_slice(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(
                run_cli(
                    "--root", str(root), "init", "--goal-id", "success", "--goal", "Record success",
                    "--execution-owner", "worker", "--control-writer", "controller",
                )[0],
                0,
            )
            self.assertEqual(run_mutation(root, "claim-successor", "--goal-id", "success", "--slice-label", "a")[0], 0)
            self.assertEqual(run_mutation(root, "record-successor-failure", "--goal-id", "success", "--slice-label", "a")[0], 0)
            self.assertEqual(run_mutation(root, "claim-successor", "--goal-id", "success", "--slice-label", "a")[0], 0)
            self.assertEqual(run_mutation(root, "record-successor-success", "--goal-id", "success", "--slice-label", "a")[0], 0)
            payload = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            circuit = payload["goals"][0]["recovery_circuits"][0]
            self.assertEqual(circuit["consecutive_successor_failures"], 0)
            self.assertEqual(circuit["state"], "closed")
            self.assertIsNone(circuit["claimed_by"])

    def test_recovery_circuits_are_independent_and_check_is_prelaunch_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(
                run_cli(
                    "--root", str(root), "init", "--goal-id", "slices", "--goal", "Track slices",
                    "--execution-owner", "worker", "--control-writer", "controller",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "claim-successor", "--goal-id", "slices", "--slice-label", "slice-a",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "record-successor-failure", "--goal-id", "slices", "--slice-label", "slice-a",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "claim-successor", "--goal-id", "slices", "--slice-label", "slice-a",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "record-successor-failure", "--goal-id", "slices", "--slice-label", "slice-a",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "claim-successor", "--goal-id", "slices", "--slice-label", "slice-b",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "record-successor-success", "--goal-id", "slices", "--slice-label", "slice-b",
                )[0],
                0,
            )
            payload = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            circuits = {item["slice_label"]: item for item in payload["goals"][0]["recovery_circuits"]}
            self.assertEqual(circuits["slice-a"]["consecutive_successor_failures"], 2)
            self.assertEqual(circuits["slice-a"]["state"], "open")
            self.assertEqual(circuits["slice-b"]["consecutive_successor_failures"], 0)
            self.assertEqual(circuits["slice-b"]["state"], "closed")
            code, _, error = run_cli(
                "--root", str(root), "check-recovery", "--goal-id", "slices", "--slice-label", "slice-a",
            )
            self.assertEqual(code, 1)
            self.assertIn("circuit is open", error)
            self.assertEqual(
                run_cli(
                    "--root", str(root), "check-recovery", "--goal-id", "slices", "--slice-label", "slice-b",
                )[0],
                0,
            )
            self.assertEqual(
                run_cli(
                    "--root", str(root), "check-recovery", "--goal-id", "slices", "--slice-label", "slice-c",
                )[0],
                0,
            )

    def test_writer_reset_requires_evidence_and_delegated_runner_cannot_reset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(
                run_cli(
                    "--root", str(root), "init", "--goal-id", "reset", "--goal", "Check reset",
                    "--execution-owner", "worker", "--control-writer", "controller",
                )[0],
                0,
            )
            self.assertEqual(
                run_mutation(
                    root, "set-grant", "--goal-id", "reset", "--grant-actor", "runner",
                    "--mutation", "claim-successor", "--mutation", "record-successor-failure",
                    "--mutation", "record-successor-success",
                )[0],
                0,
            )
            self.assertEqual(run_cli("--root", str(root), "claim-successor", "--goal-id", "reset", "--slice-label", "a", "--actor", "runner", "--expected-revision", "2")[0], 0)
            self.assertEqual(run_cli("--root", str(root), "record-successor-failure", "--goal-id", "reset", "--slice-label", "a", "--actor", "runner", "--expected-revision", "3")[0], 0)
            self.assertEqual(run_cli("--root", str(root), "claim-successor", "--goal-id", "reset", "--slice-label", "a", "--actor", "runner", "--expected-revision", "4")[0], 0)
            self.assertEqual(run_cli("--root", str(root), "record-successor-failure", "--goal-id", "reset", "--slice-label", "a", "--actor", "runner", "--expected-revision", "5")[0], 0)
            code, _, error = run_cli("--root", str(root), "reset-recovery", "--goal-id", "reset", "--slice-label", "a", "--root-cause-evidence", "review:root", "--actor", "runner", "--expected-revision", "6")
            self.assertEqual(code, 1)
            self.assertIn("only control writer", error)
            code, _, error = run_cli(
                "--root", str(root), "set-grant", "--goal-id", "reset", "--grant-actor", "other",
                "--mutation", "claim-successor", "--actor", "runner", "--expected-revision", "6",
            )
            self.assertEqual(code, 1)
            self.assertIn("only control writer", error)
            code, _, error = run_mutation(root, "reset-recovery", "--goal-id", "reset", "--slice-label", "a", "--root-cause-evidence", "")
            self.assertEqual(code, 1)
            self.assertIn("root-cause evidence", error)
            self.assertEqual(run_mutation(root, "reset-recovery", "--goal-id", "reset", "--slice-label", "a", "--root-cause-evidence", "review:root")[0], 0)
            payload = json.loads((root / ".local" / "orchestration-ledger.json").read_text())
            circuit = payload["goals"][0]["recovery_circuits"][0]
            self.assertEqual(circuit["consecutive_successor_failures"], 0)
            self.assertEqual(circuit["state"], "closed")
            self.assertEqual(circuit["last_reset_evidence"], "review:root")
            self.assertIsNotNone(circuit["last_reset_at"])
            self.assertIsNone(circuit["claimed_by"])

    def test_protected_grants_are_not_delegable_even_in_legacy_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(
                run_cli(
                    "--root", str(root), "init", "--goal-id", "legacy-grant", "--goal", "Check grant safety",
                    "--execution-owner", "worker", "--control-writer", "controller",
                )[0],
                0,
            )
            path = root / ".local" / "orchestration-ledger.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["schema_version"] = 1
            payload["goals"][0]["control_edit_grants"] = [
                {"actor": "runner", "mutations": ["set-grant", "reset-recovery"]}
            ]
            path.write_text(json.dumps(payload), encoding="utf-8")
            code, _, error = run_cli(
                "--root", str(root), "set-grant", "--goal-id", "legacy-grant",
                "--grant-actor", "other", "--mutation", "claim-successor",
                "--actor", "runner", "--expected-revision", "1",
            )
            self.assertEqual(code, 1)
            self.assertIn("only control writer", error)


if __name__ == "__main__":
    unittest.main()
