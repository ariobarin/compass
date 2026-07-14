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

SCHEMA_VERSION = 3
LEGACY_SCHEMA_VERSIONS = {1, 2}
STATES = {"planned", "active", "waiting", "blocked", "complete", "cancelled"}
GATES = {"closed", "authorized", "in_flight", "complete"}
EVIDENCE_KINDS = {"test", "artifact", "review", "runtime", "decision", "other"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
MUTATION_COMMANDS = {
    "set-owner",
    "set-state",
    "set-next",
    "add-evidence",
    "set-gate",
    "set-decision",
    "clear-decision",
    "set-grant",
    "clear-grant",
    "claim-successor",
    "record-successor-failure",
    "record-successor-success",
    "reset-recovery",
}
GRANTABLE_MUTATION_COMMANDS = MUTATION_COMMANDS - {
    "set-grant",
    "clear-grant",
    "reset-recovery",
}
CONTROL_ONLY_MUTATIONS = {"set-grant", "clear-grant", "reset-recovery"}

class LedgerError(ValueError):
    """The requested ledger operation would violate the local control contract."""

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def parse_timestamp(value: object, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value.strip():
        raise LedgerError(f"{label} must be an ISO 8601 timestamp")
    normalized = value.strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as error:
        raise LedgerError(f"{label} must be an ISO 8601 timestamp: {normalized}") from error
    if parsed.tzinfo is None:
        raise LedgerError(f"{label} must include a timezone: {normalized}")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def nonempty_string(value: object, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value.strip():
        raise LedgerError(f"{label} must be a non-empty string")
    return value.strip()

def validate_id(value: object, label: str = "goal id") -> str:
    result = nonempty_string(value, label)
    assert result is not None
    if not ID_RE.fullmatch(result):
        raise LedgerError(f"{label} must match {ID_RE.pattern}: {result}")
    return result

def check_unknown(record: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise LedgerError(f"{label} has unsupported fields: {', '.join(unknown)}")

def validate_evidence(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be an object")
    check_unknown(value, {"kind", "summary", "locator", "recorded_at"}, label)
    kind = nonempty_string(value.get("kind"), f"{label}.kind")
    assert kind is not None
    if kind not in EVIDENCE_KINDS:
        raise LedgerError(f"{label}.kind must be one of: {', '.join(sorted(EVIDENCE_KINDS))}")
    return {
        "kind": kind,
        "summary": nonempty_string(value.get("summary"), f"{label}.summary"),
        "locator": nonempty_string(value.get("locator"), f"{label}.locator", nullable=True),
        "recorded_at": parse_timestamp(value.get("recorded_at"), f"{label}.recorded_at"),
    }

def validate_decision(value: object, label: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be null or an object")
    check_unknown(value, {"question", "options", "prepared_at"}, label)
    options = value.get("options")
    if not isinstance(options, list) or len(options) < 2:
        raise LedgerError(f"{label}.options must contain at least two strings")
    cleaned = [nonempty_string(item, f"{label}.options") for item in options]
    if len(set(cleaned)) != len(cleaned):
        raise LedgerError(f"{label}.options must be unique")
    return {
        "question": nonempty_string(value.get("question"), f"{label}.question"),
        "options": cleaned,
        "prepared_at": parse_timestamp(value.get("prepared_at"), f"{label}.prepared_at"),
    }

def validate_control_grant(value: object, label: str, *, legacy: bool = False) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be an object")
    check_unknown(value, {"actor", "mutations"}, label)
    mutations = value.get("mutations")
    if not isinstance(mutations, list) or not mutations:
        raise LedgerError(f"{label}.mutations must contain at least one command")
    cleaned = [nonempty_string(item, f"{label}.mutations") for item in mutations]
    assert all(item is not None for item in cleaned)
    allowed = MUTATION_COMMANDS if legacy else GRANTABLE_MUTATION_COMMANDS
    unsupported = sorted(set(cleaned) - allowed)
    if unsupported:
        raise LedgerError(f"{label}.mutations contains unsupported commands: {', '.join(unsupported)}")
    if len(set(cleaned)) != len(cleaned):
        raise LedgerError(f"{label}.mutations must be unique")
    return {
        "actor": nonempty_string(value.get("actor"), f"{label}.actor"),
        "mutations": cleaned,
    }

def paired_optional_strings(
    value: dict[str, Any],
    evidence_field: str,
    time_field: str,
    label: str,
) -> tuple[str | None, str | None]:
    evidence = nonempty_string(
        value.get(evidence_field),
        f"{label}.{evidence_field}",
        nullable=True,
    )
    recorded_at = parse_timestamp(
        value.get(time_field),
        f"{label}.{time_field}",
        nullable=True,
    )
    if (evidence is None) != (recorded_at is None):
        raise LedgerError(
            f"{label}.{evidence_field} and {label}.{time_field} must both be set or null"
        )
    return evidence, recorded_at

def migrate_recovery_circuit(value: object, goal_updated_at: str) -> object:
    if not isinstance(value, dict) or "consecutive_successor_failures" not in value:
        return value
    migrated = dict(value)
    failures = migrated.pop("consecutive_successor_failures")
    if isinstance(failures, bool) or not isinstance(failures, int) or failures < 0:
        return value
    migrated.setdefault(
        "last_failure_evidence",
        f"migrated successor failure count: {failures}" if failures else None,
    )
    migrated.setdefault("last_failure_at", goal_updated_at if failures else None)
    migrated.setdefault("last_reset_evidence", None)
    migrated.setdefault("last_reset_at", None)
    migrated.setdefault("claimed_by", None)
    return migrated

def validate_recovery_circuit(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be an object")
    check_unknown(
        value,
        {
            "slice_label",
            "state",
            "last_failure_evidence",
            "last_failure_at",
            "last_reset_evidence",
            "last_reset_at",
            "claimed_by",
        },
        label,
    )
    state = nonempty_string(value.get("state"), f"{label}.state")
    assert state is not None
    if state not in {"open", "claimed", "closed"}:
        raise LedgerError(f"{label}.state must be closed, claimed, or open")
    claimed_by_present = "claimed_by" in value
    claimed_by = nonempty_string(value.get("claimed_by"), f"{label}.claimed_by", nullable=True)
    if not claimed_by_present and state == "claimed":
        state = "open"
        claimed_by = None
    if state == "claimed" and claimed_by is None:
        raise LedgerError(f"{label}.claimed requires a non-empty claimed_by")
    if state in {"closed", "open"} and claimed_by is not None:
        raise LedgerError(f"{label}.claimed_by must be null when state is {state}")
    last_failure_evidence, last_failure_at = paired_optional_strings(
        value,
        "last_failure_evidence",
        "last_failure_at",
        label,
    )
    last_reset_evidence, last_reset_at = paired_optional_strings(
        value,
        "last_reset_evidence",
        "last_reset_at",
        label,
    )
    return {
        "slice_label": nonempty_string(value.get("slice_label"), f"{label}.slice_label"),
        "state": state,
        "last_failure_evidence": last_failure_evidence,
        "last_failure_at": last_failure_at,
        "last_reset_evidence": last_reset_evidence,
        "last_reset_at": last_reset_at,
        "claimed_by": claimed_by,
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
