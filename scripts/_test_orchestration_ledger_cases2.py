from __future__ import annotations

from _test_orchestration_ledger_common import *

class OrchestrationLedgerTests2(unittest.TestCase):
    def test_failure_with_new_evidence_allows_changed_successor(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "circuit")
                self.assertEqual(
                    run_mutation(
                        root,
                        "claim-successor",
                        "--goal-id",
                        "circuit",
                        "--slice-label",
                        "slice-a",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "record-successor-failure",
                        "--goal-id",
                        "circuit",
                        "--slice-label",
                        "slice-a",
                        "--failure-evidence",
                        "run:41",
                        "--discriminating-evidence",
                        "trace shows provider layer failed",
                    )[0],
                    0,
                )
                payload = json.loads(
                    (root / ".local" / "orchestration-ledger.json").read_text()
                )
                circuit = payload["goals"][0]["recovery_circuits"][0]
                self.assertEqual(circuit["state"], "closed")
                self.assertEqual(circuit["last_failure_evidence"], "run:41")
                self.assertEqual(
                    circuit["last_reset_evidence"],
                    "trace shows provider layer failed",
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "claim-successor",
                        "--goal-id",
                        "circuit",
                        "--slice-label",
                        "slice-a",
                    )[0],
                    0,
                )

    def test_failure_without_new_evidence_opens_circuit(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "circuit")
                self.assertEqual(
                    run_mutation(
                        root,
                        "claim-successor",
                        "--goal-id",
                        "circuit",
                        "--slice-label",
                        "slice-a",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "record-successor-failure",
                        "--goal-id",
                        "circuit",
                        "--slice-label",
                        "slice-a",
                        "--failure-evidence",
                        "run:42",
                        "--no-new-evidence",
                    )[0],
                    0,
                )
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "check-recovery",
                    "--goal-id",
                    "circuit",
                    "--slice-label",
                    "slice-a",
                )
                self.assertEqual(code, 1)
                self.assertIn("no new discriminating evidence", error)
                code, _, error = run_mutation(
                    root,
                    "claim-successor",
                    "--goal-id",
                    "circuit",
                    "--slice-label",
                    "slice-a",
                )
                self.assertEqual(code, 1)
                self.assertIn("circuit is open", error)

    def test_failure_requires_evidence_route_without_mutation(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "circuit")
                self.assertEqual(
                    run_mutation(
                        root,
                        "claim-successor",
                        "--goal-id",
                        "circuit",
                        "--slice-label",
                        "slice-a",
                    )[0],
                    0,
                )
                revision = current_revision(root)
                with self.assertRaises(SystemExit):
                    ledger_module.parse_args(
                        [
                            "--root",
                            str(root),
                            "record-successor-failure",
                            "--goal-id",
                            "circuit",
                            "--slice-label",
                            "slice-a",
                            "--failure-evidence",
                            "run:43",
                            "--actor",
                            "controller",
                            "--expected-revision",
                            str(revision),
                        ]
                    )
                self.assertEqual(current_revision(root), revision)

    def test_only_claim_owner_may_record_outcome(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "claim")
                self.assertEqual(
                    run_mutation(
                        root,
                        "set-grant",
                        "--goal-id",
                        "claim",
                        "--grant-actor",
                        "runner",
                        "--mutation",
                        "claim-successor",
                        "--mutation",
                        "record-successor-failure",
                        "--mutation",
                        "record-successor-success",
                    )[0],
                    0,
                )
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "claim-successor",
                    "--goal-id",
                    "claim",
                    "--slice-label",
                    "a",
                    "--actor",
                    "runner",
                    "--expected-revision",
                    "2",
                )
                self.assertEqual(code, 0, error)
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "record-successor-success",
                    "--goal-id",
                    "claim",
                    "--slice-label",
                    "a",
                    "--actor",
                    "controller",
                    "--expected-revision",
                    "3",
                )
                self.assertEqual(code, 1)
                self.assertIn("does not own the claim", error)

    def test_writer_reset_requires_evidence_and_success_clears_state(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "reset")
                self.assertEqual(
                    run_mutation(
                        root,
                        "claim-successor",
                        "--goal-id",
                        "reset",
                        "--slice-label",
                        "a",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "record-successor-failure",
                        "--goal-id",
                        "reset",
                        "--slice-label",
                        "a",
                        "--failure-evidence",
                        "run:44",
                        "--no-new-evidence",
                    )[0],
                    0,
                )
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "reset-recovery",
                    "--goal-id",
                    "reset",
                    "--slice-label",
                    "a",
                    "--root-cause-evidence",
                    "review:root",
                    "--actor",
                    "runner",
                    "--expected-revision",
                    str(current_revision(root)),
                )
                self.assertEqual(code, 1)
                self.assertIn("only control writer", error)
                self.assertEqual(
                    run_mutation(
                        root,
                        "reset-recovery",
                        "--goal-id",
                        "reset",
                        "--slice-label",
                        "a",
                        "--root-cause-evidence",
                        "review:root",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "claim-successor",
                        "--goal-id",
                        "reset",
                        "--slice-label",
                        "a",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "record-successor-success",
                        "--goal-id",
                        "reset",
                        "--slice-label",
                        "a",
                    )[0],
                    0,
                )
                payload = json.loads(
                    (root / ".local" / "orchestration-ledger.json").read_text()
                )
                circuit = payload["goals"][0]["recovery_circuits"][0]
                self.assertEqual(circuit, ledger_module.empty_circuit("a"))
