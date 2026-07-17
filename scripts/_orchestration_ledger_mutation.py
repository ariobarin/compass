from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _orchestration_ledger_core import *
from _orchestration_ledger_model import validate_ledger
from _orchestration_ledger_storage import *


def circuit_index(circuits: list[dict[str, Any]], slice_label: str) -> int | None:
    return next(
        (index for index, item in enumerate(circuits) if item["slice_label"] == slice_label),
        None,
    )


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
        writer = nonempty_string(args.control_writer, "control writer")
        assert writer is not None
        ledger["goals"].append(
            {
                "id": goal_id,
                "goal": nonempty_string(args.goal, "goal"),
                "anchors": string_list(args.anchor, "anchors", require_item=True),
                "control_documents": string_list(
                    args.control_document, "control documents", require_item=True
                ),
                "phase": args.phase,
                "execution_owner": nonempty_string(args.execution_owner, "execution owner"),
                "worker_id": nonempty_string(args.worker_id, "worker id", nullable=True),
                "state": args.state,
                "next_action": None,
                "next_check_at": None,
                "evidence": [],
                "public_mutation_gate": "closed",
                "public_mutation_action": None,
                "decision_needed": None,
                "control_writer": writer,
                "control_revision": args.control_revision,
                "recovery_circuits": [],
                "created_at": now,
                "updated_at": now,
                "last_verified_at": now,
            }
        )
        ledger["updated_at"] = now
        return validate_ledger(ledger), f"initialized goal {goal_id} for principal {writer}"

    if existing is None:
        raise LedgerError(f"orchestration ledger is missing: {path}")
    ledger = existing
    goal = goal_by_id(ledger, validate_id(args.goal_id))
    actor = authorize_mutation(args, goal)

    if args.command == "set-owner":
        goal["execution_owner"] = nonempty_string(args.execution_owner, "execution owner")
        if args.clear_worker:
            goal["worker_id"] = None
        elif args.worker_id is not None:
            goal["worker_id"] = nonempty_string(args.worker_id, "worker id")
        message = f"set {goal['id']} execution owner"
    elif args.command == "set-phase":
        goal["phase"] = args.phase
        message = f"set {goal['id']} phase to {args.phase}"
    elif args.command == "set-links":
        goal["anchors"] = string_list(args.anchor, "anchors", require_item=True)
        goal["control_documents"] = string_list(
            args.control_document, "control documents", require_item=True
        )
        message = f"set {goal['id']} anchors and control documents"
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
        now = utc_now()
        observed = parse_timestamp(args.observed_at, "observed at", nullable=True) or now
        goal["evidence"].append(
            {
                "kind": args.kind,
                "summary": nonempty_string(args.summary, "evidence summary"),
                "locator": nonempty_string(args.locator, "evidence locator", nullable=True),
                "producer": nonempty_string(args.producer, "evidence producer", nullable=True),
                "observed_at": observed,
                "verified_by": actor,
                "recorded_at": now,
            }
        )
        goal["last_verified_at"] = max(
            item["observed_at"] for item in goal["evidence"]
        )
        message = f"added principal-verified evidence to {goal['id']}"
    elif args.command == "set-gate":
        goal["public_mutation_gate"] = args.gate
        if args.gate == "closed":
            if args.action is not None:
                raise LedgerError("--action is not allowed when closing the public mutation gate")
            goal["public_mutation_action"] = None
        else:
            goal["public_mutation_action"] = nonempty_string(args.action, "public mutation action")
        message = f"set {goal['id']} public mutation gate to {args.gate}"
    elif args.command == "set-decision":
        options = string_list(args.option, "decision options", require_item=True)
        if len(options) < 2:
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
    elif args.command in {
        "begin-recovery",
        "record-recovery-failure",
        "record-recovery-success",
        "reset-recovery",
    }:
        circuits = goal["recovery_circuits"]
        label = nonempty_string(args.slice_label, "slice label")
        assert label is not None
        index = circuit_index(circuits, label)
        current = circuits[index] if index is not None else None
        if args.command == "begin-recovery":
            if current is not None and current["state"] == "open":
                raise LedgerError(f"recovery circuit is open for slice {label}")
            if current is not None and current["state"] == "active":
                raise LedgerError(f"recovery is already active for slice {label}")
            updated = dict(current or empty_circuit(label))
            updated["state"] = "active"
            updated["assigned_worker"] = nonempty_string(args.worker_id, "worker id")
            message = f"began recovery for {goal['id']} slice {label}"
        elif args.command == "record-recovery-failure":
            if current is None or current["state"] != "active":
                raise LedgerError(f"slice {label} must be active before recording failure")
            updated = dict(current)
            updated["last_failure_evidence"] = nonempty_string(
                args.failure_evidence, "failure evidence"
            )
            updated["last_failure_at"] = utc_now()
            updated["assigned_worker"] = None
            if args.no_new_evidence:
                updated["state"] = "open"
                updated["last_reset_evidence"] = None
                updated["last_reset_at"] = None
            else:
                updated["state"] = "closed"
                updated["last_reset_evidence"] = nonempty_string(
                    args.discriminating_evidence, "discriminating evidence"
                )
                updated["last_reset_at"] = utc_now()
            message = f"recorded recovery failure for {goal['id']} slice {label}"
        elif args.command == "record-recovery-success":
            if current is None or current["state"] != "active":
                raise LedgerError(f"slice {label} must be active before recording success")
            updated = empty_circuit(label)
            message = f"recorded recovery success for {goal['id']} slice {label}"
        else:
            updated = dict(current or empty_circuit(label))
            updated["state"] = "closed"
            updated["assigned_worker"] = None
            updated["last_reset_evidence"] = nonempty_string(
                args.root_cause_evidence, "root-cause evidence"
            )
            updated["last_reset_at"] = utc_now()
            message = f"reset recovery for {goal['id']} slice {label}"
        if index is None:
            circuits.append(updated)
        else:
            circuits[index] = updated
    else:
        raise LedgerError(f"unsupported mutation: {args.command}")

    touch(ledger, goal)
    return validate_ledger(ledger), message
