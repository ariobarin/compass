#!/usr/bin/env python3
"""Build a fail-closed source-blind behavior validation workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable, Sequence

BLOCKED_DIRECTORY_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".ssh",
    ".aws",
    ".azure",
    ".gnupg",
    "node_modules",
    "__pycache__",
    "credentials",
    "private-keys",
    "secrets",
}
BLOCKED_FILE_NAMES = {
    "auth.json",
    "cookies.sqlite",
    "credentials",
    "credentials.json",
    "history.jsonl",
    "id_ed25519",
    "id_rsa",
    "known_hosts",
    "secrets",
    "secrets.json",
    "session_index.jsonl",
}
BLOCKED_SUFFIXES = {
    ".key",
    ".p12",
    ".pem",
    ".pfx",
    ".sqlite",
    ".sqlite-shm",
    ".sqlite-wal",
}
SECRET_PATTERNS = (
    ("private key", re.compile(rb"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(rb"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained token", re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI-style key", re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(rb"\bAKIA[0-9A-Z]{16}\b")),
)
SCAN_CHUNK_BYTES = 1024 * 1024
SCAN_OVERLAP_BYTES = 4096


class WorkspaceError(ValueError):
    """The workspace request would weaken the isolation boundary."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(SCAN_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def reject_symlink_path(path: Path, stop: Path, label: str) -> None:
    cursor = path
    while True:
        if cursor.exists() and cursor.is_symlink():
            raise WorkspaceError(f"{label} must not traverse a symlink: {cursor}")
        if cursor == stop:
            break
        if stop not in cursor.parents:
            raise WorkspaceError(f"{label} escapes source root: {path}")
        cursor = cursor.parent


def sensitive_path_reason(path: Path) -> str | None:
    parts = [part.lower() for part in path.parts]
    for part in parts[:-1]:
        if part in BLOCKED_DIRECTORY_NAMES:
            return f"blocked directory: {part}"
    name = parts[-1] if parts else ""
    if name == ".env" or name.startswith(".env."):
        return f"environment file: {name}"
    if name in BLOCKED_FILE_NAMES:
        return f"sensitive filename: {name}"
    if any(name.endswith(suffix) for suffix in BLOCKED_SUFFIXES):
        return f"sensitive file type: {name}"
    return None


def reject_sensitive_path(path: Path, label: str) -> None:
    reason = sensitive_path_reason(path)
    if reason:
        raise WorkspaceError(f"{label} looks credential-bearing ({reason}): {path.as_posix()}")


def secret_reason(path: Path) -> str | None:
    overlap = b""
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(SCAN_CHUNK_BYTES)
            if not chunk:
                return None
            sample = overlap + chunk
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(sample):
                    return label
            overlap = sample[-SCAN_OVERLAP_BYTES:]


def reject_secret_content(path: Path, label: str) -> None:
    reason = secret_reason(path)
    if reason:
        raise WorkspaceError(f"{label} contains a possible {reason}: {path.name}")


def iter_fixture_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
        return
    if not path.is_dir():
        raise WorkspaceError(f"fixture does not exist: {path}")
    for candidate in sorted(path.rglob("*")):
        if candidate.is_symlink():
            raise WorkspaceError(f"fixture tree contains a symlink: {candidate}")
        if candidate.is_file():
            yield candidate


def normalize_source_item(raw: Path, source_root: Path, label: str) -> Path:
    unresolved = raw.expanduser()
    if not unresolved.is_absolute():
        unresolved = source_root / unresolved
    reject_symlink_path(unresolved, source_root, label)
    resolved = unresolved.resolve()
    if not is_relative_to(resolved, source_root):
        raise WorkspaceError(f"{label} must stay under source root: {raw}")
    return resolved


def fixture_destination(relative: Path) -> Path:
    parts = relative.parts
    if parts and parts[0].lower() == "fixtures":
        parts = parts[1:]
    if not parts:
        raise WorkspaceError(f"fixture does not identify a file: {relative}")
    return Path("fixtures", *parts)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def file_record(path: Path, relative: str) -> dict[str, object]:
    return {
        "path": relative,
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def build_workspace(
    source_root: Path,
    contract: Path,
    output: Path,
    fixtures: Sequence[Path],
) -> dict[str, object]:
    source_root = source_root.expanduser().resolve()
    if not source_root.is_dir():
        raise WorkspaceError(f"source root is not a directory: {source_root}")

    output_unresolved = output.expanduser()
    if not output_unresolved.is_absolute():
        output_unresolved = Path.cwd() / output_unresolved
    output_parent = output_unresolved.parent.resolve()
    output_resolved = output_parent / output_unresolved.name
    if output_resolved.exists() or output_resolved.is_symlink():
        raise WorkspaceError(f"output already exists: {output_resolved}")
    if is_relative_to(output_resolved, source_root):
        raise WorkspaceError("output must be outside the source root")
    if is_relative_to(source_root, output_resolved):
        raise WorkspaceError("output must not contain the source root")

    contract_path = normalize_source_item(contract, source_root, "contract")
    if not contract_path.is_file() or contract_path.is_symlink():
        raise WorkspaceError(f"contract must be a regular non-symlink file: {contract_path}")
    reject_sensitive_path(contract_path.relative_to(source_root), "contract")
    reject_secret_content(contract_path, "contract")

    fixture_files: list[tuple[Path, Path]] = []
    seen_destinations: dict[str, Path] = {}
    for raw_fixture in fixtures:
        fixture_root = normalize_source_item(raw_fixture, source_root, "fixture")
        reject_sensitive_path(fixture_root.relative_to(source_root), "fixture")
        for fixture_file in iter_fixture_files(fixture_root):
            relative = fixture_file.relative_to(source_root)
            reject_sensitive_path(relative, "fixture")
            reject_secret_content(fixture_file, "fixture")
            destination = fixture_destination(relative)
            destination_key = destination.as_posix().casefold()
            previous_source = seen_destinations.get(destination_key)
            if previous_source is not None:
                if previous_source == fixture_file:
                    continue
                raise WorkspaceError(
                    "fixture destinations collide case-insensitively: "
                    f"{previous_source.relative_to(source_root).as_posix()} and "
                    f"{relative.as_posix()} -> {destination.as_posix()}"
                )
            seen_destinations[destination_key] = fixture_file
            fixture_files.append((fixture_file, destination))

    isolation = (
        "# Source-Blind Validator Workspace\n\n"
        "Validate the observable contract against the named target. Stay inside this "
        "workspace for local reads and use only the approved fixture paths listed in "
        "`workspace-manifest.json`. Treat source, diffs, tests, history, implementation "
        "notes, review bundles, or any unlisted local material as contamination. Record "
        "contamination and stop so the principal can create a fresh workspace.\n"
    )

    try:
        output_resolved.mkdir(parents=True)
        contract_destination = output_resolved / "contract.md"
        shutil.copyfile(contract_path, contract_destination)

        write_text(output_resolved / "AGENTS.md", isolation)
        write_text(output_resolved / "CLAUDE.md", isolation)

        copied: list[dict[str, object]] = []
        for source_file, destination_relative in fixture_files:
            destination = output_resolved / destination_relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, destination)
            copied.append(file_record(destination, destination_relative.as_posix()))

        instructions = [
            file_record(output_resolved / "AGENTS.md", "AGENTS.md"),
            file_record(output_resolved / "CLAUDE.md", "CLAUDE.md"),
        ]
        allowed_paths = [
            "AGENTS.md",
            "CLAUDE.md",
            "contract.md",
            "workspace-manifest.json",
            *[record["path"] for record in copied],
        ]
        manifest: dict[str, object] = {
            "schema_version": 2,
            "contract": file_record(contract_destination, "contract.md"),
            "instructions": instructions,
            "fixtures": copied,
            "allowed_local_paths": allowed_paths,
            "forbidden_material": [
                "source",
                "diffs",
                "tests",
                "git history",
                "implementation notes",
                "review bundles",
                "credentials",
                "unlisted local files",
            ],
        }
        write_text(
            output_resolved / "workspace-manifest.json",
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        )
        return manifest
    except Exception:
        shutil.rmtree(output_resolved, ignore_errors=True)
        raise


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture", action="append", type=Path, default=[])
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = build_workspace(
            args.source_root,
            args.contract,
            args.output,
            args.fixture,
        )
    except (WorkspaceError, OSError) as error:
        print(f"behavior workspace failed: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"behavior workspace ready: {args.output.expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
