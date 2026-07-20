#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("validate-skill-sources.py")
SPEC = importlib.util.spec_from_file_location("validate_skill_sources", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def write_repo(root: Path, records: list[dict], installed: list[str], derived: list[str] | None = None) -> None:
    (root / "manifests").mkdir(parents=True)
    derived = derived or []
    portable = ["[agents]", "skills = ["]
    portable.extend(f'  "{name}",' for name in installed)
    portable.extend(["]", "", "[claude]", "skills = []", "derived_skills = ["])
    portable.extend(f'  "{name}",' for name in derived)
    portable.append("]")
    (root / "manifests" / "portable-files.toml").write_text("\n".join(portable) + "\n", encoding="utf-8")
    (root / "manifests" / "skill-sources.json").write_text(
        json.dumps({"schema_version": 1, "skills": records}, indent=2) + "\n",
        encoding="utf-8",
    )
    for record in records:
        source = root / record.get("source", "missing")
        if ".." in Path(record.get("source", "")).parts:
            continue
        source.mkdir(parents=True, exist_ok=True)
        (source / "SKILL.md").write_text(
            f'---\nname: {record.get("name", "")}\ndescription: "test"\n---\nBody\n',
            encoding="utf-8",
        )


def record(name: str, claude: str = "none") -> dict:
    return {
        "name": name,
        "owner": "compass",
        "source": f"codex/skills/{name}",
        "profile": "default",
        "targets": {"codex": "copy", "claude": claude},
    }


class SkillSourceTests(unittest.TestCase):
    def validate(self, root: Path):
        return module.validate(
            root.resolve(),
            root / "manifests" / "skill-sources.json",
            root / "manifests" / "portable-files.toml",
        )

    def test_valid_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root, [record("alpha", "derived")], ["alpha"], ["alpha"])
            problems, records = self.validate(root)
            self.assertEqual(problems, [])
            self.assertEqual(records[0]["owner"], "compass")

    def test_missing_record_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root, [record("alpha")], ["alpha", "beta"])
            problems, _ = self.validate(root)
            self.assertIn("portable skills missing source records: beta", problems)

    def test_claude_target_must_match_portable_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root, [record("alpha", "none")], ["alpha"], ["alpha"])
            problems, _ = self.validate(root)
            self.assertTrue(any("expected derived" in problem for problem in problems))

    def test_source_cannot_escape_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bad = record("alpha")
            bad["source"] = "../alpha"
            write_repo(root, [bad], ["alpha"])
            problems, _ = self.validate(root)
            self.assertTrue(any("source must stay under" in problem for problem in problems))

    def test_external_upstream_requires_review_proof(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            external = record("alpha")
            external["owner"] = "openclaw/agent-skills"
            external["upstream"] = {
                "repository": "openclaw/agent-skills",
                "reviewed_ref": "abc123",
                "source_sha256": "0" * 64,
            }
            write_repo(root, [external], ["alpha"])
            external["upstream"]["source_sha256"] = module.source_tree_sha256(
                root / external["source"]
            )
            (root / "manifests" / "skill-sources.json").write_text(
                json.dumps({"schema_version": 1, "skills": [external]}, indent=2) + "\n",
                encoding="utf-8",
            )
            problems, _ = self.validate(root)
            self.assertEqual(problems, [])

    def test_source_hash_uses_portable_relative_path_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            files = {
                "SKILL.md": b"skill",
                "a/b.md": b"nested",
                "a.b.md": b"flat",
                "references/upstream.md": b"upstream",
            }
            for relative, content in files.items():
                target = source / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)

            expected = hashlib.sha256()
            for relative in sorted(files):
                relative_bytes = relative.encode("utf-8")
                expected.update(len(relative_bytes).to_bytes(8, "big"))
                expected.update(relative_bytes)
                content = files[relative]
                expected.update(len(content).to_bytes(8, "big"))
                expected.update(content)

            self.assertEqual(module.source_tree_sha256(source), expected.hexdigest())

    def test_source_hash_changes_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "SKILL.md").write_text("one", encoding="utf-8")
            first = module.source_tree_sha256(source)
            (source / "SKILL.md").write_text("two", encoding="utf-8")
            second = module.source_tree_sha256(source)
            self.assertNotEqual(first, second)

    def test_source_hash_ignores_python_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "SKILL.md").write_text("skill", encoding="utf-8")
            expected = module.source_tree_sha256(source)

            cache = source / "__pycache__"
            cache.mkdir()
            (cache / "helper.cpython-312.pyc").write_bytes(b"generated")
            (source / "helper.pyc").write_bytes(b"generated")
            (source / "helper.pyo").write_bytes(b"generated")

            self.assertEqual(module.source_tree_sha256(source), expected)


if __name__ == "__main__":
    unittest.main()
