#!/usr/bin/env python3
"""Run orchestration-ledger tests with unittest output on stdout."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

TEST_PATH = Path(__file__).with_name("test-orchestration-ledger.py")
SPEC = importlib.util.spec_from_file_location("test_orchestration_ledger", TEST_PATH)
if SPEC is None or SPEC.loader is None:
    raise SystemExit(f"could not load {TEST_PATH}")
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)

suite = unittest.defaultTestLoader.loadTestsFromModule(module)
result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
