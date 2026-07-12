#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("prompt-stats.py")
SPEC = importlib.util.spec_from_file_location("prompt_stats", MODULE_PATH)
assert SPEC and SPEC.loader
prompt_stats = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = prompt_stats
SPEC.loader.exec_module(prompt_stats)


def write_repo(root: Path) -> None:
    (root / "codex" / "agents").mkdir(parents=True)
    (root / "codex" / "skills" / "alpha" / "references").mkdir(parents=True)
    (root / "codex" / "skills" / "alpha" / "templates").mkdir(parents=True)
    (root / "manifests").mkdir(parents=True)

    (root / "AGENTS.md").write_text(
        "# Repository Guidance\n\nAlways verify changes before completion.\n",
        encoding="utf-8",
    )
    (root / "codex" / "AGENTS.md").write_text(
        "# Global Guidance\n\nNever emit secrets.\n",
        encoding="utf-8",
    )
    (root / "codex" / "config.review.toml").write_text(
        'model = "gpt-test"\nmodel_reasoning_effort = "medium"\n',
        encoding="utf-8",
    )
    (root / "codex" / "agents" / "reviewer.toml").write_text(
        '\n'.join(
            [
                'name = "reviewer"',
                'description = "Review focused changes."',
                'model = "gpt-review"',
                'model_reasoning_effort = "high"',
                'developer_instructions = """',
                'You must verify every material claim before reporting completion.',
                '1. Read the artifact.',
                '2. Review the evidence.',
                '"""',
                '',
            ]
        ),
        encoding="utf-8",
    )
    (root / "manifests" / "portable-files.toml").write_text(
        '[agents]\nskills = ["alpha"]\n',
        encoding="utf-8",
    )
    (root / "codex" / "skills" / "alpha" / "SKILL.md").write_text(
        '\n'.join(
            [
                '---',
                'name: alpha',
                'description: "Validate focused work."',
                '---',
                '',
                '# Alpha',
                '',
                'You must verify every material claim before reporting completion.',
                '',
            ]
        ),
        encoding="utf-8",
    )
    (root / "codex" / "skills" / "alpha" / "references" / "rules.md").write_text(
        "# Rules\n\nAlways launch checks from the repository root.\n",
        encoding="utf-8",
    )
    (root / "codex" / "skills" / "alpha" / "templates" / "report.md").write_text(
        "# Report\n\nVerification result: [pass or fail]\n",
        encoding="utf-8",
    )


class PromptStatsTests(unittest.TestCase):
    def test_report_discovers_surfaces_and_agent_routing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            report = prompt_stats.build_report(prompt_stats.parse_args(["--root", str(root)]))
            paths = {surface["path"]: surface for surface in report["surfaces"]}
            self.assertEqual(report["summary"]["files"], 7)
            self.assertEqual(paths["codex/AGENTS.md"]["activation"], "always_loaded")
            self.assertEqual(paths["codex/skills/alpha/SKILL.md"]["category"], "skill")
            self.assertEqual(paths["codex/skills/alpha/references/rules.md"]["category"], "reference")
            self.assertEqual(paths["codex/skills/alpha/templates/report.md"]["category"], "template")
            self.assertEqual(
                report["routing"],
                [
                    {
                        "name": "reviewer",
                        "path": "codex/agents/reviewer.toml",
                        "model": "gpt-review",
                        "reasoning_effort": "high",
                    }
                ],
            )

    def test_steering_and_duplicate_detection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            report = prompt_stats.build_report(
                prompt_stats.parse_args(
                    ["--root", str(root), "--duplicate-threshold", "1.0"]
                )
            )
            agent = next(
                surface for surface in report["surfaces"] if surface["path"] == "codex/agents/reviewer.toml"
            )
            self.assertEqual(agent["strong_steering"]["terms"]["must"], 1)
            self.assertEqual(agent["strong_steering"]["terms"]["numbered"], 2)
            self.assertGreaterEqual(report["summary"]["strong_steering_clauses"], 4)
            duplicates = report["findings"]["duplicate_pairs"]
            self.assertEqual(len(duplicates), 1)
            self.assertEqual(duplicates[0]["similarity"], 1.0)
            self.assertIn("verify every material claim", duplicates[0]["label"])

    def test_check_fails_only_for_budget_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            args = prompt_stats.parse_args(
                [
                    "--root",
                    str(root),
                    "--global-budget",
                    "1",
                    "--agent-total-budget",
                    "1",
                    "--agent-file-budget",
                    "1",
                    "--skill-routing-budget",
                    "1",
                    "--selected-skill-budget",
                    "1",
                ]
            )
            report = prompt_stats.build_report(args)
            self.assertTrue(report["check_failed"])
            self.assertGreaterEqual(len(report["findings"]["budget_warnings"]), 4)
            with redirect_stdout(StringIO()):
                self.assertEqual(
                    prompt_stats.main(
                        [
                            "--root",
                            str(root),
                            "--check",
                            "--global-budget",
                            "1",
                            "--agent-total-budget",
                            "1",
                            "--agent-file-budget",
                            "1",
                            "--skill-routing-budget",
                            "1",
                            "--selected-skill-budget",
                            "1",
                        ]
                    ),
                    1,
                )

    def test_json_is_stable_and_does_not_emit_prompt_bodies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            report = prompt_stats.build_report(prompt_stats.parse_args(["--root", str(root)]))
            encoded = json.dumps(report, sort_keys=True)
            self.assertNotIn("Read the artifact", encoded)
            self.assertNotIn(str(root), encoded)
            self.assertIn('"schema_version": 1', encoded)

    def test_manifest_skill_cannot_escape_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            outside = Path(directory) / "outside"
            (root / "manifests").mkdir(parents=True)
            outside.mkdir()
            (root / "manifests" / "portable-files.toml").write_text(
                '[agents]\nskills = ["../outside"]\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "single path components"):
                prompt_stats.discover_surfaces(root)

    def test_user_facing_text_uses_plain_hyphens(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            report = prompt_stats.build_report(prompt_stats.parse_args(["--root", str(root)]))
            rendered = prompt_stats.render_text(report)
            self.assertNotIn("\u2013", rendered)
            self.assertNotIn("\u2014", rendered)
            self.assertIn("agent routing", rendered)


if __name__ == "__main__":
    unittest.main()
