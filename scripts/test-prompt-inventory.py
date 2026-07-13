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

MODULE_PATH = Path(__file__).with_name("prompt-inventory.py")
SPEC = importlib.util.spec_from_file_location("prompt_inventory", MODULE_PATH)
assert SPEC and SPEC.loader
prompt_inventory = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = prompt_inventory
SPEC.loader.exec_module(prompt_inventory)


def write_repo(root: Path) -> None:
    (root / "manifests").mkdir(parents=True)
    (root / "codex" / "agents").mkdir(parents=True)
    (root / "codex" / "skills" / "alpha" / "agents").mkdir(parents=True)
    (root / "codex" / "skills" / "alpha" / "references").mkdir(parents=True)
    (root / "AGENTS.md").write_text(
        "PRIVATE GLOBAL PROMPT BODY\n", encoding="utf-8"
    )
    (root / "manifests" / "portable-files.toml").write_text(
        '[agents]\nskills = ["alpha"]\n', encoding="utf-8"
    )
    (root / "codex" / "agents" / "critic.toml").write_text(
        '\n'.join(
            [
                'name = "critic"',
                'description = "Review the artifact."',
                'model = "gpt-test"',
                'model_reasoning_effort = "high"',
                'developer_instructions = """PRIVATE AGENT BODY"""',
                '',
            ]
        ),
        encoding="utf-8",
    )
    (root / "codex" / "skills" / "alpha" / "SKILL.md").write_text(
        "---\nname: alpha\ndescription: Validate alpha artifacts.\n---\n\nPRIVATE SKILL BODY\n",
        encoding="utf-8",
    )
    (root / "codex" / "skills" / "alpha" / "agents" / "openai.yaml").write_text(
        'interface:\n  default_prompt: "PRIVATE DEFAULT PROMPT"\n',
        encoding="utf-8",
    )
    (root / "codex" / "skills" / "alpha" / "references" / "rules.md").write_text(
        "PRIVATE REFERENCE BODY\n", encoding="utf-8"
    )


class PromptInventoryTests(unittest.TestCase):
    def test_inventory_is_descriptive_and_content_free(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            report = prompt_inventory.build_report(root, 4.0)
            paths = {item["path"]: item for item in report["surfaces"]}
            self.assertEqual(report["kind"], "prompt_inventory")
            self.assertIn("codex/skills/alpha/agents/openai.yaml", paths)
            self.assertEqual(paths["codex/agents/critic.toml"]["category"], "agent")
            self.assertEqual(report["agent_routing"][0]["model"], "gpt-test")
            self.assertTrue(report["interpretation"]["size_is_not_quality"])

            encoded = json.dumps(report, sort_keys=True)
            for private_text in (
                "PRIVATE GLOBAL PROMPT BODY",
                "PRIVATE AGENT BODY",
                "PRIVATE SKILL BODY",
                "PRIVATE DEFAULT PROMPT",
                "PRIVATE REFERENCE BODY",
            ):
                self.assertNotIn(private_text, encoded)
            for proxy_name in ("steering_hotspots", "duplicate_pairs", "budgets"):
                self.assertNotIn(proxy_name, encoded)

    def test_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            first = prompt_inventory.build_report(root, 4.0)
            second = prompt_inventory.build_report(root, 4.0)
            self.assertEqual(first, second)
            with redirect_stdout(StringIO()):
                self.assertEqual(prompt_inventory.main(["--root", str(root), "--json"]), 0)

    def test_orchestration_protocol_avoids_magic_status_handshake(self) -> None:
        root = MODULE_PATH.parent.parent
        relative_paths = (
            "codex/skills/orchestration-controller/SKILL.md",
            "codex/skills/orchestration-controller/references/controller-principles.md",
            "codex/skills/subagent-driven-development/SKILL.md",
            "codex/skills/subagent-driven-development/implementer-prompt.md",
        )
        surfaces = {
            relative: (root / relative).read_text(encoding="utf-8")
            for relative in relative_paths
        }
        combined = "\n".join(surfaces.values())
        for sentinel in (
            "CONTINUE",
            "DONE",
            "DONE_WITH_CONCERNS",
            "NEEDS_CONTEXT",
            "BLOCKED",
            "WAITING_ON_REVIEW",
            "NO_RESULTS",
        ):
            self.assertNotRegex(combined, rf"\b{sentinel}\b")

        self.assertIn("continuation", combined.lower())
        self.assertIn("does not suspend", combined.lower())
        self.assertIn(
            "Return kind: completed | needs_input | waiting_external | failed",
            surfaces[
                "codex/skills/subagent-driven-development/implementer-prompt.md"
            ],
        )

    def test_manifest_skill_cannot_escape_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manifests").mkdir(parents=True)
            (root / "manifests" / "portable-files.toml").write_text(
                '[agents]\nskills = ["../outside"]\n', encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "single path components"):
                prompt_inventory.build_report(root, 4.0)


if __name__ == "__main__":
    unittest.main()
