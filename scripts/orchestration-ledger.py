#!/usr/bin/env python3
"""Maintain a principal-authored local orchestration index and recovery guard."""

from __future__ import annotations

from _orchestration_ledger_cli import *
from _orchestration_ledger_core import *
from _orchestration_ledger_model import *
from _orchestration_ledger_mutation import *
from _orchestration_ledger_parser import *
from _orchestration_ledger_storage import *

if __name__ == "__main__":
    raise SystemExit(main())
