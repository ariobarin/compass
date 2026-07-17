from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Sequence

from _orchestration_ledger_core import *
from _orchestration_ledger_storage import *
from _orchestration_ledger_parser import *
from _orchestration_ledger_mutation import *

def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        _, path = resolve_ledger_path(args.root, args.ledger)
        if args.command == "status":
            ledger = load_ledger(path, allow_missing=True)
            payload = status_payload(path, ledger, args.goal_id)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(render_status(payload, args.plain))
            return 0
        if args.command == "validate":
            ledger = load_ledger(path)
            assert ledger is not None
            if args.json:
                print(
                    json.dumps(
                        {
                            "valid": True,
                            "ledger": str(path),
                            "goals": len(ledger["goals"]),
                        },
                        indent=2,
                    )
                )
            else:
                print(f"orchestration ledger valid: {path} ({len(ledger['goals'])} goals)")
            return 0
        if args.command == "check-recovery":
            ledger = load_ledger(path)
            assert ledger is not None
            circuit = check_recovery(ledger, args.goal_id, args.slice_label)
            if args.json:
                print(
                    json.dumps(
                        {
                            "check": "recovery",
                            "ok": True,
                            "observation_only": True,
                            "circuit": circuit,
                        },
                        indent=2,
                    )
                )
            else:
                print(
                    f"recovery observation passed for {args.goal_id} "
                    f"slice {circuit['slice_label']} ({circuit['state']})"
                )
            return 0
        with ledger_lock(path):
            ledger, message = mutate(args, path)
            write_ledger(path, ledger)
        print(message)
        return 0
    except (LedgerError, OSError) as error:
        print(f"orchestration ledger failed: {error}", file=sys.stderr)
        return 1
