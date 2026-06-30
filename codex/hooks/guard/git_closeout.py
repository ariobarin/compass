"""Ask Codex to mention unresolved git state before stopping."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .common import continue_turn, env_enabled


def run_git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
        check=False,
    )


def git_root(path: Path) -> Path | None:
    result = run_git(path, ["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        return None
    root = result.stdout.strip()
    if not root:
        return None
    return Path(root)


def head_missing_from_remotes(repo: Path) -> bool:
    remotes = run_git(
        repo,
        ["for-each-ref", "--format=%(refname:short)", "refs/remotes"],
    )
    if remotes.returncode != 0:
        return False
    if not any(line.strip() for line in remotes.stdout.splitlines()):
        return False

    contains = run_git(
        repo,
        ["branch", "-r", "--contains", "HEAD", "--format=%(refname:short)"],
    )
    if contains.returncode != 0:
        return False
    return not any(line.strip() for line in contains.stdout.splitlines())


def candidate_repos(cwd: Path) -> list[Path]:
    repos: list[Path] = []
    root = git_root(cwd)
    if root is not None:
        repos.append(root)

    if not env_enabled("CODEX_PORTABLE_DISABLE_CHILD_REPO_SCAN"):
        try:
            for child in cwd.iterdir():
                if not child.is_dir():
                    continue
                if (child / ".git").exists():
                    repos.append(child)
        except OSError:
            pass

    unique: list[Path] = []
    seen: set[str] = set()
    for repo in repos:
        key = str(repo.resolve()).lower()
        if key not in seen:
            seen.add(key)
            unique.append(repo)
    return unique[:30]


def repo_status_summary(repo: Path) -> str | None:
    branch = run_git(repo, ["status", "--short", "--branch"])
    if branch.returncode != 0:
        return None

    lines = [line for line in branch.stdout.splitlines() if line.strip()]
    if not lines:
        return None

    body = [line for line in lines[1:] if line.strip()]
    header = lines[0]
    has_ahead = "[ahead " in header or "ahead " in header
    has_no_upstream = "..." not in header
    upstream_gone = "[gone]" in header
    has_unpushed_without_remote = (
        has_no_upstream or upstream_gone
    ) and head_missing_from_remotes(repo)

    if not body and not has_ahead and not has_unpushed_without_remote:
        return None

    details = []
    if body:
        details.append(f"{len(body)} dirty entries")
    if has_ahead or has_unpushed_without_remote:
        details.append("unpushed commits")
    if not details:
        return None
    return f"{repo}: {', '.join(details)}"


def dirty_worktree_closeout(data: dict) -> bool:
    if data.get("stop_hook_active") or env_enabled("CODEX_PORTABLE_DISABLE_GIT_CLOSEOUT"):
        return False

    cwd = Path(str(data.get("cwd") or os.getcwd()))
    summaries = []
    for repo in candidate_repos(cwd):
        summary = repo_status_summary(repo)
        if summary:
            summaries.append(summary)

    if not summaries:
        return False

    shown = summaries[:8]
    more = len(summaries) - len(shown)
    lines = "\n".join(f"- {summary}" for summary in shown)
    if more > 0:
        lines += f"\n- {more} more repos omitted"

    continue_turn(
        "Include this unresolved git state in the final answer. Keep it concise "
        "and do not attempt cleanup unless the user asked:\n"
        f"{lines}"
    )
    return True


HANDLERS = {"Stop": dirty_worktree_closeout}
