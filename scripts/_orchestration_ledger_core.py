from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = 4
LEGACY_SCHEMA_VERSIONS = {1, 2, 3}
STATES = {"planned", "active", "waiting", "blocked", "complete", "cancelled"}
PHASES = {"planning", "implementation"}
GATES = {"closed", "authorized", "in_flight", "complete"}
EVIDENCE_KINDS = {"test", "artifact", "review", "runtime", "decision", "other"}
RECOVERY_STATES = {"closed", "active", "open"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
MUTATION_COMMANDS = {
    "set-owner",
    "set-phase",
    "set-links",
    "set-state",
    "set-next",
    "add-evidence",
    "set-gate",
    "set-decision",
    "clear-decision",
    "begin-recovery",
    "record-recovery-failure",
    "record-recovery-success",
    "reset-recovery",
}


class LedgerError(ValueError):
    """The requested ledger operation would violate the control contract."""


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


def string_list(value: object, label: str, *, require_item: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise LedgerError(f"{label} must be an array")
    cleaned = [nonempty_string(item, f"{label} item") for item in value]
    assert all(item is not None for item in cleaned)
    result = [item for item in cleaned if item is not None]
    if require_item and not result:
        raise LedgerError(f"{label} requires at least one item")
    if len(result) != len(set(result)):
        raise LedgerError(f"{label} items must be unique")
    return result


def paired_optional_strings(
    value: dict[str, Any], evidence_field: str, time_field: str, label: str
) -> tuple[str | None, str | None]:
    evidence = nonempty_string(
        value.get(evidence_field), f"{label}.{evidence_field}", nullable=True
    )
    recorded_at = parse_timestamp(
        value.get(time_field), f"{label}.{time_field}", nullable=True
    )
    if (evidence is None) != (recorded_at is None):
        raise LedgerError(
            f"{label}.{evidence_field} and {label}.{time_field} must both be set or null"
        )
    return evidence, recorded_at
