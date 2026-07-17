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
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
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
    if isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision < 1:
        raise LedgerError("expected revision must be a positive integer")
    if expected_revision != goal["control_revision"]:
        raise LedgerError(
            f"stale control revision for {goal['id']}: "
            f"expected {expected_revision}, current {goal['control_revision']}"
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

def empty_circuit(slice_label: str) -> dict[str, Any]:
    return {
        "slice_label": slice_label,
        "state": "closed",
        "last_failure_evidence": None,
        "last_failure_at": None,
        "last_reset_evidence": None,
        "last_reset_at": None,
        "claimed_by": None,
    }

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
        goals = [goal_by_id(ledger, validate_id(goal_id))]
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
        (item for item in goal["recovery_circuits"] if item["slice_label"] == label),
        None,
    )
    if circuit is not None and circuit["state"] == "open":
        raise LedgerError(
            f"recovery circuit is open for {goal['id']} slice {label}; "
            "no new discriminating evidence supports another successor"
        )
    return circuit or empty_circuit(label)

def render_status(payload: dict[str, Any], plain: bool) -> str:
    if not payload["present"]:
        if plain:
            return f"ledger={payload['ledger']} present=false"
        return f"orchestration ledger absent: {payload['ledger']}"
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
            continue
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
            lines.append(f"  recovery: {circuit['slice_label']} | {circuit['state']}")
            if circuit["last_failure_evidence"]:
                lines.append(f"    last failure: {circuit['last_failure_evidence']}")
            if circuit["last_reset_evidence"]:
                lines.append(f"    resume evidence: {circuit['last_reset_evidence']}")
            if circuit["claimed_by"]:
                lines.append(f"    claimed by: {circuit['claimed_by']}")
        if decision:
            lines.append(f"  decision: {decision['question']}")
            for option in decision["options"]:
                lines.append(f"    - {option}")
    return "\n".join(lines)
