#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("orchestration-ledger.py")
SPEC = importlib.util.spec_from_file_location("orchestration_ledger", MODULE_PATH)
assert SPEC and SPEC.loader
ledger = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ledger
SPEC.loader.exec_module(ledger)


class LedgerHarness:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / ".local" / "orchestration-ledger.json"

    def run(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                exit_code = ledger.main(["--root", str(self.root), *args])
            except SystemExit as error:
                exit_code = int(error.code or 0)
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def init(self, goal_id: str = "release-42") -> dict[str, object]:
        exit_code, stdout, stderr = self.run(
            "init",
            "--goal-id",
            goal_id,
            "--goal",
            "Ship the reviewed release",
            "--anchor",
            "product-requirements.md",
            "--control-document",
            "local-docs/control/goal.md",
            "--control-document",
            "local-docs/control/catalog.md",
            "--execution-owner",
            "principal",
            "--control-writer",
            "principal",
        )
        if exit_code != 0:
            raise AssertionError(f"init failed: {stdout}{stderr}")
        return json.loads(self.path.read_text(encoding="utf-8"))

    def goal(self) -> dict[str, object]:
        return json.loads(self.path.read_text(encoding="utf-8"))["goals"][0]


class OrchestrationLedgerTests(unittest.TestCase):
    def test_init_writes_principal_authored_control_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            document = harness.init()
            goal = document["goals"][0]

            self.assertEqual(document["schema_version"], 4)
            self.assertEqual(goal["control_writer"], "principal")
            self.assertEqual(goal["phase"], "planning")
            self.assertEqual(goal["anchors"], ["product-requirements.md"])
            self.assertEqual(
                goal["control_documents"],
                ["local-docs/control/goal.md", "local-docs/control/catalog.md"],
            )
            self.assertEqual(goal["evidence"], [])
            self.assertEqual(goal["control_revision"], 1)
            self.assertTrue(goal["last_verified_at"].endswith("Z"))

    def test_init_requires_anchor_and_control_document(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            exit_code, _, stderr = harness.run(
                "init",
                "--goal-id",
                "missing-links",
                "--goal",
                "Keep continuity",
                "--execution-owner",
                "principal",
                "--control-writer",
                "principal",
            )
            self.assertEqual(exit_code, 2)
            self.assertIn("--anchor", stderr)
            self.assertFalse(harness.path.exists())

    def test_only_named_principal_may_mutate_control_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            exit_code, _, stderr = harness.run(
                "set-next",
                "--goal-id",
                "release-42",
                "--actor",
                "worker-7",
                "--expected-revision",
                "1",
                "--action",
                "Implement the approved slice",
            )
            self.assertEqual(exit_code, 1)
            self.assertIn("only principal control writer principal may mutate", stderr)
            self.assertEqual(harness.goal()["control_revision"], 1)

    def test_stale_revision_fails_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            first = harness.run(
                "set-next",
                "--goal-id",
                "release-42",
                "--actor",
                "principal",
                "--expected-revision",
                "1",
                "--action",
                "Review the assignment",
            )
            self.assertEqual(first[0], 0)
            second = harness.run(
                "set-state",
                "--goal-id",
                "release-42",
                "--actor",
                "principal",
                "--expected-revision",
                "1",
                "--state",
                "active",
            )
            self.assertEqual(second[0], 1)
            self.assertIn("stale control revision", second[2])
            self.assertEqual(harness.goal()["state"], "planned")

    def test_phase_and_links_change_only_through_principal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            self.assertEqual(
                harness.run(
                    "set-phase",
                    "--goal-id",
                    "release-42",
                    "--actor",
                    "principal",
                    "--expected-revision",
                    "1",
                    "--phase",
                    "implementation",
                )[0],
                0,
            )
            self.assertEqual(
                harness.run(
                    "set-links",
                    "--goal-id",
                    "release-42",
                    "--actor",
                    "principal",
                    "--expected-revision",
                    "2",
                    "--anchor",
                    "product-requirements.md#revision-4",
                    "--control-document",
                    "local-docs/control/checkpoint.md",
                )[0],
                0,
            )
            goal = harness.goal()
            self.assertEqual(goal["phase"], "implementation")
            self.assertEqual(goal["anchors"], ["product-requirements.md#revision-4"])
            self.assertEqual(goal["control_documents"], ["local-docs/control/checkpoint.md"])

    def test_delegate_evidence_is_verified_and_recorded_by_principal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            exit_code, _, stderr = harness.run(
                "add-evidence",
                "--goal-id",
                "release-42",
                "--actor",
                "principal",
                "--expected-revision",
                "1",
                "--kind",
                "test",
                "--summary",
                "Targeted tests passed",
                "--locator",
                "run:835",
                "--producer",
                "implementation-auth-01",
                "--observed-at",
                "2026-07-17T09:15:00-06:00",
            )
            self.assertEqual(exit_code, 0, stderr)
            evidence = harness.goal()["evidence"][0]
            self.assertEqual(evidence["producer"], "implementation-auth-01")
            self.assertEqual(evidence["verified_by"], "principal")
            self.assertEqual(evidence["observed_at"], "2026-07-17T15:15:00Z")
            self.assertEqual(harness.goal()["last_verified_at"], "2026-07-17T15:15:00Z")

    def test_last_verified_tracks_latest_observation_not_write_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            observations = (
                ("2026-07-17T10:00:00Z", "first"),
                ("2026-07-17T09:00:00Z", "older imported evidence"),
                ("2026-07-17T11:00:00Z", "newest"),
            )
            for revision, (observed_at, summary) in enumerate(observations, start=1):
                exit_code, _, stderr = harness.run(
                    "add-evidence",
                    "--goal-id",
                    "release-42",
                    "--actor",
                    "principal",
                    "--expected-revision",
                    str(revision),
                    "--kind",
                    "runtime",
                    "--summary",
                    summary,
                    "--observed-at",
                    observed_at,
                )
                self.assertEqual(exit_code, 0, stderr)
            self.assertEqual(harness.goal()["last_verified_at"], "2026-07-17T11:00:00Z")

    def test_recovery_opens_without_discriminating_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            self.assertEqual(
                harness.run(
                    "begin-recovery",
                    "--goal-id",
                    "release-42",
                    "--actor",
                    "principal",
                    "--expected-revision",
                    "1",
                    "--slice-label",
                    "checkout",
                    "--worker-id",
                    "recovery-01",
                )[0],
                0,
            )
            self.assertEqual(
                harness.run(
                    "record-recovery-failure",
                    "--goal-id",
                    "release-42",
                    "--actor",
                    "principal",
                    "--expected-revision",
                    "2",
                    "--slice-label",
                    "checkout",
                    "--failure-evidence",
                    "run:843",
                    "--no-new-evidence",
                )[0],
                0,
            )
            check = harness.run(
                "check-recovery",
                "--goal-id",
                "release-42",
                "--slice-label",
                "checkout",
            )
            self.assertEqual(check[0], 1)
            self.assertIn("changed hypothesis", check[2])
            self.assertEqual(harness.goal()["recovery_circuits"][0]["state"], "open")

    def test_root_cause_reset_allows_new_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            commands = [
                (
                    "begin-recovery",
                    "--goal-id", "release-42", "--actor", "principal",
                    "--expected-revision", "1", "--slice-label", "checkout",
                    "--worker-id", "recovery-01",
                ),
                (
                    "record-recovery-failure",
                    "--goal-id", "release-42", "--actor", "principal",
                    "--expected-revision", "2", "--slice-label", "checkout",
                    "--failure-evidence", "run:843", "--no-new-evidence",
                ),
                (
                    "reset-recovery",
                    "--goal-id", "release-42", "--actor", "principal",
                    "--expected-revision", "3", "--slice-label", "checkout",
                    "--root-cause-evidence", "review:provider-startup",
                ),
                (
                    "begin-recovery",
                    "--goal-id", "release-42", "--actor", "principal",
                    "--expected-revision", "4", "--slice-label", "checkout",
                    "--worker-id", "recovery-02",
                ),
            ]
            for command in commands:
                exit_code, _, stderr = harness.run(*command)
                self.assertEqual(exit_code, 0, stderr)
            circuit = harness.goal()["recovery_circuits"][0]
            self.assertEqual(circuit["state"], "active")
            self.assertEqual(circuit["assigned_worker"], "recovery-02")
            self.assertEqual(circuit["last_reset_evidence"], "review:provider-startup")

    def test_complete_requires_evidence_and_no_next_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            failed = harness.run(
                "set-state", "--goal-id", "release-42", "--actor", "principal",
                "--expected-revision", "1", "--state", "complete",
            )
            self.assertEqual(failed[0], 1)
            self.assertIn("state complete requires evidence", failed[2])
            self.assertEqual(harness.goal()["control_revision"], 1)

    def test_public_mutation_gate_records_existing_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            missing_action = harness.run(
                "set-gate", "--goal-id", "release-42", "--actor", "principal",
                "--expected-revision", "1", "--gate", "authorized",
            )
            self.assertEqual(missing_action[0], 1)
            self.assertIn("public mutation action", missing_action[2])
            success = harness.run(
                "set-gate", "--goal-id", "release-42", "--actor", "principal",
                "--expected-revision", "1", "--gate", "authorized",
                "--action", "merge PR 256 after current-head review",
            )
            self.assertEqual(success[0], 0, success[2])
            self.assertEqual(harness.goal()["public_mutation_gate"], "authorized")

    def test_schema_three_migrates_to_principal_only_schema_four(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.path.parent.mkdir(parents=True)
            legacy = {
                "schema_version": 3,
                "updated_at": "2026-07-17T12:00:00Z",
                "goals": [
                    {
                        "id": "legacy",
                        "goal": "Preserve the result",
                        "execution_owner": "principal",
                        "worker_id": "worker-7",
                        "state": "active",
                        "next_action": "Verify the result",
                        "next_check_at": None,
                        "completion_evidence": [
                            {
                                "kind": "runtime",
                                "summary": "Service is healthy",
                                "locator": "probe:1",
                                "recorded_at": "2026-07-17T11:00:00Z",
                            }
                        ],
                        "public_mutation_gate": "closed",
                        "public_mutation_action": None,
                        "decision_needed": None,
                        "control_writer": "principal",
                        "control_revision": 4,
                        "control_edit_grants": [
                            {"actor": "worker-7", "mutations": ["add-evidence"]}
                        ],
                        "recovery_circuits": [
                            {
                                "slice_label": "api",
                                "state": "claimed",
                                "last_failure_evidence": None,
                                "last_failure_at": None,
                                "last_reset_evidence": None,
                                "last_reset_at": None,
                                "claimed_by": "worker-7",
                            }
                        ],
                        "created_at": "2026-07-17T10:00:00Z",
                        "updated_at": "2026-07-17T12:00:00Z",
                    }
                ],
            }
            harness.path.write_text(json.dumps(legacy), encoding="utf-8")
            exit_code, stdout, stderr = harness.run("status", "--json")
            self.assertEqual(exit_code, 0, stderr)
            migrated = json.loads(stdout)["goals"][0]
            self.assertNotIn("control_edit_grants", migrated)
            self.assertEqual(migrated["phase"], "implementation")
            self.assertEqual(migrated["evidence"][0]["verified_by"], "principal")
            self.assertEqual(migrated["recovery_circuits"][0]["state"], "active")
            self.assertEqual(migrated["recovery_circuits"][0]["assigned_worker"], "worker-7")

    def test_ledger_path_stays_under_local_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "control.json"
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = ledger.main(
                    ["--root", str(root), "--ledger", str(outside), "status"]
                )
            self.assertEqual(exit_code, 1)
            self.assertIn("ledger path must stay under", stderr.getvalue())

    def test_status_exposes_links_phase_and_principal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = LedgerHarness(Path(directory))
            harness.init()
            exit_code, stdout, stderr = harness.run("status", "--plain")
            self.assertEqual(exit_code, 0, stderr)
            self.assertIn("phase=planning", stdout)
            self.assertIn("principal=principal", stdout)
            self.assertIn("revision=1", stdout)


if __name__ == "__main__":
    unittest.main()
