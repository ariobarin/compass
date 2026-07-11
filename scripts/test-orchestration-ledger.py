#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("orchestration-ledger.py")
SPEC = importlib.util.spec_from_file_location("orchestration_ledger", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def parse(root: Path, ledger: Path, *arguments: str):
    return module.parse_args(["--root", str(root), "--ledger", str(ledger), *arguments])


class OrchestrationLedgerTests(unittest.TestCase):
    def test_init_status_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / ".local" / "ledger.json"
            created = module.execute(
                parse(
                    root,
                    ledger,
                    "init",
                    "--id",
                    "repo-a",
                    "--goal",
                    "Land the reviewed change",
                    "--repository",
                    "owner/repo",
                    "--execution-owner",
                    "worker-a",
                    "--completion-evidence",
                    "checks pass",
                )
            )
            self.assertEqual(created["state"], "planned")
            self.assertEqual(created["public_mutation_gate"]["state"], "closed")
            status = module.execute(parse(root, ledger, "status"))
            self.assertEqual(status["summary"]["total"], 1)
            self.assertEqual(module.execute(parse(root, ledger, "validate"))["items"], 1)
            self.assertEqual(module.validate_ledger(json.loads(ledger.read_text())), [])

    def test_state_transition_requires_force_after_completion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / ".local" / "ledger.json"
            module.execute(parse(root, ledger, "init", "--id", "job", "--goal", "Goal", "--execution-owner", "worker"))
            module.execute(parse(root, ledger, "set-state", "--id", "job", "--state", "active"))
            module.execute(parse(root, ledger, "set-state", "--id", "job", "--state", "complete"))
            with self.assertRaisesRegex(module.LedgerError, "requires --force"):
                module.execute(parse(root, ledger, "set-state", "--id", "job", "--state", "active"))
            reopened = module.execute(parse(root, ledger, "set-state", "--id", "job", "--state", "active", "--force"))
            self.assertEqual(reopened["state"], "active")

    def test_gate_records_state_but_starts_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / ".local" / "ledger.json"
            module.execute(parse(root, ledger, "init", "--id", "job", "--goal", "Goal", "--execution-owner", "worker"))
            with self.assertRaisesRegex(module.LedgerError, "requires --reason"):
                module.execute(parse(root, ledger, "set-gate", "--id", "job", "--state", "open"))
            item = module.execute(parse(root, ledger, "set-gate", "--id", "job", "--state", "open", "--reason", "Owner authorized the exact push"))
            self.assertEqual(item["public_mutation_gate"]["state"], "open")

    def test_decision_requires_prepared_options(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / ".local" / "ledger.json"
            module.execute(parse(root, ledger, "init", "--id", "job", "--goal", "Goal", "--execution-owner", "worker"))
            with self.assertRaisesRegex(module.LedgerError, "2 to 10"):
                module.execute(parse(root, ledger, "set-decision", "--id", "job", "--question", "Choose", "--option", "one"))
            item = module.execute(
                parse(
                    root,
                    ledger,
                    "set-decision",
                    "--id",
                    "job",
                    "--question",
                    "Choose the release route",
                    "--option",
                    "ship now",
                    "--option",
                    "hold for review",
                    "--evidence",
                    "CI is green; review is pending",
                )
            )
            self.assertEqual(len(item["decision_needed"]["options"]), 2)

    def test_lock_refuses_concurrent_writer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / ".local" / "ledger.json"
            ledger.parent.mkdir(parents=True)
            lock = ledger.with_name(ledger.name + ".lock")
            lock.write_text("held\n", encoding="utf-8")
            with self.assertRaisesRegex(module.LedgerError, "locked by another writer"):
                module.execute(parse(root, ledger, "init", "--id", "job", "--goal", "Goal", "--execution-owner", "worker"))

    def test_repository_path_must_stay_under_local(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(module.LedgerError, "must stay under .local"):
                module.resolve_ledger_path(root, root / "ledger.json")
            external = root.parent / f"{root.name}-external-ledger.json"
            self.assertEqual(module.resolve_ledger_path(root, external), external.resolve())

    def test_evidence_and_next_action_are_compact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / ".local" / "ledger.json"
            module.execute(parse(root, ledger, "init", "--id", "job", "--goal", "Goal", "--execution-owner", "worker"))
            module.execute(parse(root, ledger, "set-next", "--id", "job", "--summary", "Inspect current checks", "--check-at", "2030-01-01T00:00:00Z"))
            item = module.execute(parse(root, ledger, "add-evidence", "--id", "job", "--kind", "check", "--summary", "Focused tests passed", "--locator", "run-123"))
            self.assertEqual(item["next_action"]["check_at"], "2030-01-01T00:00:00Z")
            self.assertEqual(item["evidence"][0]["locator"], "run-123")


if __name__ == "__main__":
    unittest.main()
