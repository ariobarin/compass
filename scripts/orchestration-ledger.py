#!/usr/bin/env python3
"""Maintain a local-only orchestration control ledger under .local/."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from _orchestration_ledger_core import LedgerError, validate_recovery_circuits
from _orchestration_ledger_model import validate_ledger
from _orchestration_ledger_storage import empty_circuit, ledger_lock
from _orchestration_ledger_parser import parse_args
from _orchestration_ledger_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
