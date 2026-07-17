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
from _orchestration_ledger_model import *
from _orchestration_ledger_storage import *

def mutate(args: argparse.Namespace, path: Path) -> tuple[dict[str, Any], str]:
    existing = load_ledger(path, allow_missing=True)
    if args.command == "init":
        goal_id = validate_id(args.goal_id)
        ledger = existing or {
            "schema_version": SCHEMA_VERSION,
            "updated_at": utc_now(),
            "goals": [],
        }
        if any(goal["id"] == goal_id for goal in ledger["goals"]):
            raise LedgerError(f"goal already exists: {goal_id}")
        now = utc_now()
        control_writer = nonempty_string(
            args.control_writer if args.control_writer is not None else args.execution_owner,
            "control writer",
        )
        ledger["goals"].append(
            {
                "id": goal_id,
                "goal": nonempty_string(args.goal, "goal"),
                "execution_owner": nonempty_string(args.execution_owner, "execution owner"),
                "worker_id": nonempty_string(args.worker_id, "worker id", nullable=True),
                "state": args.state,
                "next_action": None,
                "next_check_at": None,
                "completion_evidence": [],
                "public_mutation_gate": "closed",
                "public_mutation_action": None,
                "decision_needed": None,
                "control_writer": control_writer,
                "control_revision": args.control_revision,
                "control_edit_grants": [],
                "recovery_circuits": [],
                "created_at": now,
                "updated_at": now,
            }
        )
        ledger["updated_at"] = now
        return ledger, f"initialized goal {goal_id}"

    if existing is None:
        raise LedgerError(f"orchestration ledger is missing: {path}")
    ledger = existing
    goal = goal_by_id(ledger, validate_id(args.goal_id))
    authorize_mutation(args, goal)

    if args.command == "set-owner":
        goal["execution_owner"] = nonempty_string(args.execution_owner, "execution owner")
        if args.clear_worker:
            goal["worker_id"] = None
        elif args.worker_id is not None:
            goal["worker_id"] = nonempty_string(args.worker_id, "worker id")
        message = f"set {goal['id']} execution owner"
    elif args.command == "set-state":
        goal["state"] = args.state
        message = f"set {goal['id']} state to {args.state}"
    elif args.command == "set-next":
        if args.clear:
            goal["next_action"] = None
            goal["next_check_at"] = None
            message = f"cleared {goal['id']} next action"
        else:
            goal["next_action"] = nonempty_string(args.action, "next action")
            goal["next_check_at"] = parse_timestamp(args.check_at, "next check", nullable=True)
            message = f"set {goal['id']} next action"
    elif args.command == "add-evidence":
        goal["completion_evidence"].append(
            {
                "kind": args.kind,
                "summary": nonempty_string(args.summary, "evidence summary"),
                "locator": nonempty_string(args.locator, "evidence locator", nullable=True),
                "recorded_at": utc_now(),
            }
        )
        message = f"added evidence to {goal['id']}"
    elif args.command == "set-gate":
        goal["public_mutation_gate"] = args.gate
        if args.gate == "closed":
            if args.action is not None:
                raise LedgerError("--action is not allowed when closing the public mutation gate")
            goal["public_mutation_action"] = None
        else:
            goal["public_mutation_action"] = nonempty_string(
                args.action,
                "public mutation action",
            )
        message = f"set {goal['id']} public mutation gate to {args.gate}"
    elif args.command == "set-decision":
        options = [nonempty_string(option, "decision option") for option in args.option]
        if len(options) < 2 or len(set(options)) != len(options):
            raise LedgerError("decision requires at least two unique options")
        goal["decision_needed"] = {
            "question": nonempty_string(args.question, "decision question"),
            "options": options,
            "prepared_at": utc_now(),
        }
        message = f"set decision for {goal['id']}"
    elif args.command == "clear-decision":
        goal["decision_needed"] = None
        message = f"cleared decision for {goal['id']}"
    elif args.command == "set-grant":
        grant_actor = nonempty_string(args.grant_actor, "grant actor")
        mutations = [nonempty_string(item, "grant mutation") for item in args.mutations]
        assert all(item is not None for item in mutations)
        unsupported = sorted(set(mutations) - GRANTABLE_MUTATION_COMMANDS)
        if unsupported:
            raise LedgerError(f"grant mutations contain unsupported commands: {', '.join(unsupported)}")
        if len(set(mutations)) != len(mutations):
            raise LedgerError("grant mutations must be unique")
        goal["control_edit_grants"] = [
            grant
            for grant in goal["control_edit_grants"]
            if grant["actor"] != grant_actor
        ]
        goal["control_edit_grants"].append(
            {"actor": grant_actor, "mutations": mutations}
        )
        message = f"set control edit grant for {grant_actor} on {goal['id']}"
    elif args.command == "clear-grant":
        grant_actor = nonempty_string(args.grant_actor, "grant actor")
        before = len(goal["control_edit_grants"])
        goal["control_edit_grants"] = [
            grant
            for grant in goal["control_edit_grants"]
            if grant["actor"] != grant_actor
        ]
        if len(goal["control_edit_grants"]) == before:
            raise LedgerError(f"no control edit grant for actor {grant_actor}")
        message = f"cleared control edit grant for {grant_actor} on {goal['id']}"
    elif args.command in {
        "claim-successor",
        "record-successor-failure",
        "record-successor-success",
        "reset-recovery",
    }:
        circuits = goal["recovery_circuits"]
        slice_label = nonempty_string(args.slice_label, "slice label")
        assert slice_label is not None
        current_index = next(
            (
                index
                for index, circuit in enumerate(circuits)
                if circuit["slice_label"] == slice_label
            ),
            None,
        )
        current = circuits[current_index] if current_index is not None else None
        if args.command == "claim-successor":
            if current is not None and current["state"] == "open":
                raise LedgerError(f"recovery circuit is open for slice {slice_label}")
            if current is not None and current["state"] == "claimed":
                raise LedgerError(f"successor is already claimed for slice {slice_label}")
            updated = dict(current or empty_circuit(slice_label))
            updated["state"] = "claimed"
            updated["claimed_by"] = args.actor
            message = f"claimed successor for {goal['id']} slice {slice_label}"
        elif args.command == "record-successor-failure":
            if current is None or current["state"] != "claimed":
                raise LedgerError(f"slice {slice_label} must be claimed before recording failure")
            if current["claimed_by"] != args.actor:
                raise LedgerError(
                    f"actor {args.actor} does not own the claim for slice {slice_label}"
                )
            failure_evidence = nonempty_string(args.failure_evidence, "failure evidence")
            assert failure_evidence is not None
            updated = dict(current)
            updated["last_failure_evidence"] = failure_evidence
            updated["last_failure_at"] = utc_now()
            updated["claimed_by"] = None
            if args.no_new_evidence:
                updated["state"] = "open"
                updated["last_reset_evidence"] = None
                updated["last_reset_at"] = None
            else:
                discriminating = nonempty_string(
                    args.discriminating_evidence,
                    "discriminating evidence",
                )
                assert discriminating is not None
                updated["state"] = "closed"
                updated["last_reset_evidence"] = discriminating
                updated["last_reset_at"] = utc_now()
            message = f"recorded successor failure for {goal['id']} slice {slice_label}"
        elif args.command == "record-successor-success":
            if current is None or current["state"] != "claimed":
                raise LedgerError(f"slice {slice_label} must be claimed before recording success")
            if current["claimed_by"] != args.actor:
                raise LedgerError(
                    f"actor {args.actor} does not own the claim for slice {slice_label}"
                )
            updated = empty_circuit(slice_label)
            message = f"recorded successor success for {goal['id']} slice {slice_label}"
        else:
            evidence = nonempty_string(args.root_cause_evidence, "root-cause evidence")
            assert evidence is not None
            updated = dict(current or empty_circuit(slice_label))
            updated["state"] = "closed"
            updated["claimed_by"] = None
            updated["last_reset_evidence"] = evidence
            updated["last_reset_at"] = utc_now()
            message = f"reset recovery for {goal['id']} slice {slice_label}"
        if current_index is None:
            circuits.append(updated)
        else:
            circuits[current_index] = updated
    else:
        raise LedgerError(f"unsupported mutation: {args.command}")

    touch(ledger, goal)
    return ledger, message
