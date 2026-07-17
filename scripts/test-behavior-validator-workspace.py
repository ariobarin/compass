#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "codex"
    / "skills"
    / "behavior-validator"
    / "scripts"
    / "prepare-workspace.py"
)
SPEC = importlib.util.spec_from_file_location("prepare_workspace", MODULE_PATH)
assert SPEC and SPEC.loader
workspace = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = workspace
SPEC.loader.exec_module(workspace)


class BehaviorWorkspaceTests(unittest.TestCase):
    def make_source(self, base: Path) -> Path:
        source = base / "repo"
        source.mkdir()
        (source / "contract.md").write_text("# Contract\n", encoding="utf-8")
        return source

    def test_copies_only_contract_instructions_and_explicit_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            (source / "source.py").write_text("implementation\n", encoding="utf-8")
            fixture = source / "fixtures" / "sample.json"
            fixture.parent.mkdir()
            fixture.write_text('{"ok": true}\n', encoding="utf-8")
            output = base / "validator"

            manifest = workspace.build_workspace(
                source,
                Path("contract.md"),
                output,
                [Path("fixtures/sample.json")],
            )

            self.assertTrue((output / "contract.md").is_file())
            self.assertTrue((output / "AGENTS.md").is_file())
            self.assertTrue((output / "CLAUDE.md").is_file())
            self.assertTrue((output / "fixtures" / "sample.json").is_file())
            self.assertFalse((output / "source.py").exists())
            self.assertEqual(manifest["schema_version"], 2)
            disk = json.loads((output / "workspace-manifest.json").read_text())
            self.assertEqual(disk["fixtures"][0]["path"], "fixtures/sample.json")
            self.assertEqual(
                sorted(path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()),
                sorted(disk["allowed_local_paths"]),
            )

    def test_directory_fixture_preserves_one_stable_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            nested = source / "testdata" / "nested" / "sample.txt"
            nested.parent.mkdir(parents=True)
            nested.write_text("approved fixture\n", encoding="utf-8")
            output = base / "validator"

            workspace.build_workspace(source, Path("contract.md"), output, [Path("testdata")])

            self.assertTrue((output / "fixtures" / "testdata" / "nested" / "sample.txt").is_file())

    def test_output_must_be_new_and_outside_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            with self.assertRaisesRegex(workspace.WorkspaceError, "outside the source root"):
                workspace.build_workspace(source, Path("contract.md"), source / "validator", [])
            output = base / "validator"
            output.mkdir()
            with self.assertRaisesRegex(workspace.WorkspaceError, "already exists"):
                workspace.build_workspace(source, Path("contract.md"), output, [])

    def test_rejects_env_variants_and_sensitive_path_segments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            (source / ".env.production").write_text("TOKEN=value", encoding="utf-8")
            secret = source / "secrets" / "sample.txt"
            secret.parent.mkdir()
            secret.write_text("placeholder", encoding="utf-8")

            with self.assertRaisesRegex(workspace.WorkspaceError, "environment file"):
                workspace.build_workspace(
                    source, Path("contract.md"), base / "env-output", [Path(".env.production")]
                )
            with self.assertRaisesRegex(workspace.WorkspaceError, "blocked directory"):
                workspace.build_workspace(
                    source, Path("contract.md"), base / "secret-output", [Path("secrets/sample.txt")]
                )

    def test_rejects_high_confidence_secret_content_in_ordinary_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            fixture = source / "sample.txt"
            fixture.write_text("github_pat_abcdefghijklmnopqrstuvwxyz1234567890\n", encoding="utf-8")
            with self.assertRaisesRegex(workspace.WorkspaceError, "GitHub fine-grained token"):
                workspace.build_workspace(
                    source, Path("contract.md"), base / "token-output", [Path("sample.txt")]
                )

    def test_rejects_secret_content_in_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            (source / "contract.md").write_text(
                "-----BEGIN PRIVATE KEY-----\nnot-real\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(workspace.WorkspaceError, "contract contains a possible private key"):
                workspace.build_workspace(source, Path("contract.md"), base / "output", [])

    def test_rejects_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            target = source / "target.txt"
            target.write_text("target", encoding="utf-8")
            link = source / "link.txt"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(workspace.WorkspaceError, "symlink"):
                workspace.build_workspace(
                    source, Path("contract.md"), base / "symlink-output", [Path("link.txt")]
                )

    def test_contract_must_stay_under_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            outside = base / "outside-contract.md"
            outside.write_text("contract", encoding="utf-8")
            with self.assertRaisesRegex(workspace.WorkspaceError, "escapes source root"):
                workspace.build_workspace(source, outside, base / "validator", [])

    def test_case_colliding_distinct_fixtures_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            fixtures = source / "fixtures"
            fixtures.mkdir()
            lower = fixtures / "sample.json"
            upper = fixtures / "Sample.json"
            lower.write_text('{"case": "lower"}', encoding="utf-8")
            upper.write_text('{"case": "upper"}', encoding="utf-8")
            if lower.resolve() == upper.resolve():
                self.skipTest("filesystem is case-insensitive")
            with self.assertRaisesRegex(workspace.WorkspaceError, "collide case-insensitively"):
                workspace.build_workspace(
                    source,
                    Path("contract.md"),
                    base / "validator",
                    [Path("fixtures/sample.json"), Path("fixtures/Sample.json")],
                )

    def test_duplicate_fixture_inputs_are_deduplicated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = self.make_source(base)
            fixture = source / "fixtures" / "sample.json"
            fixture.parent.mkdir()
            fixture.write_text("{}", encoding="utf-8")
            output = base / "validator"
            manifest = workspace.build_workspace(
                source,
                Path("contract.md"),
                output,
                [Path("fixtures"), Path("fixtures/sample.json")],
            )
            self.assertEqual(len(manifest["fixtures"]), 1)


if __name__ == "__main__":
    unittest.main()
