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
    def test_copies_only_contract_and_explicit_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "repo"
            source.mkdir()
            (source / "contract.md").write_text("# Contract\n", encoding="utf-8")
            (source / "source.py").write_text("secret implementation\n", encoding="utf-8")
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
            self.assertTrue((output / "fixtures" / "fixtures" / "sample.json").is_file())
            self.assertFalse((output / "source.py").exists())
            self.assertEqual(manifest["schema_version"], 1)
            disk = json.loads((output / "workspace-manifest.json").read_text())
            self.assertEqual(disk["fixtures"][0]["path"], "fixtures/fixtures/sample.json")

    def test_output_must_be_new_and_outside_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "repo"
            source.mkdir()
            (source / "contract.md").write_text("contract", encoding="utf-8")
            with self.assertRaisesRegex(workspace.WorkspaceError, "outside the source root"):
                workspace.build_workspace(
                    source,
                    Path("contract.md"),
                    source / "validator",
                    [],
                )
            output = Path(directory) / "validator"
            output.mkdir()
            with self.assertRaisesRegex(workspace.WorkspaceError, "already exists"):
                workspace.build_workspace(
                    source,
                    Path("contract.md"),
                    output,
                    [],
                )

    def test_rejects_symlink_and_credential_like_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "repo"
            source.mkdir()
            (source / "contract.md").write_text("contract", encoding="utf-8")
            (source / ".env").write_text("TOKEN=value", encoding="utf-8")
            with self.assertRaisesRegex(workspace.WorkspaceError, "credential-bearing"):
                workspace.build_workspace(
                    source,
                    Path("contract.md"),
                    base / "credential-output",
                    [Path(".env")],
                )
            target = source / "target.txt"
            target.write_text("target", encoding="utf-8")
            link = source / "link.txt"
            try:
                link.symlink_to(target)
            except OSError:
                return
            with self.assertRaisesRegex(workspace.WorkspaceError, "symlink"):
                workspace.build_workspace(
                    source,
                    Path("contract.md"),
                    base / "symlink-output",
                    [Path("link.txt")],
                )

    def test_contract_must_stay_under_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "repo"
            source.mkdir()
            outside = base / "contract.md"
            outside.write_text("contract", encoding="utf-8")
            with self.assertRaisesRegex(workspace.WorkspaceError, "escapes source root"):
                workspace.build_workspace(
                    source,
                    outside,
                    base / "validator",
                    [],
                )


if __name__ == "__main__":
    unittest.main()
