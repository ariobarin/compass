#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "codex" / "skills" / "pr-review-loop" / "scripts" / "build-review-bundle.py"
SPEC = importlib.util.spec_from_file_location("build_review_bundle", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def init_repo(root: Path) -> str:
    git(root, "init", "-b", "main")
    git(root, "config", "user.name", "Test User")
    git(root, "config", "user.email", "test@example.com")
    (root / "app.txt").write_text("one\n", encoding="utf-8")
    git(root, "add", "app.txt")
    git(root, "commit", "-m", "initial")
    return git(root, "rev-parse", "HEAD")


def commit_file(root: Path, relative: str, content: str) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    git(root, "add", "--", relative)
    git(root, "commit", "-m", "change")
    return git(root, "rev-parse", "HEAD")


def args(root: Path, output: Path, base: str, head: str = "HEAD", *extra: str):
    return module.parse_args(
        [
            "--root",
            str(root),
            "--output",
            str(output),
            "--base",
            base,
            "--head",
            head,
            *extra,
        ]
    )


class ReviewBundleTests(unittest.TestCase):
    def test_builds_private_bundle_with_manifest_and_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "repo"
            root.mkdir()
            base = init_repo(root)
            commit_file(root, "app.txt", "two\n")
            (root / "review-task.md").write_text("Review the user-visible change.\n", encoding="utf-8")
            git(root, "add", "review-task.md")
            git(root, "commit", "-m", "add task")
            output = parent / "bundle"

            manifest = module.build_bundle(
                args(root, output, base, "HEAD", "--task-file", "review-task.md")
            )

            self.assertTrue((output / "patch.diff").is_file())
            self.assertTrue((output / "task.md").is_file())
            disk_manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(disk_manifest["head_sha"], git(root, "rev-parse", "HEAD"))
            self.assertIn("app.txt", manifest["changed_paths"])
            self.assertNotIn(str(root), (output / "manifest.json").read_text(encoding="utf-8"))

    def test_rejects_sensitive_changed_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "repo"
            root.mkdir()
            base = init_repo(root)
            commit_file(root, ".env", "EXAMPLE=value\n")
            with self.assertRaisesRegex(module.BundleError, "looks sensitive"):
                module.build_bundle(args(root, parent / "bundle", base))

    def test_rejects_secret_like_patch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "repo"
            root.mkdir()
            base = init_repo(root)
            commit_file(root, "example.txt", "github_pat_abcdefghijklmnopqrstuvwxyz123456\n")
            with self.assertRaisesRegex(module.BundleError, "possible GitHub fine-grained token"):
                module.build_bundle(args(root, parent / "bundle", base))

    def test_rejects_context_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "repo"
            root.mkdir()
            base = init_repo(root)
            commit_file(root, "app.txt", "two\n")
            outside = parent / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            with self.assertRaisesRegex(module.BundleError, "repository-relative"):
                module.build_bundle(
                    args(root, parent / "bundle", base, "HEAD", "--task-file", "../outside.md")
                )

    def test_rejects_symlinked_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "repo"
            root.mkdir()
            base = init_repo(root)
            commit_file(root, "app.txt", "two\n")
            real = root / "real-task.md"
            real.write_text("task\n", encoding="utf-8")
            link = root / "task-link.md"
            try:
                link.symlink_to(real.name)
            except OSError:
                self.skipTest("symlinks are unavailable")
            git(root, "add", "real-task.md", "task-link.md")
            git(root, "commit", "-m", "add context")
            with self.assertRaisesRegex(module.BundleError, "must not traverse a symlink"):
                module.build_bundle(
                    args(root, parent / "bundle", base, "HEAD", "--task-file", "task-link.md")
                )

    def test_rejects_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "repo"
            root.mkdir()
            base = init_repo(root)
            commit_file(root, "app.txt", "two\n")
            output = parent / "bundle"
            output.mkdir()
            with self.assertRaisesRegex(module.BundleError, "already exists"):
                module.build_bundle(args(root, output, base))

    def test_rejects_dirty_worktree_to_avoid_omitted_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "repo"
            root.mkdir()
            base = init_repo(root)
            commit_file(root, "app.txt", "two\n")
            (root / "untracked.txt").write_text("not in the patch\n", encoding="utf-8")
            with self.assertRaisesRegex(module.BundleError, "working tree is dirty"):
                module.build_bundle(args(root, parent / "bundle", base))


if __name__ == "__main__":
    unittest.main()
