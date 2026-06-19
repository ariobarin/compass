#!/usr/bin/env python3
"""Portable Codex hook guard for local workflow checks."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


DASH_CHARS = chr(0x2013) + chr(0x2014)
PUBLIC_COMMAND_RE = re.compile(
    r"\b(git\s+commit|git\s+tag|gh\s+pr\s+\S+|gh\s+release)\b",
    re.IGNORECASE,
)
def read_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}


def write_json(value: dict) -> None:
    print(json.dumps(value, separators=(",", ":")))


def deny_pre_tool(reason: str) -> None:
    write_json(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )


def continue_turn(reason: str) -> None:
    write_json({"decision": "block", "reason": reason})


def tool_command(data: dict) -> str:
    tool_input = data.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command
    return ""


def has_unicode_dash(text: str) -> bool:
    return any(char in text for char in DASH_CHARS)


def added_patch_lines(command: str) -> list[tuple[str, str]]:
    current_path = ""
    lines: list[tuple[str, str]] = []
    for line in command.splitlines():
        for prefix in (
            "*** Add File: ",
            "*** Update File: ",
            "*** Delete File: ",
            "*** Move to: ",
        ):
            if line.startswith(prefix):
                current_path = line[len(prefix) :].strip()
                break
        else:
            if line.startswith("+") and not line.startswith("+++"):
                lines.append((current_path, line[1:]))
    return lines


def dash_guard(data: dict) -> bool:
    tool_name = str(data.get("tool_name") or "")
    command = tool_command(data)

    if tool_name == "Bash":
        if PUBLIC_COMMAND_RE.search(command) and has_unicode_dash(command):
            deny_pre_tool("Public artifact command contains an en dash or em dash. Use a plain hyphen instead.")
            return True
        return False

    if tool_name == "apply_patch":
        for path, line in added_patch_lines(command):
            if has_unicode_dash(line):
                target = path or "patch"
                deny_pre_tool(f"Patch adds an en dash or em dash in {target}. Use a plain hyphen instead.")
                return True
    return False


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


def candidate_repos(cwd: Path) -> list[Path]:
    repos: list[Path] = []
    root = git_root(cwd)
    if root is not None:
        repos.append(root)
    else:
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
    no_upstream = "..." not in header and not header.endswith("main") and not header.endswith("master")

    if not body and not has_ahead and not no_upstream:
        return None

    details = []
    if body:
        details.append(f"{len(body)} dirty entries")
    if has_ahead:
        details.append("unpushed commits")
    if no_upstream:
        details.append("no upstream shown")
    if not details:
        return None
    return f"{repo}: {', '.join(details)}"


def dirty_worktree_closeout(data: dict) -> bool:
    if data.get("stop_hook_active"):
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
        "Before final answer, explicitly mention these dirty or unpushed git states:\n"
        f"{lines}"
    )
    return True


def main() -> int:
    data = read_input()
    event = str(data.get("hook_event_name") or "")

    if event == "PreToolUse":
        dash_guard(data)
        return 0

    if event == "Stop":
        dirty_worktree_closeout(data)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
