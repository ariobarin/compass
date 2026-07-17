from __future__ import annotations

from _test_orchestration_ledger_common import *

class OrchestrationLedgerTests3(unittest.TestCase):
    def test_recovery_slices_are_independent(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "slices")
                for label, mode in (("a", "open"), ("b", "closed")):
                    self.assertEqual(
                        run_mutation(
                            root,
                            "claim-successor",
                            "--goal-id",
                            "slices",
                            "--slice-label",
                            label,
                        )[0],
                        0,
                    )
                    arguments = [
                        "record-successor-failure",
                        "--goal-id",
                        "slices",
                        "--slice-label",
                        label,
                        "--failure-evidence",
                        f"run:{label}",
                    ]
                    if mode == "open":
                        arguments.append("--no-new-evidence")
                    else:
                        arguments.extend(
                            ["--discriminating-evidence", "new layer identified"]
                        )
                    self.assertEqual(run_mutation(root, *arguments)[0], 0)
                payload = json.loads(
                    (root / ".local" / "orchestration-ledger.json").read_text()
                )
                circuits = {
                    item["slice_label"]: item
                    for item in payload["goals"][0]["recovery_circuits"]
                }
                self.assertEqual(circuits["a"]["state"], "open")
                self.assertEqual(circuits["b"]["state"], "closed")

    def test_legacy_schema_versions_migrate(self) -> None:
            now = "2026-07-11T12:00:00Z"
            legacy_v1 = {
                "schema_version": 1,
                "updated_at": now,
                "goals": [
                    {
                        "id": "legacy",
                        "goal": "Migrate",
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
            migrated = ledger_module.validate_ledger(legacy_v1)
            self.assertEqual(migrated["schema_version"], 3)
            self.assertEqual(migrated["goals"][0]["control_writer"], "worker")
            self.assertEqual(migrated["goals"][0]["recovery_circuits"], [])

            legacy_v2 = {
                "schema_version": 2,
                "updated_at": now,
                "goals": [
                    {
                        **legacy_v1["goals"][0],
                        "control_writer": "controller",
                        "control_revision": 2,
                        "control_edit_grants": [],
                        "recovery_circuits": [
                            {
                                "slice_label": "a",
                                "consecutive_successor_failures": 2,
                                "state": "open",
                                "last_reset_evidence": None,
                                "last_reset_at": None,
                                "claimed_by": None,
                            }
                        ],
                    }
                ],
            }
            migrated = ledger_module.validate_ledger(legacy_v2)
            circuit = migrated["goals"][0]["recovery_circuits"][0]
            self.assertEqual(migrated["schema_version"], 3)
            self.assertEqual(circuit["state"], "open")
            self.assertEqual(circuit["last_failure_evidence"], "migrated successor failure count: 2")
            self.assertEqual(circuit["last_failure_at"], now)

    def test_recovery_slice_labels_must_be_unique(self) -> None:
            duplicate = ledger_module.empty_circuit("slice-a")
            with self.assertRaisesRegex(
                ledger_module.LedgerError,
                "slice_label values must be unique",
            ):
                ledger_module.validate_recovery_circuits(
                    [duplicate, dict(duplicate)],
                    "circuits",
                )

    def test_unknown_fields_and_protected_legacy_grants_are_rejected(self) -> None:
            with self.assertRaisesRegex(ledger_module.LedgerError, "unsupported fields"):
                ledger_module.validate_ledger(
                    {
                        "schema_version": 3,
                        "updated_at": "2026-07-11T12:00:00Z",
                        "goals": [],
                        "secret": "no",
                    }
                )
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "grant")
                path = root / ".local" / "orchestration-ledger.json"
                payload = json.loads(path.read_text())
                payload["schema_version"] = 1
                payload["goals"][0]["control_edit_grants"] = [
                    {"actor": "runner", "mutations": ["set-grant", "reset-recovery"]}
                ]
                path.write_text(json.dumps(payload), encoding="utf-8")
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "set-grant",
                    "--goal-id",
                    "grant",
                    "--grant-actor",
                    "other",
                    "--mutation",
                    "set-state",
                    "--actor",
                    "runner",
                    "--expected-revision",
                    "1",
                )
                self.assertEqual(code, 1)
                self.assertIn("only control writer", error)
