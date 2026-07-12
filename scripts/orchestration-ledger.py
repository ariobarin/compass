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

SCHEMA_VERSION = 1
STATES = {"planned", "active", "waiting", "blocked", "complete", "cancelled"}
GATES = {"closed", "authorized", "in_flight", "complete"}
EVIDENCE_KINDS = {"test", "artifact", "review", "runtime", "decision", "other"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


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


def validate_goal(value: object, index: int) -> dict[str, Any]:
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
        "created_at",
        "updated_at",
    }
    check_unknown(value, allowed, label)
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
        "execution_owner": nonempty_string(
            value.get("execution_owner"), f"{label}.execution_owner"
        ),
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
        "created_at": created,
        "updated_at": updated,
    }


def validate_ledger(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError("ledger must be a JSON object")
    check_unknown(value, {"schema_version", "updated_at", "goals"}, "ledger")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise LedgerError(f"ledger requires schema_version {SCHEMA_VERSION}")
    goals = value.get("goals")
    if not isinstance(goals, list):
        raise LedgerError("ledger.goals must be an array")
    validated = [validate_goal(goal, index) for index, goal in enumerate(goals)]
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
        raw = json.loads(path.read_text(encoding="utf-8"))
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


def touch(ledger: dict[str, Any], goal: dict[str, Any]) -> None:
    now = utc_now()
    goal["updated_at"] = now
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
                        f"worker={goal['worker_id'] or 'none'}",
                        f"gate={goal['public_mutation_gate']}",
                        f"evidence={len(goal['completion_evidence'])}",
                        f"decision={'yes' if decision else 'no'}",
                    ]
                )
            )
        else:
            lines.append(f"{goal['id']}: {goal['state']} | owner {goal['execution_owner']} | gate {goal['public_mutation_gate']}")
            lines.append(f"  goal: {goal['goal']}")
            if goal["worker_id"]:
                lines.append(f"  worker: {goal['worker_id']}")
            if goal["public_mutation_action"]:
                lines.append(f"  public action: {goal['public_mutation_action']}")
            if goal["next_action"]:
                suffix = f" at {goal['next_check_at']}" if goal["next_check_at"] else ""
                lines.append(f"  next: {goal['next_action']}{suffix}")
            lines.append(f"  evidence: {len(goal['completion_evidence'])}")
            if decision:
                lines.append(f"  decision: {decision['question']}")
                for option in decision["options"]:
                    lines.append(f"    - {option}")
    return "\n".join(lines)


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ledger", type=Path)


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
    init.add_argument("--worker-id")
    init.add_argument("--state", choices=sorted(STATES), default="planned")

    owner = subparsers.add_parser("set-owner")
    owner.add_argument("--goal-id", required=True)
    owner.add_argument("--execution-owner", required=True)
    worker_group = owner.add_mutually_exclusive_group()
    worker_group.add_argument("--worker-id")
    worker_group.add_argument("--clear-worker", action="store_true")

    state = subparsers.add_parser("set-state")
    state.add_argument("--goal-id", required=True)
    state.add_argument("--state", choices=sorted(STATES), required=True)

    next_parser = subparsers.add_parser("set-next")
    next_parser.add_argument("--goal-id", required=True)
    next_group = next_parser.add_mutually_exclusive_group(required=True)
    next_group.add_argument("--action")
    next_group.add_argument("--clear", action="store_true")
    next_parser.add_argument("--check-at")

    evidence = subparsers.add_parser("add-evidence")
    evidence.add_argument("--goal-id", required=True)
    evidence.add_argument("--kind", choices=sorted(EVIDENCE_KINDS), required=True)
    evidence.add_argument("--summary", required=True)
    evidence.add_argument("--locator")

    gate = subparsers.add_parser("set-gate")
    gate.add_argument("--goal-id", required=True)
    gate.add_argument("--gate", choices=sorted(GATES), required=True)
    gate.add_argument("--action")

    decision = subparsers.add_parser("set-decision")
    decision.add_argument("--goal-id", required=True)
    decision.add_argument("--question", required=True)
    decision.add_argument("--option", action="append", required=True)

    clear_decision = subparsers.add_parser("clear-decision")
    clear_decision.add_argument("--goal-id", required=True)

    args = parser.parse_args(argv)
    if getattr(args, "json", False) and getattr(args, "plain", False):
        parser.error("choose either --json or --plain")
    return args


def mutate(args: argparse.Namespace, path: Path) -> tuple[dict[str, Any], str]:
    existing = load_ledger(path, allow_missing=True)
    if args.command == "init":
        goal_id = validate_id(args.goal_id)
        ledger = existing or {"schema_version": SCHEMA_VERSION, "updated_at": utc_now(), "goals": []}
        if any(goal["id"] == goal_id for goal in ledger["goals"]):
            raise LedgerError(f"goal already exists: {goal_id}")
        now = utc_now()
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
