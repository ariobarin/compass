#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
import json
import statistics
import subprocess
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("compaction-sim.py")
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "compaction-sim"
SPEC = importlib.util.spec_from_file_location("compaction_sim", MODULE_PATH)
assert SPEC and SPEC.loader
compaction_sim = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = compaction_sim
SPEC.loader.exec_module(compaction_sim)


class CompactionSimulatorTests(unittest.TestCase):
    def report(self, fixture: str, *arguments: str) -> dict[str, object]:
        args = compaction_sim.parse_args(
            [str(FIXTURE_ROOT / fixture), *arguments]
        )
        return compaction_sim.build_report(args)

    @staticmethod
    def by_threshold(report: dict[str, object]) -> dict[int, dict[str, object]]:
        results = report["results"]
        assert isinstance(results, list)
        return {int(result["threshold"]): result for result in results}

    def test_lower_thresholds_compact_more_and_carry_less_context(self) -> None:
        report = self.report(
            "growth.jsonl",
            "--thresholds",
            "32000,96000",
            "--exclude-baseline",
            "--compaction-mode",
            "fixed",
        )
        results = self.by_threshold(report)
        low = results[32_000]
        high = results[96_000]
        self.assertGreater(low["compactions"], high["compactions"])
        self.assertLess(low["average_context"], high["average_context"])
        self.assertLess(low["maximum_context"], high["maximum_context"])

    def test_compaction_prefix_resets_add_cache_writes(self) -> None:
        report = self.report(
            "growth.jsonl",
            "--thresholds",
            "32000,96000",
            "--exclude-baseline",
            "--compaction-mode",
            "fixed",
        )
        results = self.by_threshold(report)
        self.assertGreater(results[32_000]["cache_writes"], results[96_000]["cache_writes"])
        self.assertGreater(results[32_000]["compactions"], 0)
        self.assertEqual(results[96_000]["compactions"], 0)

    def test_empirical_mode_uses_observed_median_ratio(self) -> None:
        traces = compaction_sim.load_traces(FIXTURE_ROOT / "observed-compactions.jsonl")
        observations = compaction_sim.calibration_observations(traces)
        model = compaction_sim.build_compaction_model(
            requested_mode="empirical",
            observations=observations,
            fixed_overhead=2_000.0,
            fixed_ratio=0.12,
            recent_tail_weight=0.5,
        )
        expected = statistics.median(
            observation.post_size / observation.pre_size
            for observation in observations
        )
        self.assertEqual(model.used_mode, "empirical")
        self.assertEqual(model.calibration_observations, 6)
        self.assertAlmostEqual(model.ratio, expected)

    def test_auto_mode_fits_when_enough_observations_exist(self) -> None:
        report = self.report(
            "observed-compactions.jsonl",
            "--thresholds",
            "32000",
            "--exclude-baseline",
        )
        model = report["compaction_model"]
        assert isinstance(model, dict)
        self.assertEqual(model["used_mode"], "fitted")
        self.assertEqual(model["calibration_observations"], 6)

    def test_uncached_input_weight_is_configurable(self) -> None:
        neutral = self.report(
            "growth.jsonl",
            "--thresholds",
            "96000",
            "--exclude-baseline",
            "--compaction-mode",
            "fixed",
        )
        zero_weight = self.report(
            "growth.jsonl",
            "--thresholds",
            "96000",
            "--exclude-baseline",
            "--compaction-mode",
            "fixed",
            "--uncached-input-weight",
            "0",
        )
        neutral_result = self.by_threshold(neutral)[96_000]
        zero_result = self.by_threshold(zero_weight)[96_000]
        self.assertEqual(
            neutral_result["usage_score"] - zero_result["usage_score"],
            neutral_result["uncached_input"],
        )

    def test_partial_traces_reduce_confidence(self) -> None:
        complete = self.report(
            "growth.jsonl",
            "--thresholds",
            "64000",
            "--exclude-baseline",
            "--compaction-mode",
            "fixed",
        )
        partial = self.report(
            "partial.jsonl",
            "--thresholds",
            "64000",
            "--exclude-baseline",
            "--compaction-mode",
            "fixed",
        )
        complete_confidence = complete["confidence"]
        partial_confidence = partial["confidence"]
        assert isinstance(complete_confidence, dict)
        assert isinstance(partial_confidence, dict)
        self.assertLess(partial_confidence["score"], complete_confidence["score"])
        self.assertNotEqual(partial_confidence["level"], "high")
        self.assertLess(partial_confidence["coverage"]["cache"], 1.0)

    def test_pareto_frontier_is_deterministic(self) -> None:
        results = [
            {"threshold": 64_000, "usage_score": 10.0, "risk_score": 5.0},
            {"threshold": 96_000, "usage_score": 12.0, "risk_score": 4.0},
            {"threshold": 128_000, "usage_score": 11.0, "risk_score": 6.0},
            {"threshold": 32_000, "usage_score": 9.0, "risk_score": 7.0},
        ]
        expected = [32_000, 64_000, 96_000]
        self.assertEqual(compaction_sim.pareto_frontier(results), expected)
        self.assertEqual(compaction_sim.pareto_frontier(list(reversed(results))), expected)

    def test_compatible_baseline_is_included(self) -> None:
        self.assertIn(
            compaction_sim.BASELINE_THRESHOLD,
            compaction_sim.parse_thresholds("64000", 272_000, True),
        )
        self.assertNotIn(
            compaction_sim.BASELINE_THRESHOLD,
            compaction_sim.parse_thresholds("64000", 200_000, True),
        )

    def test_cli_directory_json_is_deterministic(self) -> None:
        command = [
            sys.executable,
            str(MODULE_PATH),
            str(FIXTURE_ROOT),
            "--thresholds",
            "32000,48000,96000",
            "--exclude-baseline",
            "--json",
        ]
        first = subprocess.run(command, check=True, capture_output=True, text=True)
        second = subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertEqual(first.stdout, second.stdout)
        payload = json.loads(first.stdout)
        self.assertEqual(payload["schema_version"], 1)
        self.assertTrue(payload["pareto_frontier"])

    def test_simulator_has_no_model_or_network_dependencies(self) -> None:
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        forbidden_roots = {
            "aiohttp",
            "httpx",
            "openai",
            "requests",
            "socket",
            "urllib",
        }
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertFalse(imported_roots & forbidden_roots)


if __name__ == "__main__":
    unittest.main()
