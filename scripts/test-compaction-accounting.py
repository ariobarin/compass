#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("compaction-accounting.py")
SPEC = importlib.util.spec_from_file_location("compaction_accounting", MODULE_PATH)
assert SPEC and SPEC.loader
compaction_accounting = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = compaction_accounting
SPEC.loader.exec_module(compaction_accounting)


def document(events: list[dict[str, object]]) -> dict[str, object]:
    return {"schema_version": 2, "kind": "session_trace", "events": events}


class CompactionAccountingTests(unittest.TestCase):
    def test_cache_ineligible_prompts_do_not_seed_reuse(self) -> None:
        source = document(
            [
                {
                    "seq": 1,
                    "kind": "turn",
                    "active_context_tokens": 800,
                    "input_tokens": 800,
                    "output_tokens": 0,
                    "tool_output_tokens": 0,
                },
                {
                    "seq": 2,
                    "kind": "turn",
                    "active_context_tokens": 900,
                    "input_tokens": 900,
                    "output_tokens": 0,
                    "tool_output_tokens": 0,
                },
            ]
        )
        report = compaction_accounting.build_report(
            [source], [10000], 20000, 1024, "fixed", 100, 0.2
        )
        accounting = report["thresholds"][0]["input_accounting"]
        self.assertEqual(accounting["uncached_input"], 1700)
        self.assertEqual(accounting["estimated_cache_read"], 0)
        self.assertEqual(accounting["estimated_cache_write"], 0)

    def test_turn_level_compaction_keeps_retained_additions_in_baseline(self) -> None:
        source = document(
            [
                {
                    "seq": 1,
                    "kind": "turn",
                    "active_context_tokens": 10000,
                    "input_tokens": 10000,
                    "output_tokens": 1000,
                    "tool_output_tokens": 500,
                    "pre_compaction_tokens": 10000,
                    "post_compaction_tokens": 2000,
                },
                {
                    "seq": 2,
                    "kind": "turn",
                    "active_context_tokens": 3800,
                    "input_tokens": 3800,
                    "output_tokens": 0,
                    "tool_output_tokens": 0,
                },
            ]
        )
        derived = compaction_accounting.derive_session(source)
        self.assertEqual(derived.turns[0].retained_output, 1500)
        self.assertEqual(derived.turns[1].external_growth, 300)

    def test_lower_threshold_never_has_fewer_compactions_for_same_trace(self) -> None:
        source = document(
            [
                {
                    "seq": index,
                    "kind": "turn",
                    "active_context_tokens": context,
                    "input_tokens": context,
                    "output_tokens": 1000,
                    "tool_output_tokens": 500,
                }
                for index, context in enumerate((10000, 18000, 28000, 40000, 55000), 1)
            ]
        )
        report = compaction_accounting.build_report(
            [source], [20000, 50000], 100000, 1024, "fixed", 1000, 0.2
        )
        low, high = report["thresholds"]
        self.assertGreaterEqual(low["compactions"], high["compactions"])

    def test_report_does_not_claim_semantic_or_decision_precision(self) -> None:
        source = document(
            [
                {
                    "seq": 1,
                    "kind": "turn",
                    "active_context_tokens": 5000,
                    "input_tokens": 5000,
                    "output_tokens": 200,
                    "reasoning_tokens": 100,
                    "tool_output_tokens": 50,
                    "forked_context_tokens": 1000,
                }
            ]
        )
        report = compaction_accounting.build_report(
            [source], [4000], 10000, 1024, "fixed", 500, 0.2
        )
        encoded = json.dumps(report, sort_keys=True).lower()
        for banned in ("risk_score", "pareto", "semantic_loss", "confidence"):
            self.assertNotIn(banned, encoded)
        self.assertTrue(report["interpretation"]["mechanical_accounting_only"])
        self.assertFalse(report["interpretation"]["quality_measured"])
        self.assertFalse(report["interpretation"]["recommendation_emitted"])
        output = report["thresholds"][0]["output_accounting"]
        self.assertEqual(output["retained_root_context_additions"], 250)
        self.assertEqual(output["child_inherited_context"], 1000)

    def test_non_turn_token_events_feed_replay_and_accounting(self) -> None:
        source = document(
            [
                {
                    "seq": 1,
                    "kind": "turn",
                    "active_context_tokens": 1000,
                    "input_tokens": 1000,
                    "output_tokens": 100,
                },
                {
                    "seq": 2,
                    "kind": "tool",
                    "tool_output_tokens": 400,
                },
                {
                    "seq": 3,
                    "kind": "agent_spawn",
                    "forked_context_tokens": 600,
                },
                {
                    "seq": 4,
                    "kind": "turn",
                    "active_context_tokens": 1200,
                    "input_tokens": 1200,
                    "output_tokens": 0,
                },
                {
                    "seq": 5,
                    "kind": "turn",
                    "active_context_tokens": 1700,
                    "input_tokens": 1700,
                    "output_tokens": 0,
                },
            ]
        )
        report = compaction_accounting.build_report(
            [source], [1500], 10000, 1024, "fixed", 100, 0.2
        )
        threshold = report["thresholds"][0]
        self.assertEqual(threshold["compactions"], 1)
        self.assertEqual(threshold["output_accounting"]["tool_output"], 400)
        self.assertEqual(
            threshold["output_accounting"]["retained_root_context_additions"],
            500,
        )
        self.assertEqual(
            threshold["output_accounting"]["child_inherited_context"], 600
        )
        self.assertEqual(report["coverage"]["non_turn_events_with_tool_output"], 1)
        self.assertEqual(
            report["coverage"]["non_turn_events_with_forked_context"], 1
        )

    def test_trailing_native_events_remain_in_output_accounting(self) -> None:
        source = document(
            [
                {
                    "seq": 1,
                    "kind": "turn",
                    "active_context_tokens": 1000,
                    "input_tokens": 1000,
                    "output_tokens": 100,
                },
                {"seq": 2, "kind": "tool", "tool_output_tokens": 250},
                {
                    "seq": 3,
                    "kind": "agent_spawn",
                    "forked_context_tokens": 700,
                },
            ]
        )
        report = compaction_accounting.build_report(
            [source], [5000], 10000, 1024, "fixed", 100, 0.2
        )
        output = report["thresholds"][0]["output_accounting"]
        self.assertEqual(output["tool_output"], 250)
        self.assertEqual(output["retained_root_context_additions"], 350)
        self.assertEqual(output["child_inherited_context"], 700)

    def test_turn_aggregate_deduplicates_native_event_signal(self) -> None:
        source = document(
            [
                {"seq": 1, "kind": "tool", "tool_output_tokens": 400},
                {
                    "seq": 2,
                    "kind": "agent_spawn",
                    "forked_context_tokens": 600,
                },
                {
                    "seq": 3,
                    "kind": "turn",
                    "active_context_tokens": 1000,
                    "input_tokens": 1000,
                    "output_tokens": 100,
                    "tool_output_tokens": 400,
                    "forked_context_tokens": 600,
                },
            ]
        )
        report = compaction_accounting.build_report(
            [source], [5000], 10000, 1024, "fixed", 100, 0.2
        )
        output = report["thresholds"][0]["output_accounting"]
        self.assertEqual(output["tool_output"], 400)
        self.assertEqual(output["retained_root_context_additions"], 500)
        self.assertEqual(output["child_inherited_context"], 600)

    def test_empirical_mode_uses_observed_pairs(self) -> None:
        source = document(
            [
                {
                    "seq": 1,
                    "kind": "compaction",
                    "pre_compaction_tokens": 10000,
                    "post_compaction_tokens": 2000,
                },
                {
                    "seq": 2,
                    "kind": "turn",
                    "active_context_tokens": 2500,
                    "input_tokens": 2500,
                    "output_tokens": 0,
                    "tool_output_tokens": 0,
                },
            ]
        )
        report = compaction_accounting.build_report(
            [source], [2000], 10000, 1024, "empirical", 1, 0.9
        )
        self.assertEqual(report["model"]["mode"], "empirical")
        self.assertEqual(report["model"]["observed_compactions"], 1)
        self.assertAlmostEqual(report["model"]["ratio"], 0.2)


if __name__ == "__main__":
    unittest.main()
