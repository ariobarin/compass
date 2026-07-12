#!/usr/bin/env python3
"""Build a confined, fail-closed source-aware review bundle from a Git diff."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

DEFAULT_MAX_BYTES = 2 * 1024 * 1024
SENSITIVE_BASENAMES = {
    ".env",
    "auth.json",
    "credentials.json",
    "secrets.json",
    "id_rsa",
    "id_ed25519",
    "known_hosts",
    "cookies.sqlite",
    "history.jsonl",
    "session_index.jsonl",
}
SENSITIVE_SUFFIXES = {
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".sqlite",
    ".sqlite-shm",
    ".sqlite-wal",
}
SENSITIVE_SEGMENTS = {
    ".secrets",
    "credentials",
    "private-keys",
    "secrets",
}
SECRET_PATTERNS = [
    ("private key", re.compile(rb"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(rb"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained token", re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI-style key", re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(rb"\bAKIA[0-9A-Z]{16}\b")),
]


class BundleError(ValueError):
    """A review bundle could not be built without weakening its boundary."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run_git(root: Path, arguments: Sequence[str], *, binary: bool = False) -> bytes | str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=not binary,
            timeout=60,
        )
    except FileNotFoundError as error:
        raise BundleError("git is not on PATH") from error
    except subprocess.TimeoutExpired as error:
        raise BundleError(f"git command timed out: {' '.join(arguments)}") from error
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.decode("utf-8", errors="replace") if binary else error.stderr
        detail = (stderr or "git command failed").strip()
        raise BundleError(detail) from error
    return result.stdout


def resolve_commit(root: Path, value: str, label: str) -> str:
    if not value or value.startswith("-") or "\x00" in value:
        raise BundleError(f"{label} must be a non-option Git ref")
    resolved = run_git(root, ["rev-parse", "--verify", "--end-of-options", f"{value}^{{commit}}"])
    assert isinstance(resolved, str)
    sha = resolved.strip()
    if not re.fullmatch(r"[0-9a-f]{40,64}", sha):
        raise BundleError(f"{label} did not resolve to a commit: {value}")
    return sha


def normalize_repo_path(value: str) -> str:
    normalized = value.replace("\\", "/").strip("/")
    if not normalized or normalized.startswith("../") or "/../" in f"/{normalized}/":
        raise BundleError(f"unsafe repository path: {value}")
    return normalized


def sensitive_path_reason(value: str) -> str | None:
    normalized = normalize_repo_path(value)
    parts = [part.lower() for part in normalized.split("/")]
    basename = parts[-1]
    if basename in SENSITIVE_BASENAMES or basename.startswith(".env."):
        return f"sensitive basename: {basename}"
    if any(basename.endswith(suffix) for suffix in SENSITIVE_SUFFIXES):
        return f"sensitive file type: {basename}"
    for part in parts[:-1]:
        if part in SENSITIVE_SEGMENTS:
            return f"sensitive path segment: {part}"
    return None


def secret_reason(value: bytes) -> str | None:
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(value):
            return label
    return None


def safe_repo_file(root: Path, raw: str, label: str) -> tuple[str, Path]:
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise BundleError(f"{label} must be a repository-relative path: {raw}")
    normalized = normalize_repo_path(relative.as_posix())
    candidate = root / relative
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise BundleError(f"{label} must not traverse a symlink: {raw}")
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as error:
        raise BundleError(f"{label} must be an existing regular file: {raw}") from error
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise BundleError(f"{label} escapes the repository root: {raw}") from error
    if not resolved.is_file():
        raise BundleError(f"{label} must be a regular non-symlink file: {raw}")
    reason = sensitive_path_reason(normalized)
    if reason:
        raise BundleError(f"{label} looks sensitive ({reason}): {normalized}")
    return normalized, resolved


def set_private_mode(path: Path, directory: bool) -> None:
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR | (stat.S_IXUSR if directory else 0))
    except OSError:
        pass


def write_private(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    set_private_mode(path.parent, True)
    path.write_bytes(value)
    set_private_mode(path, False)


def ensure_output_boundary(root: Path, output: Path) -> None:
    output = output.resolve()
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise BundleError("output must be outside the repository checkout")
    if output.exists() or output.is_symlink():
        raise BundleError(f"output already exists: {output}")


def build_bundle(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    if not (root / ".git").exists():
        inside = run_git(root, ["rev-parse", "--is-inside-work-tree"])
        assert isinstance(inside, str)
        if inside.strip() != "true":
            raise BundleError(f"not a Git worktree: {root}")

    output = args.output.expanduser().resolve()
    ensure_output_boundary(root, output)

    dirty = run_git(root, ["status", "--porcelain=v1", "--untracked-files=all"])
    assert isinstance(dirty, str)
    if dirty.strip():
        raise BundleError("working tree is dirty; review bundles cover a committed branch or PR head only")

    base_sha = resolve_commit(root, args.base, "base")
    head_sha = resolve_commit(root, args.head, "head")
    range_value = f"{base_sha}...{head_sha}"

    changed_raw = run_git(
        root,
        ["diff", "--name-only", "-z", "--find-renames", range_value, "--"],
        binary=True,
    )
    assert isinstance(changed_raw, bytes)
    changed_paths = [
        normalize_repo_path(item.decode("utf-8", errors="strict"))
        for item in changed_raw.split(b"\0")
        if item
    ]
    if not changed_paths:
        raise BundleError("the selected commit range has no changed files")
    for changed_path in changed_paths:
        reason = sensitive_path_reason(changed_path)
        if reason:
            raise BundleError(f"changed path looks sensitive ({reason}): {changed_path}")

    patch = run_git(
        root,
        [
            "diff",
            "--binary",
            "--full-index",
            "--no-ext-diff",
            "--find-renames",
            range_value,
            "--",
        ],
        binary=True,
    )
    assert isinstance(patch, bytes)
    if not patch:
        raise BundleError("Git produced an empty patch for a non-empty changed-file list")
    if len(patch) > args.max_bytes:
        raise BundleError(
            f"patch is {len(patch)} bytes, above the {args.max_bytes}-byte bundle limit; split the change"
        )
    patch_secret = secret_reason(patch)
    if patch_secret:
        raise BundleError(f"patch contains a possible {patch_secret}; redact or split the change")

    context_inputs: list[tuple[str, Path, str]] = []
    if args.task_file:
        relative, source = safe_repo_file(root, args.task_file, "task file")
        context_inputs.append((relative, source, "task.md"))
    seen_destinations: set[str] = set()
    for raw in args.dataset:
        relative, source = safe_repo_file(root, raw, "dataset")
        destination = f"context/{relative}"
        if destination in seen_destinations:
            raise BundleError(f"duplicate dataset: {relative}")
        seen_destinations.add(destination)
        context_inputs.append((relative, source, destination))

    context_manifest: list[dict[str, Any]] = []
    context_values: list[tuple[str, bytes]] = []
    total_bytes = len(patch)
    for relative, source, destination in context_inputs:
        value = source.read_bytes()
        total_bytes += len(value)
        if total_bytes > args.max_bytes:
            raise BundleError(
                f"bundle inputs are {total_bytes} bytes, above the {args.max_bytes}-byte limit; split the review"
            )
        found_secret = secret_reason(value)
        if found_secret:
            raise BundleError(f"{relative} contains a possible {found_secret}; redact it before bundling")
        context_values.append((destination, value))
        context_manifest.append(
            {
                "source": relative,
                "bundle_path": destination,
                "bytes": len(value),
                "sha256": sha256_bytes(value),
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent))
    set_private_mode(temp, True)
    try:
        write_private(temp / "patch.diff", patch)
        for destination, value in context_values:
            write_private(temp / destination, value)
        manifest = {
            "schema_version": 1,
            "base": args.base,
            "base_sha": base_sha,
            "head": args.head,
            "head_sha": head_sha,
            "changed_paths": changed_paths,
            "patch": {
                "bundle_path": "patch.diff",
                "bytes": len(patch),
                "sha256": sha256_bytes(patch),
            },
            "context": context_manifest,
            "limits": {
                "max_bytes": args.max_bytes,
                "total_bytes": total_bytes,
            },
        }
        manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
        write_private(temp / "manifest.json", manifest_bytes)
        os.replace(temp, output)
        set_private_mode(output, True)
    except BaseException:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    return manifest


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--task-file")
    parser.add_argument("--dataset", action="append", default=[])
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.max_bytes <= 0:
        parser.error("--max-bytes must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = build_bundle(args)
    except (BundleError, OSError, UnicodeDecodeError) as error:
        print(f"review bundle failed: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"review bundle: {args.output.expanduser().resolve()}")
        print(f"head: {manifest['head_sha']}")
        print(f"changed files: {len(manifest['changed_paths'])}")
        print(f"bundle bytes: {manifest['limits']['total_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
