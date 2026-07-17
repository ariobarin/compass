#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from _test_orchestration_ledger_cases1 import OrchestrationLedgerTests1
from _test_orchestration_ledger_cases2 import OrchestrationLedgerTests2
from _test_orchestration_ledger_cases3 import OrchestrationLedgerTests3

if __name__ == "__main__":
    unittest.main()
