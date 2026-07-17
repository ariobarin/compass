from __future__ import annotations

from datetime import datetime
from typing import Any

from _orchestration_ledger_core import *


def validate_evidence(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be an object")
    check_unknown(
        value,
        {
            "kind",
            "summary",
            "locator",
            "producer",
            "observed_at",
            "verified_by",
            "recorded_at",
        },
        label,
    )
    kind = nonempty_string(value.get("kind"), f"{label}.kind")
    assert kind is not None
    if kind not in EVIDENCE_KINDS:
        raise LedgerError(f"{label}.kind must be one of: {', '.join(sorted(EVIDENCE_KINDS))}")
    return {
        "kind": kind,
        "summary": nonempty_string(value.get("summary"), f"{label}.summary"),
        "locator": nonempty_string(value.get("locator"), f"{label}.locator", nullable=True),
        "producer": nonempty_string(value.get("producer"), f"{label}.producer", nullable=True),
        "observed_at": parse_timestamp(value.get("observed_at"), f"{label}.observed_at"),
        "verified_by": nonempty_string(value.get("verified_by"), f"{label}.verified_by"),
        "recorded_at": parse_timestamp(value.get("recorded_at"), f"{label}.recorded_at"),
    }


def validate_decision(value: object, label: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be null or an object")
    check_unknown(value, {"question", "options", "prepared_at"}, label)
    options = string_list(value.get("options"), f"{label}.options", require_item=True)
    if len(options) < 2:
        raise LedgerError(f"{label}.options must contain at least two strings")
    return {
        "question": nonempty_string(value.get("question"), f"{label}.question"),
        "options": options,
        "prepared_at": parse_timestamp(value.get("prepared_at"), f"{label}.prepared_at"),
    }


def validate_recovery_circuit(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be an object")
    check_unknown(
        value,
        {
            "slice_label",
            "state",
            "assigned_worker",
            "last_failure_evidence",
            "last_failure_at",
            "last_reset_evidence",
            "last_reset_at",
        },
        label,
    )
    state = nonempty_string(value.get("state"), f"{label}.state")
    assert state is not None
    if state not in RECOVERY_STATES:
        raise LedgerError(f"{label}.state must be one of: {', '.join(sorted(RECOVERY_STATES))}")
    worker = nonempty_string(value.get("assigned_worker"), f"{label}.assigned_worker", nullable=True)
    if state == "active" and worker is None:
        raise LedgerError(f"{label}.active requires assigned_worker")
    if state in {"closed", "open"} and worker is not None:
        raise LedgerError(f"{label}.assigned_worker must be null when state is {state}")
    failure, failure_at = paired_optional_strings(
        value, "last_failure_evidence", "last_failure_at", label
    )
    reset, reset_at = paired_optional_strings(
        value, "last_reset_evidence", "last_reset_at", label
    )
    return {
        "slice_label": nonempty_string(value.get("slice_label"), f"{label}.slice_label"),
        "state": state,
        "assigned_worker": worker,
        "last_failure_evidence": failure,
        "last_failure_at": failure_at,
        "last_reset_evidence": reset,
        "last_reset_at": reset_at,
    }


def validate_recovery_circuits(value: object, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise LedgerError(f"{label} must be an array")
    circuits = [
        validate_recovery_circuit(item, f"{label}[{index}]")
        for index, item in enumerate(value)
    ]
    labels = [circuit["slice_label"] for circuit in circuits]
    if len(set(labels)) != len(labels):
        raise LedgerError(f"{label} slice_label values must be unique")
    return circuits


def migrate_evidence(item: object, writer: str, fallback_time: str) -> object:
    if not isinstance(item, dict):
        return item
    migrated = dict(item)
    recorded = migrated.get("recorded_at", fallback_time)
    migrated.setdefault("producer", None)
    migrated.setdefault("observed_at", recorded)
    migrated.setdefault("verified_by", writer)
    migrated.setdefault("recorded_at", recorded)
    return migrated


def migrate_circuit(item: object, fallback_time: str) -> object:
    if not isinstance(item, dict):
        return item
    migrated = dict(item)
    if "consecutive_successor_failures" in migrated:
        failures = migrated.pop("consecutive_successor_failures")
        migrated.setdefault(
            "last_failure_evidence",
            f"migrated successor failure count: {failures}" if failures else None,
        )
        migrated.setdefault("last_failure_at", fallback_time if failures else None)
        migrated.setdefault("last_reset_evidence", None)
        migrated.setdefault("last_reset_at", None)
    if migrated.get("state") == "claimed":
        migrated["state"] = "active"
    if "claimed_by" in migrated and "assigned_worker" not in migrated:
        migrated["assigned_worker"] = migrated.pop("claimed_by")
    migrated.setdefault("assigned_worker", None)
    return migrated


def migrate_goal(value: object, schema_version: int) -> object:
    if not isinstance(value, dict) or schema_version == SCHEMA_VERSION:
        return value
    goal = dict(value)
    updated = goal.get("updated_at") if isinstance(goal.get("updated_at"), str) else utc_now()
    writer = goal.get("control_writer") or goal.get("execution_owner") or "legacy-principal"
    if "recovery_circuit" in goal and "recovery_circuits" not in goal:
        goal["recovery_circuits"] = [goal.pop("recovery_circuit")]
    goal["recovery_circuits"] = [
        migrate_circuit(item, updated) for item in goal.get("recovery_circuits", [])
    ]
    legacy_evidence = goal.pop("completion_evidence", goal.get("evidence", []))
    goal["evidence"] = [migrate_evidence(item, str(writer), updated) for item in legacy_evidence]
    goal.setdefault("anchors", [])
    goal.setdefault("control_documents", [])
    goal.setdefault("phase", "planning" if goal.get("state") == "planned" else "implementation")
    goal.setdefault("control_writer", writer)
    goal.setdefault("control_revision", 1)
    goal.pop("control_edit_grants", None)
    goal.setdefault("last_verified_at", updated)
    return goal


def validate_goal(value: object, index: int) -> dict[str, Any]:
    label = f"goals[{index}]"
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be an object")
    allowed = {
        "id",
        "goal",
        "anchors",
        "control_documents",
        "phase",
        "execution_owner",
        "worker_id",
        "state",
        "next_action",
        "next_check_at",
        "evidence",
        "public_mutation_gate",
        "public_mutation_action",
        "decision_needed",
        "control_writer",
        "control_revision",
        "recovery_circuits",
        "created_at",
        "updated_at",
        "last_verified_at",
    }
    check_unknown(value, allowed, label)
    missing = sorted(field for field in allowed if field not in value)
    if missing:
        raise LedgerError(f"{label} is missing required fields: {', '.join(missing)}")

    state = nonempty_string(value.get("state"), f"{label}.state")
    assert state is not None
    if state not in STATES:
        raise LedgerError(f"{label}.state must be one of: {', '.join(sorted(STATES))}")
    phase = nonempty_string(value.get("phase"), f"{label}.phase")
    assert phase is not None
    if phase not in PHASES:
        raise LedgerError(f"{label}.phase must be one of: {', '.join(sorted(PHASES))}")
    gate = nonempty_string(value.get("public_mutation_gate"), f"{label}.public_mutation_gate")
    assert gate is not None
    if gate not in GATES:
        raise LedgerError(f"{label}.public_mutation_gate must be one of: {', '.join(sorted(GATES))}")
    gate_action = nonempty_string(
        value.get("public_mutation_action"), f"{label}.public_mutation_action", nullable=True
    )
    if gate == "closed" and gate_action is not None:
        raise LedgerError(f"{label}.public_mutation_action must be null when the gate is closed")
    if gate != "closed" and gate_action is None:
        raise LedgerError(f"{label}.public_mutation_action is required when the gate is {gate}")

    evidence_value = value.get("evidence")
    if not isinstance(evidence_value, list):
        raise LedgerError(f"{label}.evidence must be an array")
    evidence = [
        validate_evidence(item, f"{label}.evidence[{evidence_index}]")
        for evidence_index, item in enumerate(evidence_value)
    ]
    if state == "complete":
        if not evidence:
            raise LedgerError(f"{label}.state complete requires evidence")
        if value.get("next_action") is not None:
            raise LedgerError(f"{label}.state complete requires next_action null")
        if value.get("decision_needed") is not None:
            raise LedgerError(f"{label}.state complete requires decision_needed null")
    if gate == "complete" and not evidence:
        raise LedgerError(f"{label}.public_mutation_gate complete requires evidence")

    revision = value.get("control_revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise LedgerError(f"{label}.control_revision must be a positive integer")
    created = parse_timestamp(value.get("created_at"), f"{label}.created_at")
    updated = parse_timestamp(value.get("updated_at"), f"{label}.updated_at")
    verified = parse_timestamp(value.get("last_verified_at"), f"{label}.last_verified_at")
    assert created and updated and verified
    if datetime.fromisoformat(updated.replace("Z", "+00:00")) < datetime.fromisoformat(
        created.replace("Z", "+00:00")
    ):
        raise LedgerError(f"{label}.updated_at must not precede created_at")

    return {
        "id": validate_id(value.get("id"), f"{label}.id"),
        "goal": nonempty_string(value.get("goal"), f"{label}.goal"),
        "anchors": string_list(value.get("anchors"), f"{label}.anchors"),
        "control_documents": string_list(
            value.get("control_documents"), f"{label}.control_documents"
        ),
        "phase": phase,
        "execution_owner": nonempty_string(value.get("execution_owner"), f"{label}.execution_owner"),
        "worker_id": nonempty_string(value.get("worker_id"), f"{label}.worker_id", nullable=True),
        "state": state,
        "next_action": nonempty_string(value.get("next_action"), f"{label}.next_action", nullable=True),
        "next_check_at": parse_timestamp(
            value.get("next_check_at"), f"{label}.next_check_at", nullable=True
        ),
        "evidence": evidence,
        "public_mutation_gate": gate,
        "public_mutation_action": gate_action,
        "decision_needed": validate_decision(value.get("decision_needed"), f"{label}.decision_needed"),
        "control_writer": nonempty_string(value.get("control_writer"), f"{label}.control_writer"),
        "control_revision": revision,
        "recovery_circuits": validate_recovery_circuits(
            value.get("recovery_circuits"), f"{label}.recovery_circuits"
        ),
        "created_at": created,
        "updated_at": updated,
        "last_verified_at": verified,
    }


def validate_ledger(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError("ledger must be a JSON object")
    check_unknown(value, {"schema_version", "updated_at", "goals"}, "ledger")
    schema_version = value.get("schema_version")
    if (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, int)
        or schema_version not in LEGACY_SCHEMA_VERSIONS | {SCHEMA_VERSION}
    ):
        legacy = ", ".join(str(item) for item in sorted(LEGACY_SCHEMA_VERSIONS))
        raise LedgerError(
            f"ledger requires schema_version {SCHEMA_VERSION} "
            f"(legacy {legacy} is migrated on load)"
        )
    goals = value.get("goals")
    if not isinstance(goals, list):
        raise LedgerError("ledger.goals must be an array")
    normalized = [migrate_goal(goal, schema_version) for goal in goals]
    validated = [validate_goal(goal, index) for index, goal in enumerate(normalized)]
    ids = [goal["id"] for goal in validated]
    if len(ids) != len(set(ids)):
        raise LedgerError("ledger goal ids must be unique")
    return {
        "schema_version": SCHEMA_VERSION,
        "updated_at": parse_timestamp(value.get("updated_at"), "ledger.updated_at"),
        "goals": validated,
    }
