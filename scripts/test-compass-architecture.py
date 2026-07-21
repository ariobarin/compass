#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import tomllib
import unittest
from pathlib import Path

from _orchestration_ledger_model import LedgerError, validate_ledger

ROOT = Path(__file__).resolve().parents[1]
MODEL_EFFORT_DEFAULTS = {
    "gpt-5.6-sol": "high",
    "gpt-5.6-terra": "xhigh",
    "gpt-5.6-luna": "high",
}

MAX_SKILL_DESCRIPTION_LENGTH = 160


class CompassArchitectureTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def manifest(self) -> dict[str, object]:
        with (ROOT / "manifests" / "portable-files.toml").open("rb") as handle:
            return tomllib.load(handle)

    def test_installed_skill_set_matches_current_architecture(self) -> None:
        manifest = self.manifest()
        skills = set(manifest["agents"]["skills"])
        self.assertIn("run-a-micro-experiment", skills)
        self.assertIn("using-goals", skills)
        self.assertIn("which-llm", skills)
        self.assertIn("write-a-compass-skill", skills)
        self.assertIn("write-a-skill", skills)
        self.assertNotIn("benchmark-run-operator", skills)
        self.assertNotIn("input-token-economy", skills)
        self.assertNotIn("using-codex-goals", skills)

        for skill in skills:
            self.assertTrue((ROOT / "codex" / "skills" / skill / "SKILL.md").is_file(), skill)

        carried = ROOT / "carried" / "benchmark" / "skills" / "benchmark-run-operator" / "SKILL.md"
        self.assertTrue(carried.is_file())

    def test_runtime_globals_are_separate_and_truthful(self) -> None:
        manifest = self.manifest()
        self.assertEqual(manifest["claude"]["files"], ["CLAUDE.md"])

        codex = self.read("codex/AGENTS.md")
        claude = self.read("claude/CLAUDE.md")
        mcp = self.read("apps/compass-mcp/profile.md")

        self.assertIn("GPT-5.6 Sol", codex)
        self.assertIn("GPT-5.6 Luna", codex)
        self.assertNotIn("GPT-5.6 Terra", codex)
        self.assertNotIn("GLM-5.2", codex)

        self.assertIn("GLM-5.2", claude)
        self.assertNotIn("GPT-5.6 Sol", claude)
        self.assertNotIn("GPT-5.6 Luna", claude)

        self.assertNotRegex(mcp, r"GPT-5\.6 (?:Sol|Luna|Terra)|GLM-5\.2")

    def test_model_tier_defaults_are_documented_and_applied(self) -> None:
        with (ROOT / "codex" / "config.review.toml").open("rb") as handle:
            config = tomllib.load(handle)
        model = config["model"]
        self.assertEqual(config["model_reasoning_effort"], MODEL_EFFORT_DEFAULTS[model])

        calibration = self.read("local-docs/model-calibration.md")
        for model_name, effort in (
            ("GPT-5.6 Sol", "high"),
            ("GPT-5.6 Terra", "xhigh"),
            ("GPT-5.6 Luna", "high"),
        ):
            self.assertIn(f"| {model_name} | `{effort}` |", calibration)

    def test_current_ledger_schema_does_not_backfill_legacy_fields(self) -> None:
        timestamp = "2026-07-17T12:00:00Z"
        goal = {
            "id": "strict-v4",
            "goal": "Reject malformed current records",
            "anchors": ["product-requirements.md"],
            "control_documents": ["local-docs/control/goal.md"],
            "phase": "planning",
            "execution_owner": "principal",
            "worker_id": None,
            "state": "planned",
            "next_action": None,
            "next_check_at": None,
            "evidence": [],
            "public_mutation_gate": "closed",
            "public_mutation_action": None,
            "decision_needed": None,
            "control_writer": "principal",
            "control_revision": 1,
            "recovery_circuits": [],
            "created_at": timestamp,
            "updated_at": timestamp,
            "last_verified_at": timestamp,
        }
        del goal["anchors"]
        current = {"schema_version": 5, "updated_at": timestamp, "goals": [goal]}
        with self.assertRaisesRegex(LedgerError, "missing required fields: anchors"):
            validate_ledger(current)

    def test_ledger_schema_version_rejects_boolean_values(self) -> None:
        invalid = {
            "schema_version": True,
            "updated_at": "2026-07-17T12:00:00Z",
            "goals": [],
        }
        with self.assertRaisesRegex(LedgerError, "requires schema_version 5"):
            validate_ledger(invalid)

    def test_legacy_recovery_counter_rejects_malformed_values(self) -> None:
        timestamp = "2026-07-17T12:00:00Z"
        for invalid_count in (True, -1, "two"):
            with self.subTest(invalid_count=invalid_count):
                legacy = {
                    "schema_version": 2,
                    "updated_at": timestamp,
                    "goals": [
                        {
                            "id": "legacy",
                            "goal": "Reject malformed recovery state",
                            "execution_owner": "principal",
                            "worker_id": None,
                            "state": "active",
                            "next_action": None,
                            "next_check_at": None,
                            "completion_evidence": [],
                            "public_mutation_gate": "closed",
                            "public_mutation_action": None,
                            "decision_needed": None,
                            "control_writer": "principal",
                            "control_revision": 1,
                            "control_edit_grants": [],
                            "recovery_circuits": [
                                {
                                    "slice_label": "api",
                                    "consecutive_successor_failures": invalid_count,
                                    "state": "open",
                                    "last_reset_evidence": None,
                                    "last_reset_at": None,
                                    "claimed_by": None,
                                }
                            ],
                            "created_at": timestamp,
                            "updated_at": timestamp,
                        }
                    ],
                }
                with self.assertRaisesRegex(LedgerError, "unsupported fields"):
                    validate_ledger(legacy)

    def test_codex_agents_follow_luna_first_profile(self) -> None:
        for path in sorted((ROOT / "codex" / "agents").glob("*.toml")):
            with path.open("rb") as handle:
                agent = tomllib.load(handle)
            self.assertEqual(agent.get("model"), "gpt-5.6-luna", path.name)
            self.assertNotIn("service_tier", agent, path.name)
            effort = agent.get("model_reasoning_effort")
            self.assertIn(effort, {"high", "xhigh", "max"}, path.name)

    def test_principal_authorship_is_consistent(self) -> None:
        for relative in (
            "philosophy.md",
            "workflows/long-running-work.md",
            "codex/skills/using-goals/SKILL.md",
            "codex/skills/orchestration-controller/SKILL.md",
            "codex/skills/subagent-driven-development/SKILL.md",
            "workflows/orchestration-ledger.md",
        ):
            text = self.read(relative)
            self.assertRegex(text, r"(?i)principal")
            self.assertRegex(text, r"(?i)return(?:s|ed)? (?:artifacts (?:plus|and) )?evidence|return evidence")

        ledger = self.read("workflows/orchestration-ledger.md")
        self.assertRegex(ledger.lower(), r"does not\s+support delegated edit grants")
        self.assertNotIn("set-grant", ledger)
        self.assertNotIn("claim-successor", ledger)

    def test_long_running_work_has_complete_control_templates(self) -> None:
        for name in ("goal", "plan", "catalog", "assignment", "decision", "checkpoint"):
            self.assertTrue((ROOT / "workflows" / "templates" / f"{name}.md").is_file(), name)

    def test_workspace_template_has_distinct_lifecycles_and_templates(self) -> None:
        base = ROOT / "codex" / "skills" / "workspace-steward" / "references" / "project-template"
        required = (
            "README.md",
            "AGENTS.md",
            "CLAUDE.md",
            "glossary.md",
            "experiments/README.md",
            "experiments/TEMPLATE.md",
            "worktrees/README.md",
            "worktrees/prs/README.md",
            "worktrees/spikes/README.md",
            "local-docs/README.md",
            "local-docs/goals/TEMPLATE.md",
            "local-docs/plans/TEMPLATE.md",
            "local-docs/catalogs/TEMPLATE.md",
            "local-docs/assignments/TEMPLATE.md",
            "local-docs/checkpoints/TEMPLATE.md",
            "local-docs/decisions/TEMPLATE.md",
        )
        for relative in required:
            self.assertTrue((base / relative).is_file(), relative)

        experiment = (base / "experiments" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Experimental code does not graduate. The finding graduates.", experiment)

    def test_skill_descriptions_are_routable_and_bounded(self) -> None:
        skill_files = list((ROOT / "codex" / "skills").glob("*/SKILL.md"))
        skill_files += list((ROOT / "carried").glob("*/skills/*/SKILL.md"))
        seen: set[str] = set()
        for path in sorted(skill_files):
            text = path.read_text(encoding="utf-8")
            match = re.match(r"^---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
            self.assertIsNotNone(match, path)
            header = match.group("header")
            name_match = re.search(r"^name:\s*(.+)$", header, re.MULTILINE)
            description_match = re.search(r"^description:\s*(.+)$", header, re.MULTILINE)
            self.assertIsNotNone(name_match, path)
            self.assertIsNotNone(description_match, path)
            name = name_match.group(1).strip().strip('"\'')
            description = description_match.group(1).strip().strip('"\'')
            self.assertEqual(name, path.parent.name, path)
            self.assertNotIn(name.casefold(), seen, path)
            seen.add(name.casefold())
            self.assertLessEqual(len(description), MAX_SKILL_DESCRIPTION_LENGTH, path)

    def test_powershell_ledger_wrapper_uses_script_arguments(self) -> None:
        wrapper = self.read("scripts/orchestration-ledger.ps1")
        self.assertNotIn('$PSBoundParameters.ContainsKey("Actor")', wrapper)
        self.assertIn('[string]::IsNullOrWhiteSpace($Actor)', wrapper)
        self.assertIn('$null -eq $ExpectedRevision', wrapper)

    def test_skill_interface_prompts_match_current_architecture(self) -> None:
        prompt_files = list((ROOT / "codex" / "skills").glob("*/agents/openai.yaml"))
        prompt_files += list((ROOT / "carried").glob("*/skills/*/agents/openai.yaml"))
        for path in prompt_files:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("@codex", text, path)
            self.assertNotIn("using-codex-goals", text, path)
            self.assertNotIn("input-token-economy", text, path)

    def test_retirement_map_names_every_replaced_global_surface(self) -> None:
        manifest = self.read("manifests/retired-skills.json")
        for retired in (
            "benchmark-run-operator",
            "input-token-economy",
            "using-codex-goals",
            "benchmark-infra-reviewer.md",
        ):
            self.assertIn(retired, manifest)

    def test_retired_skill_manifest_matches_expected_retirement_sets(self) -> None:
        manifest = json.loads(self.read("manifests/retired-skills.json"))
        self.assertEqual(manifest["schema_version"], 1)
        expected = {
            "codex_home_skills": [
                "benchmark-run-operator",
                "codex-portable",
                "input-token-economy",
                "pr-merge-closeout",
                "proper-flowcharts",
                "ui-ux-pro-max",
                "using-codex-goals",
            ],
            "user_skills_home": [
                "benchmark-infra-reviewer",
                "benchmark-run-operator",
                "input-token-economy",
                "pr-merge-closeout",
                "ui-ux-pro-max",
                "using-codex-goals",
                "webmcp-eval-triage",
                "webmcp-tool-authoring",
                "webmcp-verify-tool",
            ],
            "claude_skills": [
                "benchmark-infra-reviewer",
                "benchmark-run-operator",
                "input-token-economy",
                "using-codex-goals",
            ],
            "claude_agents": [
                "benchmark-infra-reviewer.md",
            ],
        }
        for key, value in expected.items():
            self.assertEqual(manifest[key], value)

    def test_skill_description_cap_matches_shared_constant(self) -> None:
        common = self.read("scripts/common.ps1")
        match = re.search(r"MaxSkillDescriptionLength\s*=\s*(\d+)", common)
        self.assertIsNotNone(
            match,
            "scripts/common.ps1 must define $script:MaxSkillDescriptionLength",
        )
        self.assertEqual(int(match.group(1)), MAX_SKILL_DESCRIPTION_LENGTH)


if __name__ == "__main__":
    unittest.main()
