# Session Trace Schema

Schema version 1 defines a local normalization boundary for quantitative Codex
session analysis. The extractor reads local session records and emits only
content-free metadata suitable for aggregate studies and compaction simulation.

## Privacy Contract

The output is built from a fixed allowlist. It cannot include message bodies,
assistant text, reasoning text, tool output, commands, repository contents,
working directories, raw paths, originator data, secrets, or raw session and
agent identifiers.

Source paths and session identifiers are represented only as a stable
`sha256:` prefix. Child agent identifiers are used only for in-memory deduping
and are never emitted. Model and reasoning-effort values pass a strict short
identifier filter. Warnings use static error codes and line numbers, never raw
record content. Fixtures are synthetic and contain no copied session data.

A hash is an identifier, not encryption. Do not publish traces when the source
identifier itself is sensitive enough to be guessed from a small candidate set.

## Trace Document

The default output is newline-delimited JSON with one trace document per source
file. Every document has this shape:

```json
{
  "schema_version": 1,
  "source": {
    "kind": "codex-session",
    "source_id_hash": "sha256:0123456789abcdef",
    "parser": "codex-rollout-v1"
  },
  "session": {
    "session_id_hash": "sha256:0123456789abcdef",
    "started_at": "2026-07-01T12:00:00Z",
    "ended_at": "2026-07-01T12:00:10Z",
    "root_model": "gpt-5.6-codex",
    "root_reasoning_effort": "high"
  },
  "events": [],
  "warnings": []
}
```

Unknown values are `null`. The extractor does not estimate missing token values.

### Event fields

Every event contains all fields below. Fields that do not apply to the event are
`null`.

| Field | Type | Meaning |
| --- | --- | --- |
| `seq` | integer | Deterministic one-based order within the source file. |
| `kind` | string | One of `turn`, `tool_result`, `agent_spawn`, `agent_finish`, `compaction`, or `session_boundary`. |
| `timestamp` | string or null | Valid source RFC 3339 timestamp when present. |
| `model` | string or null | Model routing active for the event. |
| `reasoning_effort` | string or null | Reasoning-effort routing active for the event. |
| `input_tokens` | integer or null | Logical input tokens reported for a turn. |
| `cached_input_tokens` | integer or null | Cached input tokens reported for a turn. |
| `cache_write_tokens` | integer or null | Cache write tokens when explicitly reported. |
| `output_tokens` | integer or null | Output tokens reported for a turn. |
| `reasoning_tokens` | integer or null | Reasoning output tokens reported for a turn. |
| `active_context_tokens` | integer or null | Active context size only when explicitly reported. |
| `tool_output_tokens` | integer or null | Tool-result contribution only when explicitly reported. |
| `forked_context_tokens` | integer or null | Context inherited by a child only when explicitly reported. |
| `child_model` | string or null | Child model on an agent spawn. |
| `child_reasoning_effort` | string or null | Child effort on an agent spawn. |
| `pre_compaction_tokens` | integer or null | Context size before compaction when explicitly reported. |
| `post_compaction_tokens` | integer or null | Context size after compaction when explicitly reported. |

## Supported Sources

### `codex-rollout-v1`

Parses canonical Codex rollout JSONL records with top-level `type`, `payload`,
and optional `timestamp` fields. Supported record families are:

- `session_meta` for hashed session identity and boundaries
- `turn_context` for model and reasoning-effort routing
- `event_msg` for turns, token counts, reroutes, agent lifecycle, and boundaries
- `response_item` for content-free tool-result events
- `compacted` for compaction events

Token count events may report cumulative totals and last-call usage. The parser
uses monotonic cumulative deltas and falls back to explicit last-call usage when
totals reset. Duplicate cumulative observations add zero tokens.

### `codex-exec-json-v1`

Parses the documented JSONL event stream from `codex exec --json`, including
`thread.started`, `turn.started`, `turn.completed`, `turn.failed`, and
`item.*` records. The documented `turn.completed.usage` object maps to turn
input, cached input, output, and reasoning tokens.

## Aggregate Summary

`--summary --json` emits one JSON document:

```json
{
  "schema_version": 1,
  "kind": "session_trace_summary",
  "totals": {
    "sessions": 0,
    "turns": 0,
    "total_logical_input": 0,
    "cached_input": 0,
    "output": 0,
    "reasoning": 0,
    "compactions": 0,
    "agent_spawns": 0,
    "forked_context_tokens": 0,
    "tool_output_tokens": 0
  },
  "coverage": {
    "files_discovered": 0,
    "files_parsed": 0,
    "bytes_scanned": 0,
    "truncated": false,
    "records_seen": 0,
    "records_supported": 0,
    "malformed_records": 0,
    "record_coverage": null,
    "parser_counts": {},
    "missing_fields": {},
    "field_denominators": {},
    "warnings": 0
  }
}
```

Missing-field counts use event-kind denominators so zero totals are not confused
with fully observed data.

## Bounds and Defaults

The extractor scans files in deterministic path order, skips symlinks and known
sensitive state filenames, and streams line by line. Defaults are 1,000 files,
64 MiB total input, and 8 MiB per line. `--since-days` uses file modification
time. Use `--since-days`, `--max-files`, `--max-mb`, and `--max-line-mb` to
tighten the scan. The default destination is standard output, so the tool never
writes into a tracked Compass path unless an explicit `--output` path is supplied.

```powershell
python scripts/session-trace.py --input <path> --output traces.jsonl
python scripts/session-trace.py --input <path> --summary --json
python scripts/session-trace.py --input <path> --since-days 30 --max-mb 64
```

## Coverage Limits

- Codex `model_context_window` is a capacity, not an observed active context
  size, so it is not mapped to `active_context_tokens`.
- Current rollout compaction records may omit pre and post token counts.
- Current tool-result and agent-spawn records may omit contribution sizes.
- Agent prompt text and child identifiers are intentionally discarded even when
  present.
- Timestamps, model routing, and reasoning effort remain `null` when the source
  does not report them in a supported field.
- Unknown record types and fields are ignored. Malformed records produce static
  warnings or a controlled CLI error.

Any incompatible field or meaning change requires a new schema version and a
new explicit parser name.
