#!/usr/bin/env python3
"""Export content-free structural metadata from supported Codex JSONL sessions."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import secrets
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

SCHEMA_VERSION = 2
SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$"
)
SENSITIVE_NAMES = {
    "auth.json",
    "credentials.json",
    "history.jsonl",
    "installation_id",
    ".env",
}
KNOWN_ROLES = {
    "root",
    "controller",
    "worker",
    "implementer",
    "reviewer",
    "verifier",
    "algorithm-critic",
    "neutral-critic",
    "repo-explorer",
    "research-critic",
    "reuse-critic",
}
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh"}
TIERS = {"auto", "default", "fast", "flex", "priority", "scale"}
FORK_MODES = {"none", "full", "compact", "fresh", "shared"}
TOOL_STATUSES = {"started", "success", "failure", "cancelled", "unknown"}
COMPACTION_REASONS = {"automatic", "manual", "context_limit", "unknown"}
TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
    "active_context_tokens",
    "tool_output_tokens",
    "forked_context_tokens",
    "pre_compaction_tokens",
    "post_compaction_tokens",
)
EVENT_FIELDS = (
    "seq",
    "kind",
    "timestamp",
    "actor_id",
    "parent_id",
    "operation_id",
    "child_ordinal",
    "role",
    "requested_model",
    "effective_model",
    "requested_reasoning_effort",
    "effective_reasoning_effort",
    "service_tier",
    "fork_mode",
    "tool_category",
    "tool_status",
    "duration_ms",
    "outcome",
    "failure_class",
    "compaction_reason",
    *TOKEN_FIELDS,
)


@dataclass(frozen=True)
class SourceRecords:
    path: Path
    records: list[tuple[int, dict[str, Any]]]
    bytes_read: int
    records_seen: int
    malformed: int
    warnings: list[dict[str, Any]]


class Pseudonymizer:
    """Create identifiers that are joinable only within one export invocation."""

    def __init__(self, salt: bytes | None = None) -> None:
        self._salt = salt or secrets.token_bytes(32)

    def value(self, namespace: str, raw: Any) -> str | None:
        if raw is None:
            return None
        text = str(raw)
        if not text:
            return None
        digest = hmac.new(
            self._salt,
            f"{namespace}\0{text}".encode("utf-8", errors="replace"),
            hashlib.sha256,
        ).hexdigest()[:20]
        return f"hmac256:{digest}"

    @property
    def export_id(self) -> str:
        value = self.value("export", "session-trace-v2")
        assert value is not None
        return value


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, float) and value >= 0 and value.is_integer():
        return int(value)
    return None


def safe_identifier(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value if SAFE_IDENTIFIER_RE.fullmatch(value) else None


def normalize_role(value: Any) -> str | None:
    value = safe_identifier(value)
    if value is None:
        return None
    lowered = value.lower()
    if lowered in KNOWN_ROLES:
        return lowered
    if "review" in lowered:
        return "reviewer"
    if "implement" in lowered or "worker" in lowered:
        return "worker"
    if "control" in lowered or "orchestrat" in lowered:
        return "controller"
    return "custom"


def normalize_choice(value: Any, allowed: set[str]) -> str | None:
    if not isinstance(value, str):
        return None
    lowered = value.strip().lower().replace(" ", "_")
    return lowered if lowered in allowed else None


def failure_class(*values: Any) -> str | None:
    text = " ".join(str(value).lower() for value in values if value is not None)
    if not text:
        return None
    mapping = (
        ("timeout", ("timeout", "timed out", "deadline")),
        ("cancelled", ("cancel", "abort", "interrupt")),
        ("permission", ("permission", "denied", "unauthorized", "forbidden")),
        ("validation", ("validation", "invalid", "schema", "assert")),
        ("rate_limit", ("rate", "429", "quota")),
        ("context_limit", ("context", "token limit", "too long")),
        ("tool_error", ("tool", "command", "exit code", "process")),
        ("runtime", ("runtime", "exception", "crash", "error")),
    )
    for label, terms in mapping:
        if any(term in text for term in terms):
            return label
    return "unknown"


def tool_category(item_type: Any) -> str | None:
    if not isinstance(item_type, str):
        return None
    lowered = item_type.lower()
    if any(term in lowered for term in ("command", "shell", "terminal", "exec")):
        return "shell"
    if any(term in lowered for term in ("file", "patch", "edit", "write")):
        return "file"
    if any(term in lowered for term in ("browser", "computer", "screenshot")):
        return "browser"
    if any(term in lowered for term in ("search", "web_search")):
        return "search"
    if any(term in lowered for term in ("function", "tool", "mcp", "connector")):
        return "connector"
    if any(term in lowered for term in ("message", "reasoning")):
        return None
    return "other"


def tool_status(record_type: str, item: dict[str, Any]) -> str:
    status = normalize_choice(item.get("status"), TOOL_STATUSES)
    if status:
        return status
    if record_type.endswith(".started"):
        return "started"
    if record_type.endswith(".failed"):
        return "failure"
    if record_type.endswith(".completed"):
        exit_code = item.get("exit_code")
        return "failure" if isinstance(exit_code, int) and exit_code != 0 else "success"
    return "unknown"


def tool_outcome(status: str) -> str:
    return {
        "started": "started",
        "success": "success",
        "failure": "failure",
        "cancelled": "cancelled",
    }.get(status, "unknown")


def compaction_reason(value: Any) -> str:
    normalized = normalize_choice(value, COMPACTION_REASONS)
    if normalized:
        return normalized
    if isinstance(value, str) and "limit" in value.lower():
        return "context_limit"
    return "unknown"


def timestamp(record: dict[str, Any]) -> str | None:
    value = record.get("timestamp")
    if isinstance(value, str) and TIMESTAMP_RE.fullmatch(value):
        return value
    return None


def nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def usage_fields(usage: Any) -> dict[str, int | None]:
    if not isinstance(usage, dict):
        return {field: None for field in TOKEN_FIELDS}
    return {
        "input_tokens": integer(usage.get("input_tokens")),
        "cached_input_tokens": integer(
            usage.get("cached_input_tokens", usage.get("cache_read_tokens"))
        ),
        "cache_write_tokens": integer(usage.get("cache_write_tokens")),
        "output_tokens": integer(usage.get("output_tokens")),
        "reasoning_tokens": integer(
            usage.get("reasoning_tokens", usage.get("reasoning_output_tokens"))
        ),
        "active_context_tokens": integer(usage.get("active_context_tokens")),
        "tool_output_tokens": integer(usage.get("tool_output_tokens")),
        "forked_context_tokens": integer(usage.get("forked_context_tokens")),
        "pre_compaction_tokens": integer(usage.get("pre_compaction_tokens")),
        "post_compaction_tokens": integer(usage.get("post_compaction_tokens")),
    }


def config_fields(config: dict[str, Any]) -> dict[str, Any]:
    requested_model = safe_identifier(
        config.get("requested_model", config.get("model_requested"))
    )
    effective_model = safe_identifier(
        config.get("effective_model", config.get("model"))
    )
    requested_effort = normalize_choice(
        config.get("requested_reasoning_effort", config.get("requested_effort")),
        EFFORTS,
    )
    effective_effort = normalize_choice(
        config.get(
            "effective_reasoning_effort",
            config.get("reasoning_effort", config.get("effort")),
        ),
        EFFORTS,
    )
    return {
        "role": normalize_role(config.get("role", config.get("agent_role"))),
        "requested_model": requested_model,
        "effective_model": effective_model,
        "requested_reasoning_effort": requested_effort,
        "effective_reasoning_effort": effective_effort,
        "service_tier": normalize_choice(config.get("service_tier"), TIERS),
        "fork_mode": normalize_choice(
            config.get("fork_mode", config.get("context_mode")), FORK_MODES
        ),
    }


def event(seq: int, kind: str, stamp: str | None, **values: Any) -> dict[str, Any]:
    result = {field: None for field in EVENT_FIELDS}
    result.update({"seq": seq, "kind": kind, "timestamp": stamp})
    for key, value in values.items():
        if key in result:
            result[key] = value
    return result


def event_with_config(
    seq: int,
    kind: str,
    stamp: str | None,
    config: dict[str, Any],
    **values: Any,
) -> dict[str, Any]:
    merged = config_fields(config)
    merged.update(values)
    return event(seq, kind, stamp, **merged)


def detect_parser(records: list[tuple[int, dict[str, Any]]]) -> str | None:
    for _, record in records:
        record_type = record.get("type")
        if not isinstance(record_type, str):
            continue
        if record_type.startswith(("thread.", "turn.", "item.")):
            return "codex-exec-json-v2"
        if record_type in {
            "session_meta",
            "turn_context",
            "event_msg",
            "response_item",
            "compacted",
        }:
            return "codex-rollout-v2"
    return None


def supported_record_count(
    records: Sequence[tuple[int, dict[str, Any]]], parser: str
) -> int:
    """Count records whose structural fields are understood by the parser."""

    supported = 0
    rollout_events = {
        "token_count",
        "task_started",
        "turn_started",
        "task_complete",
        "turn_complete",
        "task_failed",
        "turn_failed",
        "task_cancelled",
        "collab_agent_spawn_end",
        "agent_spawned",
        "collab_close_end",
        "agent_finished",
        "agent_failed",
    }
    for _, record in records:
        record_type = record.get("type")
        if parser == "codex-rollout-v2":
            if record_type in {"session_meta", "turn_context", "compacted"}:
                supported += 1
                continue
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue
            if record_type == "event_msg" and payload.get("type") in rollout_events:
                supported += 1
            elif record_type == "response_item" and tool_category(
                payload.get("type")
            ) is not None:
                supported += 1
            continue

        if record_type in {
            "thread.started",
            "turn.started",
            "turn.completed",
            "turn.failed",
        }:
            supported += 1
            continue
        if isinstance(record_type, str) and record_type.startswith("item."):
            item = record.get("item") if isinstance(record.get("item"), dict) else record
            if tool_category(item.get("type")) is not None:
                supported += 1
    return supported


def cumulative_delta(
    total: dict[str, Any] | None,
    last: dict[str, Any] | None,
    previous: dict[str, int],
) -> tuple[dict[str, int | None], dict[str, int]]:
    result = {field: None for field in TOKEN_FIELDS}
    next_previous = dict(previous)
    source_keys = {
        "input_tokens": "input_tokens",
        "cached_input_tokens": "cached_input_tokens",
        "cache_write_tokens": "cache_write_tokens",
        "output_tokens": "output_tokens",
        "reasoning_tokens": "reasoning_output_tokens",
    }
    for output_key, source_key in source_keys.items():
        total_value = integer(total.get(source_key)) if isinstance(total, dict) else None
        last_value = integer(last.get(source_key)) if isinstance(last, dict) else None
        prior = previous.get(source_key)
        if total_value is not None and prior is not None and total_value >= prior:
            result[output_key] = total_value - prior
        elif last_value is not None:
            result[output_key] = last_value
        else:
            result[output_key] = total_value
        if total_value is not None:
            next_previous[source_key] = total_value
    return result, next_previous


def parse_rollout(
    source: SourceRecords,
    pseudonyms: Pseudonymizer,
    source_index: int,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    warnings = list(source.warnings)
    config: dict[str, Any] = {"role": "root"}
    raw_session_id: Any = f"source-{source_index}"
    started_at: str | None = None
    ended_at: str | None = None
    previous_totals: dict[str, int] = {}
    child_ordinals: dict[str, int] = {}
    next_child_ordinal = 1

    def actor(raw: Any = None) -> str | None:
        return pseudonyms.value("actor", raw if raw is not None else raw_session_id)

    for line_number, record in source.records:
        record_type = record.get("type")
        payload = record.get("payload")
        if not isinstance(payload, dict):
            payload = {}
        stamp = timestamp(record)

        if record_type == "session_meta":
            raw_session_id = payload.get("id", raw_session_id)
            started_at = started_at or stamp
            config.update(payload)
            continue
        if record_type == "turn_context":
            config.update(payload)
            started_at = started_at or stamp
            continue
        if record_type == "event_msg":
            payload_type = payload.get("type")
            if payload_type == "token_count":
                info = payload.get("info") if isinstance(payload.get("info"), dict) else {}
                tokens, previous_totals = cumulative_delta(
                    info.get("total_token_usage")
                    if isinstance(info.get("total_token_usage"), dict)
                    else None,
                    info.get("last_token_usage")
                    if isinstance(info.get("last_token_usage"), dict)
                    else None,
                    previous_totals,
                )
                events.append(
                    event_with_config(
                        len(events) + 1,
                        "turn",
                        stamp,
                        config,
                        actor_id=actor(),
                        **tokens,
                    )
                )
                continue
            if payload_type in {"task_started", "turn_started"}:
                started_at = started_at or stamp
                events.append(
                    event_with_config(
                        len(events) + 1,
                        "session_boundary",
                        stamp,
                        config,
                        actor_id=actor(),
                        outcome="started",
                    )
                )
                continue
            if payload_type in {"task_complete", "turn_complete"}:
                ended_at = stamp or ended_at
                events.append(
                    event_with_config(
                        len(events) + 1,
                        "session_boundary",
                        stamp,
                        config,
                        actor_id=actor(),
                        outcome="success",
                    )
                )
                continue
            if payload_type in {"task_failed", "turn_failed", "task_cancelled"}:
                ended_at = stamp or ended_at
                outcome = "cancelled" if "cancel" in str(payload_type) else "failure"
                events.append(
                    event_with_config(
                        len(events) + 1,
                        "session_boundary",
                        stamp,
                        config,
                        actor_id=actor(),
                        outcome=outcome,
                        failure_class=failure_class(
                            payload_type,
                            payload.get("code"),
                            payload.get("error_type"),
                            nested(payload, "error", "type"),
                        ),
                    )
                )
                continue
            if payload_type in {"collab_agent_spawn_end", "agent_spawned"}:
                child_raw = payload.get(
                    "new_thread_id", payload.get("child_id", payload.get("call_id"))
                )
                child_key = str(child_raw) if child_raw is not None else f"line-{line_number}"
                if child_key not in child_ordinals:
                    child_ordinals[child_key] = next_child_ordinal
                    next_child_ordinal += 1
                child_config = dict(config)
                child_config.update(payload)
                events.append(
                    event_with_config(
                        len(events) + 1,
                        "agent_spawn",
                        stamp,
                        child_config,
                        actor_id=pseudonyms.value("actor", child_raw),
                        parent_id=actor(payload.get("parent_thread_id")),
                        operation_id=pseudonyms.value("operation", payload.get("call_id")),
                        child_ordinal=child_ordinals[child_key],
                        forked_context_tokens=integer(payload.get("forked_context_tokens")),
                        outcome="success",
                    )
                )
                continue
            if payload_type in {"collab_close_end", "agent_finished", "agent_failed"}:
                child_raw = payload.get(
                    "receiver_thread_id",
                    payload.get("child_id", payload.get("call_id")),
                )
                child_key = str(child_raw) if child_raw is not None else f"line-{line_number}"
                if child_key not in child_ordinals:
                    child_ordinals[child_key] = next_child_ordinal
                    next_child_ordinal += 1
                failed = "failed" in str(payload_type)
                events.append(
                    event_with_config(
                        len(events) + 1,
                        "agent_finish",
                        stamp,
                        payload,
                        actor_id=pseudonyms.value("actor", child_raw),
                        parent_id=actor(payload.get("parent_thread_id")),
                        operation_id=pseudonyms.value(
                            "operation", payload.get("call_id")
                        ),
                        child_ordinal=child_ordinals[child_key],
                        outcome="failure" if failed else "success",
                        failure_class=(
                            failure_class(payload_type, payload.get("code"))
                            if failed
                            else None
                        ),
                    )
                )
                continue
            continue

        if record_type == "response_item":
            item_type = payload.get("type")
            category = tool_category(item_type)
            if category is None:
                continue
            status = tool_status("item.completed", payload)
            events.append(
                event_with_config(
                    len(events) + 1,
                    "tool",
                    stamp,
                    config,
                    actor_id=actor(),
                    operation_id=pseudonyms.value(
                        "operation",
                        payload.get("call_id", payload.get("id", f"line-{line_number}")),
                    ),
                    tool_category=category,
                    tool_status=status,
                    duration_ms=integer(payload.get("duration_ms")),
                    outcome=tool_outcome(status),
                    failure_class=(
                        failure_class(
                            payload.get("status"),
                            payload.get("exit_code"),
                            payload.get("error_type"),
                        )
                        if status == "failure"
                        else None
                    ),
                    tool_output_tokens=integer(payload.get("tool_output_tokens")),
                )
            )
            continue

        if record_type == "compacted":
            events.append(
                event_with_config(
                    len(events) + 1,
                    "compaction",
                    stamp,
                    config,
                    actor_id=actor(),
                    compaction_reason=compaction_reason(payload.get("reason")),
                    pre_compaction_tokens=integer(payload.get("pre_compaction_tokens")),
                    post_compaction_tokens=integer(payload.get("post_compaction_tokens")),
                    output_tokens=integer(payload.get("output_tokens")),
                )
            )
            continue

    session_id = pseudonyms.value("session", raw_session_id)
    root_config = config_fields(config)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "session_trace",
        "export_id": pseudonyms.export_id,
        "source": {
            "kind": "codex-session",
            "source_id": pseudonyms.value("source", str(source.path.resolve())),
            "parser": "codex-rollout-v2",
        },
        "session": {
            "session_id": session_id,
            "root_actor_id": actor(),
            "started_at": started_at,
            "ended_at": ended_at,
            **root_config,
        },
        "events": events,
        "warnings": warnings,
    }


def parse_exec(
    source: SourceRecords,
    pseudonyms: Pseudonymizer,
    source_index: int,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    warnings = list(source.warnings)
    config: dict[str, Any] = {"role": "root"}
    raw_session_id: Any = f"source-{source_index}"
    started_at: str | None = None
    ended_at: str | None = None

    def actor() -> str | None:
        return pseudonyms.value("actor", raw_session_id)

    for line_number, record in source.records:
        record_type = record.get("type")
        stamp = timestamp(record)
        config.update(
            {
                key: record[key]
                for key in (
                    "model",
                    "effective_model",
                    "requested_model",
                    "reasoning_effort",
                    "requested_reasoning_effort",
                    "service_tier",
                    "fork_mode",
                    "role",
                )
                if key in record
            }
        )
        if record_type == "thread.started":
            raw_session_id = record.get("thread_id", raw_session_id)
            started_at = started_at or stamp
            continue
        if record_type == "turn.started":
            started_at = started_at or stamp
            events.append(
                event_with_config(
                    len(events) + 1,
                    "session_boundary",
                    stamp,
                    config,
                    actor_id=actor(),
                    outcome="started",
                )
            )
            continue
        if record_type in {"turn.completed", "turn.failed"}:
            usage = usage_fields(record.get("usage"))
            failed = record_type.endswith("failed")
            ended_at = stamp or ended_at
            events.append(
                event_with_config(
                    len(events) + 1,
                    "turn",
                    stamp,
                    config,
                    actor_id=actor(),
                    outcome="failure" if failed else "success",
                    failure_class=(
                        failure_class(
                            record.get("code"),
                            record.get("error_type"),
                            nested(record, "error", "type"),
                        )
                        if failed
                        else None
                    ),
                    **usage,
                )
            )
            continue
        if isinstance(record_type, str) and record_type.startswith("item."):
            item = record.get("item") if isinstance(record.get("item"), dict) else record
            category = tool_category(item.get("type"))
            if category is None:
                continue
            status = tool_status(record_type, item)
            events.append(
                event_with_config(
                    len(events) + 1,
                    "tool",
                    stamp,
                    config,
                    actor_id=actor(),
                    operation_id=pseudonyms.value(
                        "operation", item.get("id", f"line-{line_number}")
                    ),
                    tool_category=category,
                    tool_status=status,
                    duration_ms=integer(item.get("duration_ms")),
                    outcome=tool_outcome(status),
                    failure_class=(
                        failure_class(
                            item.get("status"),
                            item.get("exit_code"),
                            item.get("error_type"),
                        )
                        if status == "failure"
                        else None
                    ),
                    tool_output_tokens=integer(item.get("tool_output_tokens")),
                )
            )

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "session_trace",
        "export_id": pseudonyms.export_id,
        "source": {
            "kind": "codex-session",
            "source_id": pseudonyms.value("source", str(source.path.resolve())),
            "parser": "codex-exec-json-v2",
        },
        "session": {
            "session_id": pseudonyms.value("session", raw_session_id),
            "root_actor_id": actor(),
            "started_at": started_at,
            "ended_at": ended_at,
            **config_fields(config),
        },
        "events": events,
        "warnings": warnings,
    }


def read_source(path: Path, max_line_bytes: int) -> SourceRecords:
    records: list[tuple[int, dict[str, Any]]] = []
    warnings: list[dict[str, Any]] = []
    records_seen = 0
    malformed = 0
    bytes_read = 0
    with path.open("rb") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            bytes_read += len(raw_line)
            if not raw_line.strip():
                continue
            records_seen += 1
            if len(raw_line) > max_line_bytes:
                warnings.append({"code": "line_too_large", "line": line_number})
                continue
            try:
                value = json.loads(raw_line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                malformed += 1
                warnings.append({"code": "malformed_json", "line": line_number})
                continue
            if not isinstance(value, dict):
                warnings.append({"code": "non_object_record", "line": line_number})
                continue
            records.append((line_number, value))
    return SourceRecords(
        path, records, bytes_read, records_seen, malformed, warnings
    )


def discover_files(
    inputs: Sequence[Path],
    since_days: int | None,
    max_files: int,
    max_bytes: int,
) -> tuple[list[Path], bool]:
    cutoff = None if since_days is None else time.time() - since_days * 86400
    candidates: set[Path] = set()
    for raw in inputs:
        path = raw.expanduser()
        if (
            path.is_file()
            and not path.is_symlink()
            and path.suffix.lower() in {".json", ".jsonl"}
            and path.name.lower() not in SENSITIVE_NAMES
        ):
            candidates.add(path)
        elif path.is_dir():
            for candidate in path.rglob("*"):
                if (
                    candidate.is_file()
                    and not candidate.is_symlink()
                    and candidate.suffix.lower() in {".json", ".jsonl"}
                    and candidate.name.lower() not in SENSITIVE_NAMES
                ):
                    candidates.add(candidate)
    selected: list[Path] = []
    total_bytes = 0
    truncated = False
    for path in sorted(candidates, key=lambda item: str(item.resolve())):
        if len(selected) >= max_files:
            truncated = True
            break
        try:
            stat = path.stat()
        except OSError:
            continue
        if cutoff is not None and stat.st_mtime < cutoff:
            continue
        if total_bytes + stat.st_size > max_bytes:
            truncated = True
            break
        selected.append(path)
        total_bytes += stat.st_size
    return selected, truncated


def parse_sources(
    paths: Sequence[Path], pseudonyms: Pseudonymizer, max_line_bytes: int
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    traces: list[dict[str, Any]] = []
    coverage = {
        "files_parsed": 0,
        "bytes_scanned": 0,
        "records_seen": 0,
        "records_supported": 0,
        "malformed_records": 0,
        "warnings": 0,
        "unsupported_files": 0,
    }
    for source_index, path in enumerate(paths, 1):
        source = read_source(path, max_line_bytes)
        coverage["bytes_scanned"] += source.bytes_read
        coverage["records_seen"] += source.records_seen
        coverage["malformed_records"] += source.malformed
        parser = detect_parser(source.records)
        if parser is None:
            coverage["unsupported_files"] += 1
            continue
        trace = (
            parse_rollout(source, pseudonyms, source_index)
            if parser.startswith("codex-rollout")
            else parse_exec(source, pseudonyms, source_index)
        )
        coverage["files_parsed"] += 1
        coverage["records_supported"] += supported_record_count(
            source.records, trace["source"]["parser"]
        )
        coverage["warnings"] += len(trace["warnings"])
        traces.append(trace)
    return traces, coverage


def summarize(
    traces: Sequence[dict[str, Any]], coverage: dict[str, int], discovered: int, truncated: bool
) -> dict[str, Any]:
    totals = Counter(
        sessions=len(traces),
        events=0,
        turns=0,
        tools=0,
        agent_spawns=0,
        agent_finishes=0,
        compactions=0,
        failures=0,
        input_tokens=0,
        cached_input_tokens=0,
        cache_write_tokens=0,
        output_tokens=0,
        reasoning_tokens=0,
        tool_output_tokens=0,
        forked_context_tokens=0,
    )
    roles: Counter[str] = Counter()
    models: Counter[str] = Counter()
    parsers: Counter[str] = Counter()
    for trace in traces:
        parsers[trace["source"]["parser"]] += 1
        session_role = trace["session"].get("role")
        if session_role:
            roles[session_role] += 1
        session_model = trace["session"].get("effective_model")
        if session_model:
            models[session_model] += 1
        for item in trace["events"]:
            totals["events"] += 1
            if item["kind"] == "turn":
                totals["turns"] += 1
            elif item["kind"] == "tool":
                totals["tools"] += 1
            elif item["kind"] == "agent_spawn":
                totals["agent_spawns"] += 1
            elif item["kind"] == "agent_finish":
                totals["agent_finishes"] += 1
            elif item["kind"] == "compaction":
                totals["compactions"] += 1
            if item.get("outcome") == "failure":
                totals["failures"] += 1
            if item.get("role"):
                roles[item["role"]] += 1
            if item.get("effective_model"):
                models[item["effective_model"]] += 1
            for token_field in (
                "input_tokens",
                "cached_input_tokens",
                "cache_write_tokens",
                "output_tokens",
                "reasoning_tokens",
                "tool_output_tokens",
                "forked_context_tokens",
            ):
                value = item.get(token_field)
                if isinstance(value, int):
                    totals[token_field] += value
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "session_trace_summary",
        "totals": dict(totals),
        "groups": {
            "roles": dict(sorted(roles.items())),
            "effective_models": dict(sorted(models.items())),
            "parsers": dict(sorted(parsers.items())),
        },
        "coverage": {
            "files_discovered": discovered,
            "truncated": truncated,
            **coverage,
            "record_coverage": (
                round(coverage["records_supported"] / coverage["records_seen"], 4)
                if coverage["records_seen"]
                else None
            ),
        },
        "privacy": {
            "content_included": False,
            "identifiers": "export-scoped HMAC pseudonyms",
            "salt_emitted": False,
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--since-days", type=int)
    parser.add_argument("--max-files", type=int, default=1000)
    parser.add_argument("--max-mb", type=float, default=64.0)
    parser.add_argument("--max-line-mb", type=float, default=8.0)
    args = parser.parse_args(argv)
    if args.since_days is not None and args.since_days < 0:
        parser.error("since days must be nonnegative")
    if args.max_files <= 0 or args.max_mb <= 0 or args.max_line_mb <= 0:
        parser.error("scan limits must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    files, truncated = discover_files(
        args.inputs,
        args.since_days,
        args.max_files,
        int(args.max_mb * 1024 * 1024),
    )
    pseudonyms = Pseudonymizer()
    try:
        traces, coverage = parse_sources(
            files, pseudonyms, int(args.max_line_mb * 1024 * 1024)
        )
    except OSError as error:
        print(f"session trace failed: {error}", file=sys.stderr)
        return 2

    if args.summary:
        output = json.dumps(
            summarize(traces, coverage, len(files), truncated),
            indent=2,
            sort_keys=True,
        ) + "\n"
    else:
        output = "".join(json.dumps(trace, sort_keys=True) + "\n" for trace in traces)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
