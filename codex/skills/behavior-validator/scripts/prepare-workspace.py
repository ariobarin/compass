#!/usr/bin/env python3
"""Build a source-blind behavior validation workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Iterable, Sequence

BLOCKED_DIRECTORY_NAMES = {".git", ".hg", ".svn", "node_modules", "__pycache__"}
BLOCKED_FILE_NAMES = {
    ".env",
    ".env.local",
    "credentials",
    "credentials.json",
    "secrets",
    "secrets.json",
    "id_rsa",
    "id_ed25519",
}
BLOCKED_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}


class WorkspaceError(ValueError):
    """The workspace request would weaken the isolation boundary."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
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


def reject_sensitive_name(path: Path) -> None:
    for part in path.parts:
        lowered = part.lower()
        if lowered in BLOCKED_DIRECTORY_NAMES:
            raise WorkspaceError(f"fixture includes blocked directory: {part}")
    lowered_name = path.name.lower()
    if lowered_name in BLOCKED_FILE_NAMES or path.suffix.lower() in BLOCKED_SUFFIXES:
        raise WorkspaceError(f"fixture looks credential-bearing: {path.name}")


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


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
    if output_resolved.exists():
        raise WorkspaceError(f"output already exists: {output_resolved}")
    if is_relative_to(output_resolved, source_root):
        raise WorkspaceError("output must be outside the source root")
    if is_relative_to(source_root, output_resolved):
        raise WorkspaceError("output must not contain the source root")

    contract_path = normalize_source_item(contract, source_root, "contract")
    if not contract_path.is_file():
        raise WorkspaceError(f"contract is not a file: {contract_path}")
    if contract_path.is_symlink():
        raise WorkspaceError(f"contract must not be a symlink: {contract_path}")

    fixture_files: list[tuple[Path, Path]] = []
    seen_destinations: set[str] = set()
    for raw_fixture in fixtures:
        fixture_root = normalize_source_item(raw_fixture, source_root, "fixture")
        reject_sensitive_name(fixture_root.relative_to(source_root))
        for fixture_file in iter_fixture_files(fixture_root):
            relative = fixture_file.relative_to(source_root)
            reject_sensitive_name(relative)
            destination = Path("fixtures") / relative
            destination_key = destination.as_posix().lower()
            if destination_key in seen_destinations:
                continue
            seen_destinations.add(destination_key)
            fixture_files.append((fixture_file, destination))

    try:
        output_resolved.mkdir(parents=True)
        contract_destination = output_resolved / "contract.md"
        shutil.copyfile(contract_path, contract_destination)

        copied: list[dict[str, object]] = []
        for source_file, destination_relative in fixture_files:
            destination = output_resolved / destination_relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, destination)
            copied.append(
                {
                    "path": destination_relative.as_posix(),
                    "sha256": sha256(destination),
                    "size_bytes": destination.stat().st_size,
                }
            )

        isolation = (
            "# Validator Workspace\n\n"
            "This directory contains only an observable behavior contract and explicitly "
            "approved fixtures. Do not leave this directory to inspect implementation "
            "material. Treat any source, diff, test, history, or review bundle exposure "
            "as contamination.\n"
        )
        write_text(output_resolved / "AGENTS.md", isolation)

        manifest: dict[str, object] = {
            "schema_version": 1,
            "contract": {
                "path": "contract.md",
                "sha256": sha256(contract_destination),
                "size_bytes": contract_destination.stat().st_size,
            },
            "fixtures": copied,
            "forbidden_material": [
                "source",
                "diffs",
                "tests",
                "git history",
                "implementation notes",
                "review bundles",
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
