#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("session-trace.py")
SPEC = importlib.util.spec_from_file_location("session_trace", MODULE_PATH)
assert SPEC and SPEC.loader
session_trace = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = session_trace
SPEC.loader.exec_module(session_trace)


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


class SessionTraceTests(unittest.TestCase):
    def test_rollout_preserves_structure_without_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private-session.jsonl"
            write_jsonl(
                path,
                [
                    {
                        "timestamp": "2026-07-01T12:00:00Z",
                        "type": "session_meta",
                        "payload": {
                            "id": "RAW_SESSION_SECRET",
                            "cwd": "/private/repository/name",
                            "originator": "PRIVATE_PERSON",
                        },
                    },
                    {
                        "timestamp": "2026-07-01T12:00:01Z",
                        "type": "turn_context",
                        "payload": {
                            "role": "controller",
                            "requested_model": "gpt-requested",
                            "model": "gpt-effective",
                            "requested_reasoning_effort": "medium",
                            "effort": "high",
                            "service_tier": "priority",
                            "fork_mode": "compact",
                        },
                    },
                    {
                        "timestamp": "2026-07-01T12:00:02Z",
                        "type": "event_msg",
                        "payload": {"type": "task_started"},
                    },
                    {
                        "timestamp": "2026-07-01T12:00:03Z",
                        "type": "response_item",
                        "payload": {
                            "type": "function_call_output",
                            "call_id": "RAW_TOOL_CALL",
                            "output": "PRIVATE_TOOL_OUTPUT",
                            "command": "rm -rf PRIVATE_COMMAND",
                            "tool_output_tokens": 12,
                        },
                    },
                    {
                        "timestamp": "2026-07-01T12:00:04Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 12000,
                                    "cached_input_tokens": 9000,
                                    "output_tokens": 500,
                                    "reasoning_output_tokens": 200,
                                },
                                "last_token_usage": {
                                    "input_tokens": 12000,
                                    "cached_input_tokens": 9000,
                                    "output_tokens": 500,
                                    "reasoning_output_tokens": 200,
                                },
                            },
                        },
                    },
                    {
                        "timestamp": "2026-07-01T12:00:05Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "collab_agent_spawn_end",
                            "new_thread_id": "RAW_CHILD_SECRET",
                            "role": "neutral-critic",
                            "model": "gpt-child",
                            "reasoning_effort": "medium",
                            "fork_mode": "full",
                            "forked_context_tokens": 8000,
                            "prompt": "PRIVATE_CHILD_PROMPT",
                        },
                    },
                    {
                        "timestamp": "2026-07-01T12:00:06Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "collab_close_end",
                            "receiver_thread_id": "RAW_CHILD_SECRET",
                        },
                    },
                    {
                        "timestamp": "2026-07-01T12:00:07Z",
                        "type": "compacted",
                        "payload": {
                            "reason": "automatic",
                            "pre_compaction_tokens": 90000,
                            "post_compaction_tokens": 18000,
                            "message": "PRIVATE_COMPACTION_TEXT",
                        },
                    },
                    {
                        "timestamp": "2026-07-01T12:00:08Z",
                        "type": "event_msg",
                        "payload": {"type": "task_complete"},
                    },
                ],
            )
            source = session_trace.read_source(path, 1024 * 1024)
            trace = session_trace.parse_rollout(
                source, session_trace.Pseudonymizer(b"a" * 32), 1
            )

            self.assertEqual(trace["schema_version"], 2)
            self.assertEqual(trace["session"]["role"], "controller")
            self.assertEqual(trace["session"]["requested_model"], "gpt-requested")
            self.assertEqual(trace["session"]["effective_model"], "gpt-effective")
            self.assertEqual(trace["session"]["service_tier"], "priority")

            spawn = next(item for item in trace["events"] if item["kind"] == "agent_spawn")
            finish = next(item for item in trace["events"] if item["kind"] == "agent_finish")
            self.assertEqual(spawn["actor_id"], finish["actor_id"])
            self.assertEqual(spawn["child_ordinal"], finish["child_ordinal"])
            self.assertEqual(spawn["role"], "neutral-critic")
            self.assertEqual(spawn["forked_context_tokens"], 8000)

            tool = next(item for item in trace["events"] if item["kind"] == "tool")
            self.assertEqual(tool["tool_category"], "connector")
            self.assertEqual(tool["tool_output_tokens"], 12)

            encoded = json.dumps(trace, sort_keys=True)
            for secret in (
                "RAW_SESSION_SECRET",
                "RAW_TOOL_CALL",
                "RAW_CHILD_SECRET",
                "PRIVATE_TOOL_OUTPUT",
                "PRIVATE_COMMAND",
                "PRIVATE_CHILD_PROMPT",
                "PRIVATE_COMPACTION_TEXT",
                "PRIVATE_PERSON",
                str(path),
            ):
                self.assertNotIn(secret, encoded)

    def test_pseudonyms_are_export_scoped(self) -> None:
        first = session_trace.Pseudonymizer(b"a" * 32)
        second = session_trace.Pseudonymizer(b"b" * 32)
        self.assertEqual(first.value("actor", "same"), first.value("actor", "same"))
        self.assertNotEqual(first.value("actor", "same"), second.value("actor", "same"))
        self.assertNotEqual(first.value("actor", "same"), first.value("session", "same"))

    def test_exec_failure_is_classified_without_error_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exec.jsonl"
            write_jsonl(
                path,
                [
                    {"type": "thread.started", "thread_id": "RAW_THREAD"},
                    {"type": "turn.started"},
                    {
                        "type": "item.completed",
                        "item": {
                            "id": "RAW_ITEM",
                            "type": "command_execution",
                            "command": "PRIVATE COMMAND",
                            "aggregated_output": "PRIVATE OUTPUT",
                            "exit_code": 1,
                            "tool_output_tokens": 4,
                        },
                    },
                    {
                        "type": "turn.failed",
                        "error_type": "timeout",
                        "error": {"message": "PRIVATE ERROR MESSAGE"},
                        "usage": {"input_tokens": 100, "output_tokens": 5},
                    },
                ],
            )
            source = session_trace.read_source(path, 1024 * 1024)
            trace = session_trace.parse_exec(
                source, session_trace.Pseudonymizer(b"c" * 32), 1
            )
            turn = next(item for item in trace["events"] if item["kind"] == "turn")
            self.assertEqual(turn["outcome"], "failure")
            self.assertEqual(turn["failure_class"], "timeout")
            tool = next(item for item in trace["events"] if item["kind"] == "tool")
            self.assertEqual(tool["tool_category"], "shell")
            self.assertEqual(tool["tool_status"], "failure")
            encoded = json.dumps(trace)
            self.assertNotIn("PRIVATE", encoded)
            self.assertNotIn("RAW_THREAD", encoded)
            self.assertNotIn("RAW_ITEM", encoded)

    def test_unknown_tool_state_and_untrusted_timestamp_are_not_promoted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unknown.jsonl"
            write_jsonl(
                path,
                [
                    {"type": "thread.started", "thread_id": "RAW_THREAD"},
                    {
                        "timestamp": "PRIVATE T TIMESTAMP",
                        "type": "item.updated",
                        "item": {
                            "id": "RAW_ITEM",
                            "type": "mcp_tool_call",
                            "status": "in_progress",
                        },
                    },
                ],
            )
            source = session_trace.read_source(path, 1024 * 1024)
            trace = session_trace.parse_exec(
                source, session_trace.Pseudonymizer(b"d" * 32), 1
            )
            tool = next(item for item in trace["events"] if item["kind"] == "tool")
            self.assertEqual(tool["tool_status"], "unknown")
            self.assertEqual(tool["outcome"], "unknown")
            self.assertIsNone(tool["timestamp"])
            self.assertNotIn("PRIVATE", json.dumps(trace))

    def test_coverage_counts_only_understood_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "coverage.jsonl"
            write_jsonl(
                path,
                [
                    {"type": "session_meta", "payload": {"id": "RAW"}},
                    {"type": "event_msg", "payload": {"type": "unknown_event"}},
                    {"type": "response_item", "payload": {"type": "message"}},
                ],
            )
            traces, coverage = session_trace.parse_sources(
                [path], session_trace.Pseudonymizer(b"e" * 32), 1024 * 1024
            )
            self.assertEqual(len(traces), 1)
            self.assertEqual(coverage["records_seen"], 3)
            self.assertEqual(coverage["records_supported"], 1)

    def test_explicit_sensitive_file_is_not_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "auth.json"
            path.write_text('{"type":"thread.started"}\n', encoding="utf-8")
            files, truncated = session_trace.discover_files(
                [path], None, max_files=10, max_bytes=1024
            )
            self.assertEqual(files, [])
            self.assertFalse(truncated)

    def test_summary_retains_role_and_outcome_counts(self) -> None:
        trace = {
            "source": {"parser": "codex-rollout-v2"},
            "session": {"role": "controller", "effective_model": "gpt-test"},
            "events": [
                {
                    "kind": "turn",
                    "outcome": "failure",
                    "role": "controller",
                    "effective_model": "gpt-test",
                    "input_tokens": 10,
                    "cached_input_tokens": 4,
                    "cache_write_tokens": 2,
                    "output_tokens": 3,
                    "reasoning_tokens": 1,
                    "tool_output_tokens": None,
                    "forked_context_tokens": None,
                }
            ],
        }
        coverage = {
            "files_parsed": 1,
            "bytes_scanned": 100,
            "records_seen": 1,
            "records_supported": 1,
            "malformed_records": 0,
            "warnings": 0,
            "unsupported_files": 0,
        }
        summary = session_trace.summarize([trace], coverage, 1, False)
        self.assertEqual(summary["totals"]["failures"], 1)
        self.assertEqual(summary["totals"]["input_tokens"], 10)
        self.assertEqual(summary["groups"]["roles"]["controller"], 2)
        self.assertFalse(summary["privacy"]["content_included"])


if __name__ == "__main__":
    unittest.main()
