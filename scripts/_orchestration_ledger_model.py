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

def validate_goal(value: object, index: int, *, legacy: bool = False) -> dict[str, Any]:
    label = f"goals[{index}]"
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be an object")
    allowed = {
        "id",
        "goal",
        "execution_owner",
        "worker_id",
        "state",
        "next_action",
        "next_check_at",
        "completion_evidence",
        "public_mutation_gate",
        "public_mutation_action",
        "decision_needed",
        "control_writer",
        "control_revision",
        "control_edit_grants",
        "recovery_circuits",
        "created_at",
        "updated_at",
    }
    check_unknown(value, allowed, label)
    if not legacy:
        missing = sorted(
            field
            for field in (
                "control_writer",
                "control_revision",
                "control_edit_grants",
                "recovery_circuits",
            )
            if field not in value
        )
        if missing:
            raise LedgerError(f"{label} is missing required control fields: {', '.join(missing)}")
    state = nonempty_string(value.get("state"), f"{label}.state")
    assert state is not None
    if state not in STATES:
        raise LedgerError(f"{label}.state must be one of: {', '.join(sorted(STATES))}")
    gate = nonempty_string(value.get("public_mutation_gate"), f"{label}.public_mutation_gate")
    assert gate is not None
    if gate not in GATES:
        raise LedgerError(f"{label}.public_mutation_gate must be one of: {', '.join(sorted(GATES))}")
    gate_action = nonempty_string(
        value.get("public_mutation_action"),
        f"{label}.public_mutation_action",
        nullable=True,
    )
    if gate == "closed" and gate_action is not None:
        raise LedgerError(f"{label}.public_mutation_action must be null when the gate is closed")
    if gate != "closed" and gate_action is None:
        raise LedgerError(f"{label}.public_mutation_action is required when the gate is {gate}")
    evidence = value.get("completion_evidence")
    if not isinstance(evidence, list):
        raise LedgerError(f"{label}.completion_evidence must be an array")
    if state == "complete":
        if not evidence:
            raise LedgerError(f"{label}.state complete requires completion evidence")
        if value.get("next_action") is not None:
            raise LedgerError(f"{label}.state complete requires next_action null")
        if value.get("decision_needed") is not None:
            raise LedgerError(f"{label}.state complete requires decision_needed null")
    if gate == "complete" and not evidence:
        raise LedgerError(f"{label}.public_mutation_gate complete requires completion evidence")
    execution_owner = nonempty_string(value.get("execution_owner"), f"{label}.execution_owner")
    control_writer = nonempty_string(
        value.get("control_writer", execution_owner),
        f"{label}.control_writer",
    )
    control_revision = value.get("control_revision", 1)
    if isinstance(control_revision, bool) or not isinstance(control_revision, int) or control_revision < 1:
        raise LedgerError(f"{label}.control_revision must be a positive integer")
    raw_grants = value.get("control_edit_grants", [])
    if not isinstance(raw_grants, list):
        raise LedgerError(f"{label}.control_edit_grants must be an array")
    grants = [
        validate_control_grant(
            item,
            f"{label}.control_edit_grants[{grant_index}]",
            legacy=legacy,
        )
        for grant_index, item in enumerate(raw_grants)
    ]
    grant_actors = [grant["actor"] for grant in grants]
    if len(set(grant_actors)) != len(grant_actors):
        raise LedgerError(f"{label}.control_edit_grants actors must be unique")
    recovery_circuits = validate_recovery_circuits(
        value.get("recovery_circuits", []),
        f"{label}.recovery_circuits",
    )
    created = parse_timestamp(value.get("created_at"), f"{label}.created_at")
    updated = parse_timestamp(value.get("updated_at"), f"{label}.updated_at")
    assert created and updated
    if datetime.fromisoformat(updated.replace("Z", "+00:00")) < datetime.fromisoformat(
        created.replace("Z", "+00:00")
    ):
        raise LedgerError(f"{label}.updated_at must not precede created_at")
    return {
        "id": validate_id(value.get("id"), f"{label}.id"),
        "goal": nonempty_string(value.get("goal"), f"{label}.goal"),
        "execution_owner": execution_owner,
        "worker_id": nonempty_string(value.get("worker_id"), f"{label}.worker_id", nullable=True),
        "state": state,
        "next_action": nonempty_string(value.get("next_action"), f"{label}.next_action", nullable=True),
        "next_check_at": parse_timestamp(
            value.get("next_check_at"),
            f"{label}.next_check_at",
            nullable=True,
        ),
        "completion_evidence": [
            validate_evidence(item, f"{label}.completion_evidence[{evidence_index}]")
            for evidence_index, item in enumerate(evidence)
        ],
        "public_mutation_gate": gate,
        "public_mutation_action": gate_action,
        "decision_needed": validate_decision(value.get("decision_needed"), f"{label}.decision_needed"),
        "control_writer": control_writer,
        "control_revision": control_revision,
        "control_edit_grants": grants,
        "recovery_circuits": recovery_circuits,
        "created_at": created,
        "updated_at": updated,
    }

def validate_ledger(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError("ledger must be a JSON object")
    check_unknown(value, {"schema_version", "updated_at", "goals"}, "ledger")
    schema_version = value.get("schema_version")
    if schema_version not in LEGACY_SCHEMA_VERSIONS | {SCHEMA_VERSION}:
        legacy_text = ", ".join(str(item) for item in sorted(LEGACY_SCHEMA_VERSIONS))
        raise LedgerError(
            f"ledger requires schema_version {SCHEMA_VERSION} "
            f"(legacy {legacy_text} is migrated on load)"
        )
    goals = value.get("goals")
    if not isinstance(goals, list):
        raise LedgerError("ledger.goals must be an array")
    normalized_goals: list[object] = []
    for raw_goal in goals:
        if not isinstance(raw_goal, dict):
            normalized_goals.append(raw_goal)
            continue
        goal = dict(raw_goal)
        if "recovery_circuit" in goal and "recovery_circuits" not in goal:
            goal["recovery_circuits"] = [goal.pop("recovery_circuit")]
        if schema_version in LEGACY_SCHEMA_VERSIONS:
            updated_at = goal.get("updated_at")
            if isinstance(updated_at, str):
                goal["recovery_circuits"] = [
                    migrate_recovery_circuit(item, updated_at)
                    for item in goal.get("recovery_circuits", [])
                ]
        normalized_goals.append(goal)
    validated = [
        validate_goal(goal, index, legacy=schema_version in LEGACY_SCHEMA_VERSIONS)
        for index, goal in enumerate(normalized_goals)
    ]
    ids = [goal["id"] for goal in validated]
    if len(set(ids)) != len(ids):
        raise LedgerError("ledger goal ids must be unique")
    return {
        "schema_version": SCHEMA_VERSION,
        "updated_at": parse_timestamp(value.get("updated_at"), "ledger.updated_at"),
        "goals": validated,
    }
