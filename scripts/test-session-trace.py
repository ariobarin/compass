#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
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


def write_jsonl(path: Path, records: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(item if isinstance(item, str) else json.dumps(item) for item in records) + "\n",
        encoding="utf-8",
    )


def extract(path: Path, *extra: str):
    args = session_trace.parse_args(["--input", str(path), *extra])
    return session_trace.extract_traces(args)


class SessionTraceTests(unittest.TestCase):
    def test_rollout_redacts_content_and_hashes_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rollout-private-name.jsonl"
            prompt = "RAW_PROMPT_DO_NOT_EMIT"
            tool_output = "RAW_TOOL_OUTPUT_DO_NOT_EMIT"
            session_id = "session-secret-id"
            write_jsonl(
                path,
                [
                    {
                        "timestamp": "2026-07-10T10:00:00Z",
                        "type": "session_meta",
                        "payload": {
                            "id": session_id,
                            "cwd": "/private/repository/path",
                            "originator": "private-user",
                        },
                    },
                    {
                        "timestamp": "2026-07-10T10:00:01Z",
                        "type": "turn_context",
                        "payload": {"model": "gpt-5.6-codex", "effort": "high"},
                    },
                    {
                        "timestamp": "2026-07-10T10:00:02Z",
                        "type": "event_msg",
                        "payload": {"type": "task_started"},
                    },
                    {
                        "timestamp": "2026-07-10T10:00:03Z",
                        "type": "response_item",
                        "payload": {"type": "message", "content": prompt},
                    },
                    {
                        "timestamp": "2026-07-10T10:00:04Z",
                        "type": "response_item",
                        "payload": {
                            "type": "function_call_output",
                            "output": tool_output,
                            "tool_output_tokens": 7,
                        },
                    },
                    {
                        "timestamp": "2026-07-10T10:00:05Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 120,
                                    "cached_input_tokens": 80,
                                    "output_tokens": 20,
                                    "reasoning_output_tokens": 5,
                                },
                                "last_token_usage": {
                                    "input_tokens": 120,
                                    "cached_input_tokens": 80,
                                    "output_tokens": 20,
                                    "reasoning_output_tokens": 5,
                                },
                            },
                        },
                    },
                ],
            )
            traces, _ = extract(path)
            rendered = json.dumps(traces)
            self.assertNotIn(prompt, rendered)
            self.assertNotIn(tool_output, rendered)
            self.assertNotIn(str(path), rendered)
            self.assertNotIn(session_id, rendered)
            self.assertEqual(traces[0]["session"]["session_id_hash"], session_trace.stable_hash(session_id))
            self.assertEqual(traces[0]["source"]["source_id_hash"], session_trace.stable_hash(str(path.resolve())))

    def test_token_counts_normalize_cumulative_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tokens.jsonl"
            write_jsonl(
                path,
                [
                    {"type": "session_meta", "payload": {"id": "fake"}},
                    {"type": "event_msg", "payload": {"type": "task_started"}},
                    {
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 100,
                                    "cached_input_tokens": 40,
                                    "output_tokens": 10,
                                    "reasoning_output_tokens": 2,
                                },
                                "last_token_usage": {
                                    "input_tokens": 100,
                                    "cached_input_tokens": 40,
                                    "output_tokens": 10,
                                    "reasoning_output_tokens": 2,
                                },
                            },
                        },
                    },
                    {
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 250,
                                    "cached_input_tokens": 140,
                                    "output_tokens": 35,
                                    "reasoning_output_tokens": 8,
                                },
                                "last_token_usage": {
                                    "input_tokens": 150,
                                    "cached_input_tokens": 100,
                                    "output_tokens": 25,
                                    "reasoning_output_tokens": 6,
                                },
                            },
                        },
                    },
                    {"type": "event_msg", "payload": {"type": "task_complete"}},
                ],
            )
            traces, _ = extract(path)
            turn = next(event for event in traces[0]["events"] if event["kind"] == "turn")
            self.assertEqual(turn["input_tokens"], 250)
            self.assertEqual(turn["cached_input_tokens"], 140)
            self.assertEqual(turn["output_tokens"], 35)
            self.assertEqual(turn["reasoning_tokens"], 8)

    def test_exec_json_documented_usage_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exec.jsonl"
            write_jsonl(
                path,
                [
                    {"type": "thread.started", "thread_id": "thread-fake"},
                    {"type": "turn.started"},
                    {
                        "type": "item.completed",
                        "item": {
                            "type": "command_execution",
                            "aggregated_output": "SECRET_COMMAND_OUTPUT",
                            "tool_output_tokens": 4,
                        },
                    },
                    {
                        "type": "turn.completed",
                        "usage": {
                            "input_tokens": 24763,
                            "cached_input_tokens": 24448,
                            "output_tokens": 122,
                            "reasoning_output_tokens": 0,
                        },
                    },
                ],
            )
            traces, _ = extract(path)
            turn = next(event for event in traces[0]["events"] if event["kind"] == "turn")
            tool = next(event for event in traces[0]["events"] if event["kind"] == "tool_result")
            self.assertEqual(traces[0]["source"]["parser"], session_trace.PARSER_EXEC)
            self.assertEqual(turn["input_tokens"], 24763)
            self.assertEqual(turn["reasoning_tokens"], 0)
            self.assertEqual(tool["tool_output_tokens"], 4)
            self.assertNotIn("SECRET_COMMAND_OUTPUT", json.dumps(traces))

    def test_malformed_and_unknown_records_are_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "malformed.jsonl"
            write_jsonl(
                path,
                [
                    "{not json",
                    {"type": "session_meta", "payload": {"id": "fake"}},
                    {
                        "type": "event_msg",
                        "payload": {
                            "type": "future_event",
                            "unsupported_secret": "IGNORE_ME",
                        },
                    },
                ],
            )
            traces, stats = extract(path)
            rendered = json.dumps(traces)
            self.assertIn("malformed json record at line 1", traces[0]["warnings"])
            self.assertNotIn("IGNORE_ME", rendered)
            self.assertEqual(stats.malformed_records, 1)

    def test_agent_and_compaction_metadata_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "agents.jsonl"
            write_jsonl(
                path,
                [
                    {"type": "session_meta", "payload": {"id": "fake"}},
                    {
                        "type": "event_msg",
                        "payload": {
                            "type": "collab_agent_spawn_end",
                            "new_thread_id": "child-private-id",
                            "prompt": "CHILD_PROMPT_SECRET",
                            "model": "gpt-5.6-codex-mini",
                            "reasoning_effort": "medium",
                            "forked_context_tokens": 8000,
                        },
                    },
                    {
                        "type": "event_msg",
                        "payload": {
                            "type": "collab_close_end",
                            "receiver_thread_id": "child-private-id",
                        },
                    },
                    {
                        "type": "compacted",
                        "payload": {
                            "message": "COMPACTION_TEXT_SECRET",
                            "pre_compaction_tokens": 90000,
                            "post_compaction_tokens": 18000,
                        },
                    },
                ],
            )
            traces, _ = extract(path)
            rendered = json.dumps(traces)
            self.assertNotIn("child-private-id", rendered)
            self.assertNotIn("CHILD_PROMPT_SECRET", rendered)
            self.assertNotIn("COMPACTION_TEXT_SECRET", rendered)
            spawn = next(event for event in traces[0]["events"] if event["kind"] == "agent_spawn")
            compaction = next(event for event in traces[0]["events"] if event["kind"] == "compaction")
            self.assertEqual(spawn["forked_context_tokens"], 8000)
            self.assertEqual(compaction["pre_compaction_tokens"], 90000)
            self.assertEqual(compaction["post_compaction_tokens"], 18000)

    def test_output_ordering_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_jsonl(root / "z.jsonl", [{"type": "thread.started", "thread_id": "z"}])
            write_jsonl(root / "A.jsonl", [{"type": "thread.started", "thread_id": "a"}])
            first, _ = extract(root)
            second, _ = extract(root)
            self.assertEqual(first, second)
            expected = [
                session_trace.stable_hash(str((root / "A.jsonl").resolve())),
                session_trace.stable_hash(str((root / "z.jsonl").resolve())),
            ]
            self.assertEqual([item["source"]["source_id_hash"] for item in first], expected)

    def test_summary_reports_coverage_and_missing_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "summary.jsonl"
            write_jsonl(
                path,
                [
                    {"type": "thread.started", "thread_id": "fake"},
                    {"type": "turn.started"},
                    {"type": "turn.completed", "usage": {"input_tokens": 10}},
                ],
            )
            traces, stats = extract(path)
            summary = session_trace.summarize(traces, stats)
            self.assertEqual(summary["totals"]["sessions"], 1)
            self.assertEqual(summary["totals"]["turns"], 1)
            self.assertEqual(summary["totals"]["total_logical_input"], 10)
            self.assertEqual(summary["coverage"]["missing_fields"]["turn.output_tokens"], 1)
            self.assertEqual(summary["coverage"]["record_coverage"], 1.0)

    def test_cli_rejects_known_sensitive_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--input", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("refusing to scan", result.stderr)


if __name__ == "__main__":
    unittest.main()
