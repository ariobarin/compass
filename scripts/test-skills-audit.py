#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("skills-audit.py")
SPEC = importlib.util.spec_from_file_location("skills_audit", MODULE_PATH)
assert SPEC and SPEC.loader
skills_audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = skills_audit
SPEC.loader.exec_module(skills_audit)


def write_skill(root: Path, name: str, description: str, body: str = "Do the work.") -> Path:
    skill = root / name
    skill.mkdir(parents=True, exist_ok=True)
    path = skill / "SKILL.md"
    path.write_text(
        f'---\nname: {name}\ndescription: "{description}"\n---\n\n# {name}\n\n{body}\n',
        encoding="utf-8",
    )
    return path


def write_repo(root: Path, names: list[str]) -> None:
    (root / "manifests").mkdir(parents=True)
    lines = ["[agents]", "skills = ["] + [f'  "{name}",' for name in names] + ["]"]
    (root / "manifests" / "portable-files.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for name in names:
        write_skill(root / "codex" / "skills", name, f"Use {name} for focused work.")


class SkillAuditTests(unittest.TestCase):
    def test_parse_frontmatter_supports_folded_description(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(
                "---\nname: sample\ndescription: >\n  First line\n  second line\n---\nBody\n",
                encoding="utf-8",
            )
            skill = skills_audit.parse_frontmatter(path)
            self.assertIsNotNone(skill)
            assert skill
            self.assertEqual(skill.description, "First line second line")

    def test_report_finds_external_same_name_collision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            write_repo(root, ["alpha", "beta"])
            external = Path(directory) / "external"
            write_skill(external, "alpha", "Different alpha implementation.")
            args = skills_audit.parse_args(
                ["--root", str(root), "--no-live", "--skill-root", f"external={external}"]
            )
            report = skills_audit.build_report(args)
            self.assertEqual(report["budget"]["included_skills"], 2)
            self.assertEqual(report["findings"]["exact_name_collisions"][0]["name"], "alpha")
            self.assertTrue(report["check_failed"])

    def test_live_prompt_reports_unowned_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            write_repo(root, ["alpha"])
            prompt_file = Path(directory) / "prompt.json"
            prompt = "\n".join(
                [
                    "<skills_instructions>",
                    "### Skill roots",
                    f"- `r1` = `{root / 'codex' / 'skills'}`",
                    "### Available skills",
                    "- alpha: Alpha work. (file: r1/alpha/SKILL.md)",
                    "- extra: Extra work. (file: /missing/extra/SKILL.md)",
                    "### How to use skills",
                    "</skills_instructions>",
                ]
            )
            prompt_file.write_text(json.dumps({"nested": {"prompt": prompt}}), encoding="utf-8")
            args = skills_audit.parse_args(
                ["--root", str(root), "--live-prompt", str(prompt_file)]
            )
            report = skills_audit.build_report(args)
            self.assertEqual(report["inventory_mode"], "live")
            self.assertEqual(report["findings"]["loaded_unowned"], ["extra"])

    def test_usage_scan_returns_counts_without_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "history.jsonl"
            log.write_text("use $alpha now\nread /tmp/skills/beta/SKILL.md\n", encoding="utf-8")
            now = time.time()
            log.touch()
            summary = skills_audit.scan_usage([log], ["alpha", "beta", "gamma"], 90, 1024 * 1024)
            self.assertEqual(summary.hits, {"alpha": 1, "beta": 1, "gamma": 0})
            self.assertEqual(summary.scanned_files, 1)
            self.assertLessEqual(log.stat().st_mtime, now + 1)

    def test_near_duplicate_descriptions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = skills_audit.parse_frontmatter(
                write_skill(root, "first", "Review pull requests with exact current head evidence.")
            )
            second = skills_audit.parse_frontmatter(
                write_skill(root, "second", "Review pull requests with current exact head evidence.")
            )
            assert first and second
            pairs = skills_audit.near_duplicates([first, second], 0.8)
            self.assertEqual(len(pairs), 1)
            self.assertEqual(pairs[0].kind, "description")


if __name__ == "__main__":
    unittest.main()
