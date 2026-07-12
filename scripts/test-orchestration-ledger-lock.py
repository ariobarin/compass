#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("orchestration-ledger.py")
SPEC = importlib.util.spec_from_file_location("orchestration_ledger", MODULE_PATH)
assert SPEC and SPEC.loader
ledger = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ledger
SPEC.loader.exec_module(ledger)


class OrchestrationLedgerLockTests(unittest.TestCase):
    def test_second_writer_fails_without_mutating_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / ".local" / "orchestration-ledger.json"
            error = io.StringIO()

            with ledger.ledger_lock(path):
                with redirect_stderr(error):
                    exit_code = ledger.main(
                        [
                            "--root",
                            str(root),
                            "init",
                            "--goal-id",
                            "sample",
                            "--goal",
                            "Keep concurrent updates",
                            "--execution-owner",
                            "worker",
                        ]
                    )

            self.assertEqual(exit_code, 1)
            self.assertIn("locked by another writer", error.getvalue())
            self.assertFalse(path.exists())
            self.assertFalse(path.with_name(path.name + ".lock").exists())

    def test_lock_is_removed_after_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".local" / "orchestration-ledger.json"
            with self.assertRaisesRegex(RuntimeError, "boom"):
                with ledger.ledger_lock(path):
                    raise RuntimeError("boom")
            self.assertFalse(path.with_name(path.name + ".lock").exists())


if __name__ == "__main__":
    unittest.main()
