from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from _orchestration_ledger_core import *


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ledger", type=Path)


def add_mutation_auth_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--actor", "--principal", required=True)
    parser.add_argument(
        "--expected-revision",
        "--expected-control-revision",
        "--revision",
        dest="expected_revision",
        required=True,
        type=int,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_options(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status")
    status.add_argument("--goal-id")
    status.add_argument("--json", action="store_true")
    status.add_argument("--plain", action="store_true")

    validate = subparsers.add_parser("validate")
    validate.add_argument("--json", action="store_true")

    init = subparsers.add_parser("init")
    init.add_argument("--goal-id", required=True)
    init.add_argument("--goal", required=True)
    init.add_argument("--anchor", action="append", required=True)
    init.add_argument("--control-document", action="append", required=True)
    init.add_argument("--phase", choices=sorted(PHASES), default="planning")
    init.add_argument("--execution-owner", required=True)
    init.add_argument("--control-writer", "--principal", required=True)
    init.add_argument("--control-revision", type=int, default=1)
    init.add_argument("--worker-id")
    init.add_argument("--state", choices=sorted(STATES), default="planned")

    owner = subparsers.add_parser("set-owner")
    add_mutation_auth_options(owner)
    owner.add_argument("--goal-id", required=True)
    owner.add_argument("--execution-owner", required=True)
    worker_group = owner.add_mutually_exclusive_group()
    worker_group.add_argument("--worker-id")
    worker_group.add_argument("--clear-worker", action="store_true")

    phase = subparsers.add_parser("set-phase")
    add_mutation_auth_options(phase)
    phase.add_argument("--goal-id", required=True)
    phase.add_argument("--phase", choices=sorted(PHASES), required=True)

    links = subparsers.add_parser("set-links")
    add_mutation_auth_options(links)
    links.add_argument("--goal-id", required=True)
    links.add_argument("--anchor", action="append", required=True)
    links.add_argument("--control-document", action="append", required=True)

    state = subparsers.add_parser("set-state")
    add_mutation_auth_options(state)
    state.add_argument("--goal-id", required=True)
    state.add_argument("--state", choices=sorted(STATES), required=True)

    next_parser = subparsers.add_parser("set-next")
    add_mutation_auth_options(next_parser)
    next_parser.add_argument("--goal-id", required=True)
    next_group = next_parser.add_mutually_exclusive_group(required=True)
    next_group.add_argument("--action")
    next_group.add_argument("--clear", action="store_true")
    next_parser.add_argument("--check-at")

    evidence = subparsers.add_parser("add-evidence")
    add_mutation_auth_options(evidence)
    evidence.add_argument("--goal-id", required=True)
    evidence.add_argument("--kind", choices=sorted(EVIDENCE_KINDS), required=True)
    evidence.add_argument("--summary", required=True)
    evidence.add_argument("--locator")
    evidence.add_argument("--producer")
    evidence.add_argument("--observed-at")

    gate = subparsers.add_parser("set-gate")
    add_mutation_auth_options(gate)
    gate.add_argument("--goal-id", required=True)
    gate.add_argument("--gate", choices=sorted(GATES), required=True)
    gate.add_argument("--action")

    decision = subparsers.add_parser("set-decision")
    add_mutation_auth_options(decision)
    decision.add_argument("--goal-id", required=True)
    decision.add_argument("--question", required=True)
    decision.add_argument("--option", action="append", required=True)

    clear_decision = subparsers.add_parser("clear-decision")
    add_mutation_auth_options(clear_decision)
    clear_decision.add_argument("--goal-id", required=True)

    begin = subparsers.add_parser("begin-recovery")
    add_mutation_auth_options(begin)
    begin.add_argument("--goal-id", required=True)
    begin.add_argument("--slice-label", required=True)
    begin.add_argument("--worker-id", required=True)

    failure = subparsers.add_parser("record-recovery-failure")
    add_mutation_auth_options(failure)
    failure.add_argument("--goal-id", required=True)
    failure.add_argument("--slice-label", required=True)
    failure.add_argument("--failure-evidence", required=True)
    failure_route = failure.add_mutually_exclusive_group(required=True)
    failure_route.add_argument("--discriminating-evidence")
    failure_route.add_argument("--no-new-evidence", action="store_true")

    success = subparsers.add_parser("record-recovery-success")
    add_mutation_auth_options(success)
    success.add_argument("--goal-id", required=True)
    success.add_argument("--slice-label", required=True)

    reset = subparsers.add_parser("reset-recovery")
    add_mutation_auth_options(reset)
    reset.add_argument("--goal-id", required=True)
    reset.add_argument("--slice-label", required=True)
    reset.add_argument("--root-cause-evidence", required=True)

    recovery_check = subparsers.add_parser("check-recovery")
    recovery_check.add_argument("--goal-id", required=True)
    recovery_check.add_argument("--slice-label", required=True)
    recovery_check.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if getattr(args, "json", False) and getattr(args, "plain", False):
        parser.error("choose either --json or --plain")
    if args.command == "init" and args.control_revision < 1:
        parser.error("--control-revision must be a positive integer")
    return args
