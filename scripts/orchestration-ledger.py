#!/usr/bin/env python3
"""Maintain a local-only orchestration control ledger under .local/."""

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

SCHEMA_VERSION = 2
LEGACY_SCHEMA_VERSION = 1
SUCCESSOR_FAILURE_THRESHOLD = 2
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
    cleaned_mutations = [nonempty_string(item, f"{label}.mutations") for item in mutations]
    assert all(item is not None for item in cleaned_mutations)
    allowed_mutations = MUTATION_COMMANDS if legacy else GRANTABLE_MUTATION_COMMANDS
    unsupported = sorted(set(cleaned_mutations) - allowed_mutations)
    if unsupported:
        raise LedgerError(
            f"{label}.mutations contains unsupported commands: {', '.join(unsupported)}"
        )
    if len(set(cleaned_mutations)) != len(cleaned_mutations):
        raise LedgerError(f"{label}.mutations must be unique")
    return {
        "actor": nonempty_string(value.get("actor"), f"{label}.actor"),
        "mutations": cleaned_mutations,
    }


def validate_recovery_circuit(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError(f"{label} must be an object")
    check_unknown(
        value,
        {
            "slice_label",
            "consecutive_successor_failures",
            "state",
            "last_reset_evidence",
            "last_reset_at",
            "claimed_by",
        },
        label,
    )
    failures = value.get("consecutive_successor_failures")
    if isinstance(failures, bool) or not isinstance(failures, int) or failures < 0:
        raise LedgerError(f"{label}.consecutive_successor_failures must be a non-negative integer")
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
    if failures >= SUCCESSOR_FAILURE_THRESHOLD and state != "open":
        raise LedgerError(
            f"{label}.state must be open after {SUCCESSOR_FAILURE_THRESHOLD} consecutive successor failures"
        )
    if state == "claimed" and failures >= SUCCESSOR_FAILURE_THRESHOLD:
        raise LedgerError(f"{label}.claimed cannot have two or more consecutive failures")
    last_reset_evidence = nonempty_string(
        value.get("last_reset_evidence"), f"{label}.last_reset_evidence", nullable=True
    )
    last_reset_at = parse_timestamp(
        value.get("last_reset_at"), f"{label}.last_reset_at", nullable=True
    )
    if (last_reset_evidence is None) != (last_reset_at is None):
        raise LedgerError(f"{label}.last_reset_evidence and last_reset_at must both be set or null")
    return {
        "slice_label": nonempty_string(value.get("slice_label"), f"{label}.slice_label"),
        "consecutive_successor_failures": failures,
        "state": state,
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
        value.get("control_writer", execution_owner), f"{label}.control_writer"
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
        value.get("recovery_circuits", []), f"{label}.recovery_circuits"
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
        "next_action": nonempty_string(
            value.get("next_action"), f"{label}.next_action", nullable=True
        ),
        "next_check_at": parse_timestamp(
            value.get("next_check_at"), f"{label}.next_check_at", nullable=True
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
    if schema_version not in {LEGACY_SCHEMA_VERSION, SCHEMA_VERSION}:
        raise LedgerError(
            f"ledger requires schema_version {SCHEMA_VERSION} (legacy {LEGACY_SCHEMA_VERSION} is migrated on load)"
        )
    goals = value.get("goals")
    if not isinstance(goals, list):
        raise LedgerError("ledger.goals must be an array")
    normalized_goals: list[object] = []
    for goal in goals:
        if isinstance(goal, dict) and "recovery_circuit" in goal and "recovery_circuits" not in goal:
            migrated_goal = dict(goal)
            migrated_goal["recovery_circuits"] = [migrated_goal.pop("recovery_circuit")]
            normalized_goals.append(migrated_goal)
        else:
            normalized_goals.append(goal)
    validated = [
        validate_goal(goal, index, legacy=schema_version == LEGACY_SCHEMA_VERSION)
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


def resolve_ledger_path(root: Path, raw: Path | None) -> tuple[Path, Path]:
    root = root.expanduser().resolve()
    local_root = root / ".local"
    candidate = raw.expanduser() if raw else Path(".local/orchestration-ledger.json")
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = Path(os.path.abspath(candidate))
    try:
        candidate.relative_to(local_root)
    except ValueError as error:
        raise LedgerError(f"ledger path must stay under {local_root}: {candidate}") from error

    cursor = root
    for part in candidate.relative_to(root).parts:
        cursor = cursor / part
        if cursor.exists() and cursor.is_symlink():
            raise LedgerError(f"ledger path must not traverse a symlink: {cursor}")
    return root, candidate


def load_ledger(path: Path, *, allow_missing: bool = False) -> dict[str, Any] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        if allow_missing:
            return None
        raise LedgerError(f"orchestration ledger is missing: {path}")
    except json.JSONDecodeError as error:
        raise LedgerError(
            f"invalid orchestration ledger at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error
    return validate_ledger(raw)


def set_private_mode(path: Path, directory: bool) -> None:
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR | (stat.S_IXUSR if directory else 0))
    except OSError:
        pass


@contextmanager
def ledger_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise LedgerError(f"ledger directory must not be a symlink: {path.parent}")
    set_private_mode(path.parent, True)
    lock_path = path.with_name(path.name + ".lock")
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise LedgerError(f"orchestration ledger is locked by another writer: {lock_path}") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()}\ncreated_at={utc_now()}\n")
            handle.flush()
            os.fsync(handle.fileno())
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def write_ledger(path: Path, ledger: dict[str, Any]) -> None:
    ledger = validate_ledger(ledger)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise LedgerError(f"ledger directory must not be a symlink: {path.parent}")
    set_private_mode(path.parent, True)
    payload = (json.dumps(ledger, indent=2, sort_keys=False) + "\n").encode("utf-8")
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        set_private_mode(temporary, False)
        os.replace(temporary, path)
        set_private_mode(path, False)
    finally:
        if temporary.exists():
            temporary.unlink()


def goal_by_id(ledger: dict[str, Any], goal_id: str) -> dict[str, Any]:
    for goal in ledger["goals"]:
        if goal["id"] == goal_id:
            return goal
    raise LedgerError(f"unknown goal id: {goal_id}")


def authorize_mutation(args: argparse.Namespace, goal: dict[str, Any]) -> None:
    actor = nonempty_string(getattr(args, "actor", None), "actor")
    expected_revision = getattr(args, "expected_revision", None)
    if isinstance(expected_revision, bool) or not isinstance(expected_revision, int):
        raise LedgerError("expected revision must be a positive integer")
    if expected_revision < 1:
        raise LedgerError("expected revision must be a positive integer")
    if expected_revision != goal["control_revision"]:
        raise LedgerError(
            f"stale control revision for {goal['id']}: expected {expected_revision}, current {goal['control_revision']}"
        )
    command = getattr(args, "command", None)
    if command in CONTROL_ONLY_MUTATIONS:
        if actor != goal["control_writer"]:
            raise LedgerError(f"only control writer may mutate {goal['id']} with {command}")
        return
    if actor == goal["control_writer"]:
        return
    for grant in goal["control_edit_grants"]:
        if grant["actor"] == actor and command in grant["mutations"]:
            return
    raise LedgerError(f"actor {actor} is not authorized to mutate {goal['id']} with {command}")


def touch(ledger: dict[str, Any], goal: dict[str, Any]) -> None:
    now = utc_now()
    goal["updated_at"] = now
    goal["control_revision"] += 1
    ledger["updated_at"] = now


def status_payload(path: Path, ledger: dict[str, Any] | None, goal_id: str | None) -> dict[str, Any]:
    if ledger is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "ledger": str(path),
            "present": False,
            "goals": [],
        }
    goals = ledger["goals"]
    if goal_id:
        goals = [goal_by_id(ledger, goal_id)]
    return {
        "schema_version": SCHEMA_VERSION,
        "ledger": str(path),
        "present": True,
        "updated_at": ledger["updated_at"],
        "goals": goals,
    }


def check_recovery(ledger: dict[str, Any], goal_id: str, slice_label: str) -> dict[str, Any]:
    goal = goal_by_id(ledger, validate_id(goal_id))
    label = nonempty_string(slice_label, "slice label")
    assert label is not None
    circuit = next(
        (circuit for circuit in goal["recovery_circuits"] if circuit["slice_label"] == label),
        None,
    )
    if circuit is not None and circuit["state"] == "open":
        raise LedgerError(
            f"recovery circuit is open for {goal['id']} slice {label}; observation reports no safe successor"
        )
    return circuit or {
        "slice_label": label,
        "consecutive_successor_failures": 0,
        "state": "closed",
    }


def render_status(payload: dict[str, Any], plain: bool) -> str:
    if not payload["present"]:
        return f"ledger={payload['ledger']} present=false" if plain else f"orchestration ledger absent: {payload['ledger']}"
    lines = [
        f"ledger={payload['ledger']} present=true goals={len(payload['goals'])}"
        if plain
        else f"orchestration ledger: {payload['ledger']} ({len(payload['goals'])} goals)"
    ]
    for goal in payload["goals"]:
        decision = goal["decision_needed"]
        if plain:
            lines.append(
                " ".join(
                    [
                        f"goal={goal['id']}",
                        f"state={goal['state']}",
                        f"owner={goal['execution_owner']}",
                        f"writer={goal['control_writer']}",
                        f"revision={goal['control_revision']}",
                        f"worker={goal['worker_id'] or 'none'}",
                        f"gate={goal['public_mutation_gate']}",
                        f"evidence={len(goal['completion_evidence'])}",
                        f"decision={'yes' if decision else 'no'}",
                    ]
                )
            )
        else:
            lines.append(
                f"{goal['id']}: {goal['state']} | owner {goal['execution_owner']} | "
                f"writer {goal['control_writer']} rev {goal['control_revision']} | "
                f"gate {goal['public_mutation_gate']}"
            )
            lines.append(f"  goal: {goal['goal']}")
            if goal["worker_id"]:
                lines.append(f"  worker: {goal['worker_id']}")
            if goal["public_mutation_action"]:
                lines.append(f"  public action: {goal['public_mutation_action']}")
            if goal["next_action"]:
                suffix = f" at {goal['next_check_at']}" if goal["next_check_at"] else ""
                lines.append(f"  next: {goal['next_action']}{suffix}")
            lines.append(f"  evidence: {len(goal['completion_evidence'])}")
            for circuit in goal["recovery_circuits"]:
                lines.append(
                    f"  recovery: {circuit['slice_label']} | "
                    f"successor failures {circuit['consecutive_successor_failures']} | {circuit['state']}"
                )
                if circuit["claimed_by"]:
                    lines.append(f"    claimed by: {circuit['claimed_by']}")
            if decision:
                lines.append(f"  decision: {decision['question']}")
                for option in decision["options"]:
                    lines.append(f"    - {option}")
    return "\n".join(lines)


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ledger", type=Path)


def add_mutation_auth_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--actor", "--control-actor", required=True)
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
    init.add_argument("--execution-owner", required=True)
    init.add_argument("--control-writer", "--writer")
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

    grant = subparsers.add_parser("set-grant", aliases=["set-control-grant"])
    add_mutation_auth_options(grant)
    grant.add_argument("--goal-id", required=True)
    grant.add_argument("--grant-actor", "--granted-actor", required=True)
    grant.add_argument(
        "--mutation",
        "--command",
        "--edit",
        "--grant-mutation",
        dest="mutations",
        action="append",
        required=True,
    )

    clear_grant = subparsers.add_parser("clear-grant", aliases=["clear-control-grant"])
    add_mutation_auth_options(clear_grant)
    clear_grant.add_argument("--goal-id", required=True)
    clear_grant.add_argument("--grant-actor", "--granted-actor", required=True)

    claim = subparsers.add_parser("claim-successor")
    add_mutation_auth_options(claim)
    claim.add_argument("--goal-id", required=True)
    claim.add_argument("--slice-label", required=True)

    failure = subparsers.add_parser("record-successor-failure")
    add_mutation_auth_options(failure)
    failure.add_argument("--goal-id", required=True)
    failure.add_argument("--slice-label", required=True)

    success = subparsers.add_parser("record-successor-success")
    add_mutation_auth_options(success)
    success.add_argument("--goal-id", required=True)
    success.add_argument("--slice-label", required=True)

    reset = subparsers.add_parser("reset-recovery")
    add_mutation_auth_options(reset)
    reset.add_argument("--goal-id", required=True)
    reset.add_argument("--slice-label", required=True)
    reset.add_argument(
        "--root-cause-evidence",
        "--root-cause-evidence-locator",
        "--evidence-locator",
        required=True,
    )

    check_recovery = subparsers.add_parser("check-recovery")
    check_recovery.add_argument("--goal-id", required=True)
    check_recovery.add_argument("--slice-label", required=True)
    check_recovery.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    args.command = {
        "set-control-grant": "set-grant",
        "clear-control-grant": "clear-grant",
    }.get(args.command, args.command)
    if getattr(args, "json", False) and getattr(args, "plain", False):
        parser.error("choose either --json or --plain")
    if args.command == "init" and (args.control_revision is None or args.control_revision < 1):
        parser.error("--control-revision must be a positive integer")
    return args


def mutate(args: argparse.Namespace, path: Path) -> tuple[dict[str, Any], str]:
    existing = load_ledger(path, allow_missing=True)
    if args.command == "init":
        goal_id = validate_id(args.goal_id)
        ledger = existing or {"schema_version": SCHEMA_VERSION, "updated_at": utc_now(), "goals": []}
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
                args.action, "public mutation action"
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
            raise LedgerError(
                f"grant mutations contain unsupported commands: {', '.join(unsupported)}"
            )
        if len(set(mutations)) != len(mutations):
            raise LedgerError("grant mutations must be unique")
        goal["control_edit_grants"] = [
            grant for grant in goal["control_edit_grants"] if grant["actor"] != grant_actor
        ]
        goal["control_edit_grants"].append({"actor": grant_actor, "mutations": mutations})
        message = f"set control edit grant for {grant_actor} on {goal['id']}"
    elif args.command == "clear-grant":
        grant_actor = nonempty_string(args.grant_actor, "grant actor")
        before = len(goal["control_edit_grants"])
        goal["control_edit_grants"] = [
            grant for grant in goal["control_edit_grants"] if grant["actor"] != grant_actor
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
            updated = current or {
                "slice_label": slice_label,
                "consecutive_successor_failures": 0,
                "state": "closed",
                "last_reset_evidence": None,
                "last_reset_at": None,
            }
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
            updated = dict(current)
            updated["consecutive_successor_failures"] += 1
            updated["state"] = (
                "open"
                if updated["consecutive_successor_failures"] >= SUCCESSOR_FAILURE_THRESHOLD
                else "closed"
            )
            updated["claimed_by"] = None
            message = f"recorded successor failure for {goal['id']} slice {slice_label}"
        elif args.command == "record-successor-success":
            if current is None or current["state"] != "claimed":
                raise LedgerError(f"slice {slice_label} must be claimed before recording success")
            if current["claimed_by"] != args.actor:
                raise LedgerError(
                    f"actor {args.actor} does not own the claim for slice {slice_label}"
                )
            updated = dict(current)
            updated["consecutive_successor_failures"] = 0
            updated["state"] = "closed"
            updated["claimed_by"] = None
            message = f"recorded successor success for {goal['id']} slice {slice_label}"
        else:
            evidence = nonempty_string(args.root_cause_evidence, "root-cause evidence")
            assert evidence is not None
            updated = current or {
                "slice_label": slice_label,
                "consecutive_successor_failures": 0,
                "state": "closed",
                "last_reset_evidence": None,
                "last_reset_at": None,
            }
            updated = dict(updated)
            updated["consecutive_successor_failures"] = 0
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
                print(json.dumps({"valid": True, "ledger": str(path), "goals": len(ledger["goals"])}, indent=2))
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
                    f"recovery observation passed for {args.goal_id} slice {circuit['slice_label']} "
                    f"({circuit['state']}, {circuit['consecutive_successor_failures']} consecutive failures)"
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


if __name__ == "__main__":
    raise SystemExit(main())
