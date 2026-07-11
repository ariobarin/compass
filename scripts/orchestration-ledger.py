#!/usr/bin/env python3
"""Maintain compact local orchestration state under Compass .local storage."""

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
ITEM_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
STATES = {"planned", "active", "waiting", "blocked", "review", "complete", "cancelled"}
GATE_STATES = {"closed", "open", "blocked"}
EVIDENCE_KINDS = {"command", "check", "review", "artifact", "status", "decision"}
TRANSITIONS = {
    "planned": {"active", "cancelled"},
    "active": {"waiting", "blocked", "review", "complete", "cancelled"},
    "waiting": {"active", "blocked", "cancelled"},
    "blocked": {"active", "waiting", "cancelled"},
    "review": {"active", "blocked", "complete", "cancelled"},
    "complete": set(),
    "cancelled": set(),
}
MAX_EVIDENCE = 100


class LedgerError(ValueError):
    """The requested ledger operation would produce ambiguous or invalid state."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_timestamp(value: str | None, label: str, *, allow_none: bool = True) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not value.strip():
        raise LedgerError(f"{label} must be an ISO 8601 timestamp")
    text = value.strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise LedgerError(f"{label} must be an ISO 8601 timestamp: {value}") from error
    if parsed.tzinfo is None:
        raise LedgerError(f"{label} must include a timezone: {value}")
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require_text(value: object, label: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LedgerError(f"{label} must be a non-empty string")
    normalized = re.sub(r"\s+", " ", value).strip()
    if len(normalized) > limit:
        raise LedgerError(f"{label} exceeds {limit} characters")
    return normalized


def optional_text(value: object, label: str, limit: int) -> str | None:
    if value is None:
        return None
    return require_text(value, label, limit)


def default_ledger_path(root: Path) -> Path:
    return root / ".local" / "orchestration-ledger.json"


def resolve_ledger_path(root: Path, value: Path | None) -> Path:
    root = root.resolve()
    path = (value.expanduser() if value else default_ledger_path(root)).resolve()
    try:
        relative = path.relative_to(root)
    except ValueError:
        return path
    local_root = Path(".local")
    if relative != local_root and local_root not in relative.parents:
        raise LedgerError("a ledger inside the repository must stay under .local")
    return path


def empty_ledger() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "updated_at": utc_now(), "items": []}


def load_ledger(path: Path, *, allow_missing: bool = False) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        if allow_missing:
            return empty_ledger()
        raise LedgerError(f"ledger does not exist: {path}")
    except json.JSONDecodeError as error:
        raise LedgerError(
            f"ledger JSON is invalid at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error
    problems = validate_ledger(value)
    if problems:
        raise LedgerError("invalid ledger: " + "; ".join(problems))
    return value


def set_private_mode(path: Path, directory: bool) -> None:
    try:
        mode = stat.S_IRUSR | stat.S_IWUSR | (stat.S_IXUSR if directory else 0)
        path.chmod(mode)
    except OSError:
        pass


@contextmanager
def ledger_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    set_private_mode(path.parent, True)
    lock_path = path.with_name(path.name + ".lock")
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise LedgerError(f"ledger is locked by another writer: {lock_path}") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()}\ncreated_at={utc_now()}\n")
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def save_ledger(path: Path, ledger: dict[str, Any]) -> None:
    problems = validate_ledger(ledger)
    if problems:
        raise LedgerError("refusing to save invalid ledger: " + "; ".join(problems))
    path.parent.mkdir(parents=True, exist_ok=True)
    set_private_mode(path.parent, True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(ledger, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        set_private_mode(temp_path, False)
        os.replace(temp_path, path)
        set_private_mode(path, False)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def item_index(ledger: dict[str, Any], item_id: str) -> int:
    for index, item in enumerate(ledger["items"]):
        if item["id"] == item_id:
            return index
    raise LedgerError(f"unknown orchestration item: {item_id}")


def validate_item(item: object, index: int) -> list[str]:
    prefix = f"item {index}"
    if not isinstance(item, dict):
        return [f"{prefix} must be an object"]
    allowed = {
        "id", "goal", "repository", "execution_owner", "worker_id", "state",
        "next_action", "completion_evidence", "evidence", "public_mutation_gate",
        "decision_needed", "created_at", "updated_at",
    }
    problems: list[str] = []
    unknown = sorted(set(item) - allowed)
    if unknown:
        problems.append(f"{prefix} has unsupported fields: {', '.join(unknown)}")
    item_id = item.get("id")
    if not isinstance(item_id, str) or not ITEM_ID_RE.fullmatch(item_id):
        problems.append(f"{prefix} has invalid id")
    for field, limit in (("goal", 1000), ("execution_owner", 200)):
        value = item.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            problems.append(f"{prefix}.{field} must be a non-empty string up to {limit} characters")
    for field, limit in (("repository", 300), ("worker_id", 300)):
        value = item.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip() or len(value) > limit):
            problems.append(f"{prefix}.{field} must be null or a non-empty string up to {limit} characters")
    if item.get("state") not in STATES:
        problems.append(f"{prefix}.state is invalid")

    next_action = item.get("next_action")
    if next_action is not None:
        if not isinstance(next_action, dict) or set(next_action) != {"summary", "check_at"}:
            problems.append(f"{prefix}.next_action must be null or contain summary and check_at")
        else:
            summary = next_action.get("summary")
            if not isinstance(summary, str) or not summary.strip() or len(summary) > 1000:
                problems.append(f"{prefix}.next_action.summary is invalid")
            try:
                parse_timestamp(next_action.get("check_at"), f"{prefix}.next_action.check_at")
            except LedgerError as error:
                problems.append(str(error))

    completion = item.get("completion_evidence")
    if not isinstance(completion, list) or len(completion) > 50 or any(
        not isinstance(value, str) or not value.strip() or len(value) > 500 for value in completion
    ):
        problems.append(f"{prefix}.completion_evidence must be an array of up to 50 compact strings")

    evidence = item.get("evidence")
    if not isinstance(evidence, list) or len(evidence) > MAX_EVIDENCE:
        problems.append(f"{prefix}.evidence must be an array of up to {MAX_EVIDENCE} entries")
    else:
        for evidence_index, entry in enumerate(evidence, start=1):
            label = f"{prefix}.evidence {evidence_index}"
            if not isinstance(entry, dict) or set(entry) != {"recorded_at", "kind", "summary", "locator"}:
                problems.append(f"{label} has an invalid shape")
                continue
            if entry.get("kind") not in EVIDENCE_KINDS:
                problems.append(f"{label}.kind is invalid")
            if not isinstance(entry.get("summary"), str) or not entry["summary"].strip() or len(entry["summary"]) > 1000:
                problems.append(f"{label}.summary is invalid")
            locator = entry.get("locator")
            if locator is not None and (not isinstance(locator, str) or not locator.strip() or len(locator) > 1000):
                problems.append(f"{label}.locator is invalid")
            try:
                parse_timestamp(entry.get("recorded_at"), f"{label}.recorded_at", allow_none=False)
            except LedgerError as error:
                problems.append(str(error))

    gate = item.get("public_mutation_gate")
    if not isinstance(gate, dict) or set(gate) != {"state", "reason", "updated_at"}:
        problems.append(f"{prefix}.public_mutation_gate has an invalid shape")
    else:
        if gate.get("state") not in GATE_STATES:
            problems.append(f"{prefix}.public_mutation_gate.state is invalid")
        reason = gate.get("reason")
        if reason is not None and (not isinstance(reason, str) or not reason.strip() or len(reason) > 1000):
            problems.append(f"{prefix}.public_mutation_gate.reason is invalid")
        try:
            parse_timestamp(gate.get("updated_at"), f"{prefix}.public_mutation_gate.updated_at", allow_none=False)
        except LedgerError as error:
            problems.append(str(error))

    decision = item.get("decision_needed")
    if decision is not None:
        if not isinstance(decision, dict) or set(decision) != {"question", "options", "evidence", "requested_at"}:
            problems.append(f"{prefix}.decision_needed has an invalid shape")
        else:
            question = decision.get("question")
            options = decision.get("options")
            decision_evidence = decision.get("evidence")
            if not isinstance(question, str) or not question.strip() or len(question) > 1000:
                problems.append(f"{prefix}.decision_needed.question is invalid")
            if not isinstance(options, list) or not 2 <= len(options) <= 10 or len(options) != len(set(options)) or any(
                not isinstance(value, str) or not value.strip() or len(value) > 500 for value in options
            ):
                problems.append(f"{prefix}.decision_needed.options must contain 2 to 10 unique compact strings")
            if decision_evidence is not None and (
                not isinstance(decision_evidence, str) or not decision_evidence.strip() or len(decision_evidence) > 2000
            ):
                problems.append(f"{prefix}.decision_needed.evidence is invalid")
            try:
                parse_timestamp(decision.get("requested_at"), f"{prefix}.decision_needed.requested_at", allow_none=False)
            except LedgerError as error:
                problems.append(str(error))

    for field in ("created_at", "updated_at"):
        try:
            parse_timestamp(item.get(field), f"{prefix}.{field}", allow_none=False)
        except LedgerError as error:
            problems.append(str(error))
    return problems


def validate_ledger(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["ledger must be an object"]
    problems: list[str] = []
    if set(value) != {"schema_version", "updated_at", "items"}:
        problems.append("ledger must contain only schema_version, updated_at, and items")
    if value.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"ledger requires schema_version {SCHEMA_VERSION}")
    try:
        parse_timestamp(value.get("updated_at"), "ledger.updated_at", allow_none=False)
    except LedgerError as error:
        problems.append(str(error))
    items = value.get("items")
    if not isinstance(items, list):
        problems.append("ledger.items must be an array")
        return problems
    seen: set[str] = set()
    for index, item in enumerate(items, start=1):
        problems.extend(validate_item(item, index))
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            if item["id"] in seen:
                problems.append(f"duplicate item id: {item['id']}")
            seen.add(item["id"])
    return problems


def mutate(path: Path, operation) -> dict[str, Any]:
    with ledger_lock(path):
        ledger = load_ledger(path, allow_missing=True)
        result = operation(ledger)
        ledger["updated_at"] = utc_now()
        save_ledger(path, ledger)
        return result


def init_item(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    item_id = require_text(args.id, "id", 64)
    if not ITEM_ID_RE.fullmatch(item_id):
        raise LedgerError("id must be a lowercase slug using letters, numbers, dot, underscore, or hyphen")
    goal = require_text(args.goal, "goal", 1000)
    owner = require_text(args.execution_owner, "execution owner", 200)
    repository = optional_text(args.repository, "repository", 300)
    worker_id = optional_text(args.worker_id, "worker id", 300)
    completion = [require_text(value, "completion evidence", 500) for value in args.completion_evidence]
    now = utc_now()

    def apply(ledger: dict[str, Any]) -> dict[str, Any]:
        existing = next((item for item in ledger["items"] if item["id"] == item_id), None)
        if existing and not args.force:
            raise LedgerError(f"orchestration item already exists: {item_id}")
        item = {
            "id": item_id,
            "goal": goal,
            "repository": repository,
            "execution_owner": owner,
            "worker_id": worker_id,
            "state": "planned",
            "next_action": None,
            "completion_evidence": completion,
            "evidence": [],
            "public_mutation_gate": {"state": "closed", "reason": "not admitted", "updated_at": now},
            "decision_needed": None,
            "created_at": existing["created_at"] if existing else now,
            "updated_at": now,
        }
        if existing:
            ledger["items"][item_index(ledger, item_id)] = item
        else:
            ledger["items"].append(item)
        return item

    return mutate(path, apply)


def update_item(path: Path, item_id: str, change) -> dict[str, Any]:
    def apply(ledger: dict[str, Any]) -> dict[str, Any]:
        index = item_index(ledger, item_id)
        item = ledger["items"][index]
        change(item)
        item["updated_at"] = utc_now()
        ledger["items"][index] = item
        return item

    return mutate(path, apply)


def status(path: Path, item_id: str | None) -> dict[str, Any]:
    ledger = load_ledger(path, allow_missing=True)
    if item_id:
        return ledger["items"][item_index(ledger, item_id)]
    now = datetime.now(timezone.utc)
    overdue = 0
    for item in ledger["items"]:
        action = item.get("next_action")
        if not action or not action.get("check_at") or item["state"] in {"complete", "cancelled"}:
            continue
        check_at = datetime.fromisoformat(action["check_at"].replace("Z", "+00:00"))
        if check_at < now:
            overdue += 1
    counts = {state: 0 for state in sorted(STATES)}
    for item in ledger["items"]:
        counts[item["state"]] += 1
    return {
        "schema_version": SCHEMA_VERSION,
        "ledger": str(path),
        "updated_at": ledger["updated_at"],
        "summary": {
            "total": len(ledger["items"]),
            "states": counts,
            "decisions_needed": sum(item["decision_needed"] is not None for item in ledger["items"]),
            "open_public_gates": sum(item["public_mutation_gate"]["state"] == "open" for item in ledger["items"]),
            "overdue_checks": overdue,
        },
        "items": sorted(ledger["items"], key=lambda item: (item["updated_at"], item["id"]), reverse=True),
    }


def render_plain(value: dict[str, Any]) -> str:
    if "valid" in value:
        return f"valid={str(value['valid']).lower()} ledger={value['ledger']} items={value['items']}"
    if "items" not in value or "summary" not in value:
        action = value.get("next_action") or {}
        gate = value.get("public_mutation_gate") or {}
        return " ".join(
            [
                f"id={value.get('id')}",
                f"state={value.get('state')}",
                f"owner={value.get('execution_owner')}",
                f"worker={value.get('worker_id') or 'none'}",
                f"gate={gate.get('state')}",
                f"next={json.dumps(action.get('summary')) if action else 'none'}",
                f"decision={'yes' if value.get('decision_needed') else 'no'}",
            ]
        )
    lines = [
        f"ledger={value['ledger']}",
        f"total={value['summary']['total']}",
        f"decisions_needed={value['summary']['decisions_needed']}",
        f"open_public_gates={value['summary']['open_public_gates']}",
        f"overdue_checks={value['summary']['overdue_checks']}",
    ]
    for item in value["items"]:
        gate = item["public_mutation_gate"]["state"]
        next_summary = item["next_action"]["summary"] if item["next_action"] else "none"
        lines.append(
            f"item={item['id']} state={item['state']} owner={item['execution_owner']} "
            f"worker={item['worker_id'] or 'none'} gate={gate} decision={'yes' if item['decision_needed'] else 'no'} "
            f"next={json.dumps(next_summary)}"
        )
    return "\n".join(lines)


def emit(value: dict[str, Any], args: argparse.Namespace) -> None:
    if args.json:
        print(json.dumps(value, indent=2, sort_keys=True))
    elif args.plain:
        print(render_plain(value))
    else:
        if "valid" in value:
            print(f"orchestration ledger: valid ({value['items']} items)")
        elif "summary" in value and "items" in value:
            summary = value["summary"]
            print(f"orchestration items: {summary['total']}")
            print(f"decisions needed: {summary['decisions_needed']}")
            print(f"open public gates: {summary['open_public_gates']}")
            print(f"overdue checks: {summary['overdue_checks']}")
            for item in value["items"]:
                next_summary = item["next_action"]["summary"] if item["next_action"] else "none"
                print(
                    f"{item['id']}: {item['state']} owner={item['execution_owner']} "
                    f"gate={item['public_mutation_gate']['state']} next={next_summary}"
                )
        else:
            print(render_plain(value))


def add_common_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--plain", action="store_true")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ledger", type=Path)
    subparsers = parser.add_subparsers(dest="action", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--id")
    add_common_output_options(status_parser)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--id", required=True)
    init_parser.add_argument("--goal", required=True)
    init_parser.add_argument("--repository")
    init_parser.add_argument("--execution-owner", required=True)
    init_parser.add_argument("--worker-id")
    init_parser.add_argument("--completion-evidence", action="append", default=[])
    init_parser.add_argument("--force", action="store_true")
    add_common_output_options(init_parser)

    state_parser = subparsers.add_parser("set-state")
    state_parser.add_argument("--id", required=True)
    state_parser.add_argument("--state", choices=sorted(STATES), required=True)
    state_parser.add_argument("--force", action="store_true")
    add_common_output_options(state_parser)

    next_parser = subparsers.add_parser("set-next")
    next_parser.add_argument("--id", required=True)
    next_parser.add_argument("--summary", required=True)
    next_parser.add_argument("--check-at")
    add_common_output_options(next_parser)

    clear_next_parser = subparsers.add_parser("clear-next")
    clear_next_parser.add_argument("--id", required=True)
    add_common_output_options(clear_next_parser)

    evidence_parser = subparsers.add_parser("add-evidence")
    evidence_parser.add_argument("--id", required=True)
    evidence_parser.add_argument("--kind", choices=sorted(EVIDENCE_KINDS), required=True)
    evidence_parser.add_argument("--summary", required=True)
    evidence_parser.add_argument("--locator")
    add_common_output_options(evidence_parser)

    gate_parser = subparsers.add_parser("set-gate")
    gate_parser.add_argument("--id", required=True)
    gate_parser.add_argument("--state", choices=sorted(GATE_STATES), required=True)
    gate_parser.add_argument("--reason")
    add_common_output_options(gate_parser)

    decision_parser = subparsers.add_parser("set-decision")
    decision_parser.add_argument("--id", required=True)
    decision_parser.add_argument("--question", required=True)
    decision_parser.add_argument("--option", action="append", required=True)
    decision_parser.add_argument("--evidence")
    add_common_output_options(decision_parser)

    clear_decision_parser = subparsers.add_parser("clear-decision")
    clear_decision_parser.add_argument("--id", required=True)
    add_common_output_options(clear_decision_parser)

    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("--id", required=True)
    remove_parser.add_argument("--force", action="store_true")
    add_common_output_options(remove_parser)

    validate_parser = subparsers.add_parser("validate")
    add_common_output_options(validate_parser)

    args = parser.parse_args(argv)
    if getattr(args, "json", False) and getattr(args, "plain", False):
        parser.error("choose either --json or --plain")
    return args


def execute(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    path = resolve_ledger_path(root, args.ledger)
    if args.action == "status":
        return status(path, args.id)
    if args.action == "validate":
        ledger = load_ledger(path, allow_missing=True)
        return {"valid": True, "ledger": str(path), "items": len(ledger["items"])}
    if args.action == "init":
        return init_item(path, args)

    item_id = require_text(args.id, "id", 64)
    if not ITEM_ID_RE.fullmatch(item_id):
        raise LedgerError("id must be a lowercase slug using letters, numbers, dot, underscore, or hyphen")

    if args.action == "set-state":
        def change_state(item: dict[str, Any]) -> None:
            current = item["state"]
            target = args.state
            if target != current and target not in TRANSITIONS[current] and not args.force:
                raise LedgerError(f"state transition {current} -> {target} requires --force")
            item["state"] = target
        return update_item(path, item_id, change_state)

    if args.action == "set-next":
        summary = require_text(args.summary, "next action", 1000)
        check_at = parse_timestamp(args.check_at, "next check")
        return update_item(path, item_id, lambda item: item.__setitem__("next_action", {"summary": summary, "check_at": check_at}))

    if args.action == "clear-next":
        return update_item(path, item_id, lambda item: item.__setitem__("next_action", None))

    if args.action == "add-evidence":
        summary = require_text(args.summary, "evidence summary", 1000)
        locator = optional_text(args.locator, "evidence locator", 1000)
        def add_evidence(item: dict[str, Any]) -> None:
            if len(item["evidence"]) >= MAX_EVIDENCE:
                raise LedgerError(f"evidence limit reached ({MAX_EVIDENCE}); compress or remove the item")
            item["evidence"].append(
                {"recorded_at": utc_now(), "kind": args.kind, "summary": summary, "locator": locator}
            )
        return update_item(path, item_id, add_evidence)

    if args.action == "set-gate":
        reason = optional_text(args.reason, "gate reason", 1000)
        if args.state in {"open", "blocked"} and reason is None:
            raise LedgerError(f"gate state {args.state} requires --reason")
        gate = {"state": args.state, "reason": reason, "updated_at": utc_now()}
        return update_item(path, item_id, lambda item: item.__setitem__("public_mutation_gate", gate))

    if args.action == "set-decision":
        question = require_text(args.question, "decision question", 1000)
        options = [require_text(value, "decision option", 500) for value in args.option]
        if not 2 <= len(options) <= 10 or len(options) != len(set(options)):
            raise LedgerError("a decision needs 2 to 10 unique --option values")
        evidence = optional_text(args.evidence, "decision evidence", 2000)
        decision = {
            "question": question,
            "options": options,
            "evidence": evidence,
            "requested_at": utc_now(),
        }
        return update_item(path, item_id, lambda item: item.__setitem__("decision_needed", decision))

    if args.action == "clear-decision":
        return update_item(path, item_id, lambda item: item.__setitem__("decision_needed", None))

    if args.action == "remove":
        def remove_item(ledger: dict[str, Any]) -> dict[str, Any]:
            index = item_index(ledger, item_id)
            item = ledger["items"][index]
            if item["state"] not in {"complete", "cancelled"} and not args.force:
                raise LedgerError("remove requires a complete or cancelled item, or --force")
            return ledger["items"].pop(index)
        return mutate(path, remove_item)

    raise LedgerError(f"unsupported action: {args.action}")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = execute(args)
    except (LedgerError, OSError) as error:
        print(f"orchestration ledger failed: {error}", file=sys.stderr)
        return 1
    emit(result, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
