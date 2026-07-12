#!/usr/bin/env python3
"""Extract privacy-preserving quantitative traces from local Codex records."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Iterator, Sequence

SCHEMA_VERSION = 1
PARSER_ROLLOUT = "codex-rollout-v1"
PARSER_EXEC = "codex-exec-json-v1"
SUPPORTED_SUFFIXES = {".jsonl", ".json"}
SENSITIVE_NAMES = {
    ".codex-global-state.json", ".env", "auth.json", "credentials.json",
    "history.jsonl", "models_cache.json", "session_index.jsonl",
}
EVENT_FIELDS = (
    "seq", "kind", "timestamp", "model", "reasoning_effort",
    "input_tokens", "cached_input_tokens", "cache_write_tokens",
    "output_tokens", "reasoning_tokens", "active_context_tokens",
    "tool_output_tokens", "forked_context_tokens", "child_model",
    "child_reasoning_effort", "pre_compaction_tokens",
    "post_compaction_tokens",
)
TOKEN_FIELDS = set(EVENT_FIELDS[5:]) - {"child_model", "child_reasoning_effort"}
ROUTING_FIELDS = {"model", "reasoning_effort", "child_model", "child_reasoning_effort"}
SAFE_VALUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,79}$")
TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$"
)
TOOL_ITEM_TYPES = {
    "command_execution", "computer_call_output", "custom_tool_call_output",
    "dynamic_tool_call", "file_change", "function_call_output",
    "image_generation", "local_shell_call_output", "mcp_tool_call", "web_search",
}


@dataclass
class ScanStats:
    files_discovered: int = 0
    files_parsed: int = 0
    bytes_scanned: int = 0
    records_seen: int = 0
    records_supported: int = 0
    malformed_records: int = 0
    truncated: bool = False
    parser_counts: dict[str, int] = field(default_factory=dict)


def stable_hash(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8", errors="surrogatepass")).hexdigest()
    return "sha256:" + digest[:16]


def hash_identifier(value: Any) -> str | None:
    return stable_hash(str(value)) if isinstance(value, (str, int)) and str(value) else None


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def first(mapping: dict[str, Any], *keys: str) -> Any:
    return next((mapping[key] for key in keys if key in mapping), None)


def token_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, float) and value >= 0 and value.is_integer():
        return int(value)
    return None


def safe_label(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value if SAFE_VALUE_RE.fullmatch(value) else None


def safe_timestamp(value: Any) -> str | None:
    if not isinstance(value, str) or not TIMESTAMP_RE.fullmatch(value.strip()):
        return None
    value = value.strip()
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return value


def normalize_usage(raw: dict[str, Any]) -> dict[str, int | None]:
    return {
        "input_tokens": token_int(first(raw, "input_tokens", "input")),
        "cached_input_tokens": token_int(first(
            raw, "cached_input_tokens", "cached_input", "cache_read_input_tokens"
        )),
        "cache_write_tokens": token_int(first(
            raw, "cache_write_tokens", "cache_creation_input_tokens"
        )),
        "output_tokens": token_int(first(raw, "output_tokens", "output")),
        "reasoning_tokens": token_int(first(
            raw, "reasoning_output_tokens", "reasoning_tokens"
        )),
        "active_context_tokens": token_int(raw.get("active_context_tokens")),
        "tool_output_tokens": token_int(raw.get("tool_output_tokens")),
        "forked_context_tokens": token_int(raw.get("forked_context_tokens")),
        "pre_compaction_tokens": token_int(raw.get("pre_compaction_tokens")),
        "post_compaction_tokens": token_int(raw.get("post_compaction_tokens")),
    }


def totals_monotonic(current: dict[str, int | None], previous: dict[str, int | None]) -> bool:
    pairs = [
        (value, previous.get(key)) for key, value in current.items()
        if value is not None and previous.get(key) is not None
    ]
    return bool(pairs) and all(current_value >= old_value for current_value, old_value in pairs)


class TraceBuilder:
    def __init__(self, source: Path, parser_name: str) -> None:
        self.source_hash = stable_hash(str(source.resolve()))
        self.parser_name = parser_name
        self.session_hash: str | None = None
        self.started_at: str | None = None
        self.ended_at: str | None = None
        self.root_model: str | None = None
        self.root_effort: str | None = None
        self.model: str | None = None
        self.effort: str | None = None
        self.events: list[dict[str, Any]] = []
        self.warnings: list[str] = []
        self.open_turn: int | None = None
        self.previous_totals: dict[str, int | None] | None = None
        self.spawned: set[str] = set()
        self.finished: set[str] = set()

    def warn(self, code: str, line: int | None = None) -> None:
        message = code + (f" at line {line}" if line is not None else "")
        if message not in self.warnings:
            self.warnings.append(message)

    def timestamp(self, value: Any) -> str | None:
        value = safe_timestamp(value)
        if value is not None:
            self.started_at = value if self.started_at is None else min(self.started_at, value)
            self.ended_at = value if self.ended_at is None else max(self.ended_at, value)
        return value

    def route(self, model: Any = None, effort: Any = None) -> None:
        model, effort = safe_label(model), safe_label(effort)
        if model is not None:
            self.model = model
            self.root_model = self.root_model or model
        if effort is not None:
            self.effort = effort
            self.root_effort = self.root_effort or effort

    def event(self, kind: str, timestamp: Any = None, **values: Any) -> int:
        event = {field: None for field in EVENT_FIELDS}
        event.update(seq=len(self.events) + 1, kind=kind, timestamp=self.timestamp(timestamp))
        for key, value in values.items():
            if key in TOKEN_FIELDS:
                event[key] = token_int(value)
            elif key in ROUTING_FIELDS:
                event[key] = safe_label(value)
        self.events.append(event)
        return len(self.events) - 1

    def start_turn(self, timestamp: Any = None, model: Any = None, effort: Any = None) -> None:
        self.open_turn = None
        self.route(model, effort)
        self.open_turn = self.event(
            "turn", timestamp, model=self.model, reasoning_effort=self.effort
        )

    def ensure_turn(self, timestamp: Any = None) -> int:
        if self.open_turn is None:
            self.start_turn(timestamp)
        assert self.open_turn is not None
        return self.open_turn

    def add_usage(self, usage: dict[str, Any], timestamp: Any = None) -> None:
        event = self.events[self.ensure_turn(timestamp)]
        for key, value in normalize_usage(usage).items():
            if value is not None:
                event[key] = value if event[key] is None else event[key] + value

    def add_cumulative_usage(self, info: dict[str, Any], line: int, timestamp: Any) -> None:
        total = normalize_usage(as_dict(info.get("total_token_usage")))
        last = normalize_usage(as_dict(info.get("last_token_usage")))
        has_total = any(value is not None for value in total.values())
        has_last = any(value is not None for value in last.values())
        if not has_total and not has_last:
            self.warn("token event had no supported usage fields", line)
            return
        if has_total and self.previous_totals is not None and totals_monotonic(total, self.previous_totals):
            delta = {
                key: value - self.previous_totals[key]
                if value is not None and self.previous_totals.get(key) is not None else None
                for key, value in total.items()
            }
        elif has_total and self.previous_totals is None:
            delta = last if has_last else total
        elif has_total and has_last:
            delta = last
            self.warn("token totals reset; used last usage", line)
        else:
            delta = last if has_last else total
        self.add_usage(delta, timestamp)
        if has_total:
            self.previous_totals = total

    def agent_spawn(self, child_id: Any, timestamp: Any, payload: dict[str, Any]) -> None:
        child = hash_identifier(child_id)
        if child is not None and child in self.spawned:
            return
        if child is not None:
            self.spawned.add(child)
        self.event(
            "agent_spawn", timestamp, model=self.model, reasoning_effort=self.effort,
            child_model=payload.get("model"),
            child_reasoning_effort=first(payload, "reasoning_effort", "effort"),
            forked_context_tokens=payload.get("forked_context_tokens"),
        )

    def agent_finish(self, child_id: Any, timestamp: Any) -> None:
        child = hash_identifier(child_id)
        if child is not None and child in self.finished:
            return
        if child is not None:
            self.finished.add(child)
        self.event(
            "agent_finish", timestamp, model=self.model, reasoning_effort=self.effort
        )

    def finish(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "source": {
                "kind": "codex-session", "source_id_hash": self.source_hash,
                "parser": self.parser_name,
            },
            "session": {
                "session_id_hash": self.session_hash, "started_at": self.started_at,
                "ended_at": self.ended_at, "root_model": self.root_model,
                "root_reasoning_effort": self.root_effort,
            },
            "events": self.events,
            "warnings": sorted(self.warnings),
        }


def detect_parser(record: dict[str, Any]) -> str | None:
    kind = record.get("type")
    if kind in {
        "session_meta", "response_item", "inter_agent_communication",
        "inter_agent_communication_metadata", "compacted", "turn_context",
        "world_state", "event_msg",
    }:
        return PARSER_ROLLOUT
    if isinstance(kind, str) and (
        kind.startswith("thread.") or kind.startswith("turn.")
        or kind.startswith("item.") or kind == "error"
    ):
        return PARSER_EXEC
    return None


def is_tool_item(kind: Any) -> bool:
    return isinstance(kind, str) and (kind in TOOL_ITEM_TYPES or kind.endswith("_call_output"))


def handle_rollout(builder: TraceBuilder, record: dict[str, Any], line: int) -> bool:
    kind, payload = record.get("type"), as_dict(record.get("payload"))
    timestamp = record.get("timestamp")
    if kind == "session_meta":
        builder.session_hash = hash_identifier(first(payload, "session_id", "id"))
        builder.event("session_boundary", first(payload, "timestamp", "started_at") or timestamp)
        builder.route(payload.get("model"), first(payload, "reasoning_effort", "effort"))
    elif kind == "turn_context":
        builder.route(payload.get("model"), first(payload, "effort", "reasoning_effort"))
        builder.timestamp(timestamp)
    elif kind == "compacted":
        builder.event(
            "compaction", timestamp, model=builder.model, reasoning_effort=builder.effort,
            pre_compaction_tokens=payload.get("pre_compaction_tokens"),
            post_compaction_tokens=payload.get("post_compaction_tokens"),
        )
    elif kind == "response_item":
        if is_tool_item(payload.get("type")):
            builder.event(
                "tool_result", timestamp, model=builder.model,
                reasoning_effort=builder.effort,
                tool_output_tokens=payload.get("tool_output_tokens"),
            )
        else:
            builder.timestamp(timestamp)
    elif kind in {"inter_agent_communication", "inter_agent_communication_metadata", "world_state"}:
        builder.timestamp(timestamp)
    elif kind == "event_msg":
        event_kind = payload.get("type")
        if event_kind in {"task_started", "turn_started"}:
            builder.start_turn(timestamp, payload.get("model"), first(payload, "reasoning_effort", "effort"))
        elif event_kind in {"task_complete", "turn_complete", "turn_aborted"}:
            builder.timestamp(timestamp)
            builder.open_turn = None
        elif event_kind == "token_count":
            builder.add_cumulative_usage(as_dict(payload.get("info")), line, timestamp)
        elif event_kind == "thread_settings_applied":
            settings = as_dict(payload.get("thread_settings"))
            builder.route(first(settings, "model", "model_id"), first(settings, "reasoning_effort", "effort"))
            builder.timestamp(timestamp)
        elif event_kind == "model_reroute":
            builder.route(payload.get("to_model"))
            if builder.open_turn is not None:
                builder.events[builder.open_turn]["model"] = builder.model
            builder.timestamp(timestamp)
        elif event_kind == "collab_agent_spawn_end":
            builder.agent_spawn(first(payload, "new_thread_id", "receiver_thread_id", "agent_thread_id"), timestamp, payload)
        elif event_kind == "collab_close_end":
            builder.agent_finish(first(payload, "receiver_thread_id", "agent_thread_id"), timestamp)
        elif event_kind == "sub_agent_activity":
            child = first(payload, "agent_thread_id", "receiver_thread_id")
            if payload.get("activity_kind") == "started":
                builder.agent_spawn(child, timestamp, {})
            elif payload.get("activity_kind") in {"interrupted", "completed", "finished"}:
                builder.agent_finish(child, timestamp)
            else:
                builder.timestamp(timestamp)
        else:
            builder.timestamp(timestamp)
    else:
        return False
    return True


def handle_exec(builder: TraceBuilder, record: dict[str, Any]) -> bool:
    kind, timestamp = record.get("type"), record.get("timestamp")
    if kind == "thread.started":
        builder.session_hash = hash_identifier(first(record, "thread_id", "session_id", "id"))
        builder.route(record.get("model"), first(record, "reasoning_effort", "effort"))
        builder.event("session_boundary", timestamp)
    elif kind == "turn.started":
        builder.start_turn(timestamp, record.get("model"), first(record, "reasoning_effort", "effort"))
    elif kind == "turn.completed":
        builder.add_usage(as_dict(record.get("usage")), timestamp)
        builder.open_turn = None
    elif kind == "turn.failed":
        builder.timestamp(timestamp)
        builder.open_turn = None
    elif kind == "item.completed":
        item = as_dict(record.get("item"))
        if is_tool_item(item.get("type")):
            builder.event(
                "tool_result", timestamp, model=builder.model,
                reasoning_effort=builder.effort,
                tool_output_tokens=item.get("tool_output_tokens"),
            )
        else:
            builder.timestamp(timestamp)
    elif kind in {"item.started", "item.updated", "error"}:
        builder.timestamp(timestamp)
    else:
        return False
    return True


def parse_json(raw: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def bounded_lines(handle: BinaryIO, max_bytes: int, max_line: int) -> Iterator[tuple[int, bytes, bool, int]]:
    consumed = 0
    line = 0
    while consumed < max_bytes:
        raw = handle.readline(min(max_line + 1, max_bytes - consumed))
        if not raw:
            break
        line += 1
        consumed += len(raw)
        if len(raw) > max_line and not raw.endswith(b"\n"):
            record_bytes = len(raw)
            while consumed < max_bytes:
                chunk = handle.readline(min(max_line + 1, max_bytes - consumed))
                if not chunk:
                    break
                consumed += len(chunk)
                record_bytes += len(chunk)
                if chunk.endswith(b"\n"):
                    break
            yield line, b"", True, record_bytes
        else:
            yield line, raw, False, len(raw)


def parse_file(path: Path, selected: str, max_bytes: int, max_line: int, stats: ScanStats) -> tuple[dict[str, Any], int]:
    builder: TraceBuilder | None = None
    consumed = 0
    records_before = stats.records_seen
    parser_name = selected if selected != "auto" else "unknown"
    try:
        with path.open("rb") as handle:
            for line, raw, oversized, read_bytes in bounded_lines(handle, max_bytes, max_line):
                consumed += read_bytes
                if oversized:
                    stats.malformed_records += 1
                    builder = builder or TraceBuilder(path, parser_name)
                    builder.warn("record exceeded line byte limit", line)
                    continue
                if not raw.strip():
                    continue
                stats.records_seen += 1
                record = parse_json(raw)
                if record is None:
                    stats.malformed_records += 1
                    builder = builder or TraceBuilder(path, parser_name)
                    builder.warn("malformed json record", line)
                    continue
                detected = detect_parser(record)
                if builder is None:
                    parser_name = selected if selected != "auto" else (detected or "unsupported-jsonl-v1")
                    builder = TraceBuilder(path, parser_name)
                if selected == "auto" and detected and builder.parser_name in {"unknown", "unsupported-jsonl-v1"}:
                    builder.parser_name = detected
                if detected and builder.parser_name in {PARSER_ROLLOUT, PARSER_EXEC} and detected != builder.parser_name:
                    builder.warn("mixed source formats; ignored incompatible record", line)
                    continue
                supported = (
                    handle_rollout(builder, record, line) if builder.parser_name == PARSER_ROLLOUT
                    else handle_exec(builder, record) if builder.parser_name == PARSER_EXEC
                    else False
                )
                stats.records_supported += int(supported)
    except OSError:
        builder = builder or TraceBuilder(path, parser_name)
        builder.warn("source could not be read")
    builder = builder or TraceBuilder(path, parser_name)
    if stats.records_seen == records_before and not builder.warnings:
        builder.warn("source contained no records")
    try:
        if path.stat().st_size > max_bytes:
            builder.warn("source truncated by byte limit")
            stats.truncated = True
    except OSError:
        pass
    return builder.finish(), consumed


def discover(input_path: Path, since_days: int | None) -> list[Path]:
    cutoff = None
    if since_days is not None:
        cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=since_days)).timestamp()
    if input_path.is_file():
        candidates = [input_path]
    elif input_path.is_dir():
        candidates = [
            path for path in input_path.rglob("*")
            if path.is_file() and not path.is_symlink()
            and path.suffix.lower() in SUPPORTED_SUFFIXES
        ]
    else:
        raise ValueError("input path does not exist")
    files = []
    for path in candidates:
        if path.name.lower() in SENSITIVE_NAMES:
            continue
        try:
            if cutoff is not None and path.stat().st_mtime < cutoff:
                continue
        except OSError:
            continue
        files.append(path)
    return sorted(files, key=lambda path: (str(path).casefold(), str(path)))


def extract_traces(args: argparse.Namespace) -> tuple[list[dict[str, Any]], ScanStats]:
    input_path = args.input.expanduser()
    if input_path.is_file() and input_path.name.lower() in SENSITIVE_NAMES:
        raise ValueError("refusing to scan a known sensitive state file")
    files = discover(input_path, args.since_days)
    stats = ScanStats(files_discovered=len(files))
    traces = []
    remaining = int(args.max_mb * 1024 * 1024)
    max_line = int(args.max_line_mb * 1024 * 1024)
    for path in files[:args.max_files]:
        if remaining <= 0:
            stats.truncated = True
            break
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        trace, consumed = parse_file(path, args.format, min(size, remaining), max_line, stats)
        traces.append(trace)
        stats.files_parsed += 1
        stats.bytes_scanned += consumed
        stats.parser_counts[trace["source"]["parser"]] = stats.parser_counts.get(trace["source"]["parser"], 0) + 1
        remaining -= consumed
        if size > consumed:
            stats.truncated = True
            break
    if len(files) > args.max_files:
        stats.truncated = True
    return traces, stats


def summarize(traces: Sequence[dict[str, Any]], stats: ScanStats) -> dict[str, Any]:
    totals = {
        "sessions": len(traces), "turns": 0, "total_logical_input": 0,
        "cached_input": 0, "output": 0, "reasoning": 0, "compactions": 0,
        "agent_spawns": 0, "forked_context_tokens": 0, "tool_output_tokens": 0,
    }
    tracked = {
        "turn.input_tokens": ("turn", "input_tokens"),
        "turn.cached_input_tokens": ("turn", "cached_input_tokens"),
        "turn.output_tokens": ("turn", "output_tokens"),
        "turn.reasoning_tokens": ("turn", "reasoning_tokens"),
        "turn.active_context_tokens": ("turn", "active_context_tokens"),
        "tool_result.tool_output_tokens": ("tool_result", "tool_output_tokens"),
        "agent_spawn.forked_context_tokens": ("agent_spawn", "forked_context_tokens"),
        "compaction.pre_compaction_tokens": ("compaction", "pre_compaction_tokens"),
        "compaction.post_compaction_tokens": ("compaction", "post_compaction_tokens"),
    }
    denominators = {key: 0 for key in tracked}
    missing = {key: 0 for key in tracked}
    warnings = 0
    for trace in traces:
        warnings += len(trace.get("warnings", []))
        for event in trace.get("events", []):
            kind = event.get("kind")
            if kind == "turn":
                totals["turns"] += 1
                totals["total_logical_input"] += event.get("input_tokens") or 0
                totals["cached_input"] += event.get("cached_input_tokens") or 0
                totals["output"] += event.get("output_tokens") or 0
                totals["reasoning"] += event.get("reasoning_tokens") or 0
            elif kind == "compaction":
                totals["compactions"] += 1
            elif kind == "agent_spawn":
                totals["agent_spawns"] += 1
                totals["forked_context_tokens"] += event.get("forked_context_tokens") or 0
            elif kind == "tool_result":
                totals["tool_output_tokens"] += event.get("tool_output_tokens") or 0
            for name, (expected_kind, field_name) in tracked.items():
                if kind == expected_kind:
                    denominators[name] += 1
                    missing[name] += int(event.get(field_name) is None)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "session_trace_summary",
        "totals": totals,
        "coverage": {
            "files_discovered": stats.files_discovered,
            "files_parsed": stats.files_parsed,
            "bytes_scanned": stats.bytes_scanned,
            "truncated": stats.truncated,
            "records_seen": stats.records_seen,
            "records_supported": stats.records_supported,
            "malformed_records": stats.malformed_records,
            "record_coverage": round(stats.records_supported / stats.records_seen, 6) if stats.records_seen else None,
            "parser_counts": dict(sorted(stats.parser_counts.items())),
            "missing_fields": missing,
            "field_denominators": denominators,
            "warnings": warnings,
        },
    }


def render_summary(summary: dict[str, Any]) -> str:
    totals, coverage = summary["totals"], summary["coverage"]
    return "\n".join([
        f"sessions: {totals['sessions']}", f"turns: {totals['turns']}",
        f"logical input tokens: {totals['total_logical_input']}",
        f"cached input tokens: {totals['cached_input']}",
        f"output tokens: {totals['output']}",
        f"reasoning tokens: {totals['reasoning']}",
        f"compactions: {totals['compactions']}",
        f"agent spawns: {totals['agent_spawns']}",
        f"records supported: {coverage['records_supported']}/{coverage['records_seen']}",
        f"truncated: {str(coverage['truncated']).lower()}",
    ])


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--since-days", type=int)
    parser.add_argument("--max-files", type=int, default=1000)
    parser.add_argument("--max-mb", type=float, default=64.0)
    parser.add_argument("--max-line-mb", type=float, default=8.0)
    parser.add_argument("--format", choices=("auto", PARSER_ROLLOUT, PARSER_EXEC), default="auto")
    args = parser.parse_args(argv)
    if args.since_days is not None and args.since_days < 0:
        parser.error("--since-days must be nonnegative")
    if args.max_files <= 0 or args.max_mb <= 0 or args.max_line_mb <= 0:
        parser.error("scan bounds must be positive")
    if args.json and not args.summary:
        parser.error("--json is only valid with --summary")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        traces, stats = extract_traces(args)
        if args.summary:
            report = summarize(traces, stats)
            text = json.dumps(report, indent=2, sort_keys=True) if args.json else render_summary(report)
        else:
            text = "\n".join(json.dumps(trace, sort_keys=True, separators=(",", ":")) for trace in traces)
        if args.output is None:
            print(text)
        else:
            output = args.output.expanduser()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
    except (OSError, ValueError) as error:
        message = str(error) if isinstance(error, ValueError) else "input or output could not be read"
        print(f"session trace failed: {message}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
