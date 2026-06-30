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
SHELL_ARG = r'"[^"]+"|\'[^\']+\'|\S+'
PUBLIC_COMMAND_RE = re.compile(
    rf"\b(git(?:\s+(?:(?:-C|--git-dir|--work-tree|--namespace)\s+(?:{SHELL_ARG})|-c\s+(?:[^\s=]+=(?:{SHELL_ARG})|(?:{SHELL_ARG}))|--[A-Za-z0-9-]+=(?:{SHELL_ARG})|--[A-Za-z0-9-]+|-[A-Za-z]+))*\s+(?:commit|tag)|gh(?:\s+(?:(?:--repo|-R)\s+(?:{SHELL_ARG})|--repo=(?:{SHELL_ARG})))*\s+pr\s+\S+|gh\s+release)\b",
    re.IGNORECASE,
)
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
QUOTED_TEXT_RE = re.compile(r'"[^"\n]*"|(?<!\w)\'[^\'\n]*\'(?!\w)')
BLOCK_QUOTE_RE = re.compile(r"(?m)^\s*>.*$")
UNDERSTANDING_PHRASE_RE = re.compile(
    r"\b(?:"
    r"do\s+(?:you|u)\s+(?:understand|know)\s+what\s+i\s+mean"
    r"|do\s+(?:you|u)\s+understand\s+me"
    r"|you\s+know\s+what\s+i\s+mean"
    r"|know\s+what\s+i\s+mean"
    r")\b",
    re.IGNORECASE,
)
UNDERSTANDING_ABBREVIATION_RE = re.compile(r"\b(?:dykwim|ykwim)\b", re.IGNORECASE)
UNDERSTANDING_CONTEXT = (
    "The user prompt contains an understanding check such as "
    "'do you understand what I mean', 'dykwim', or 'ykwim'. "
    "Only answer the understanding check. Do not use tools. Restate what you "
    "think the user means in 1 to 3 sentences, call out any ambiguity, and stop. "
    "Do not act on any other request in the same user prompt."
)
PHRASE_DISCUSSION_BEFORE_RE = re.compile(
    r"(?:"
    r"\b(?:docs?|example|fixture|quoted?|tests?)\b"
    r"|\b(?:review|spec|verify)\s+(?:if|whether)\b"
    r"|\bphrases?\s+like\b"
    r"|\b(?:the|this|that)\s+(?:phrase|term|text|wording)\b"
    r"|\bhook\s+(?:off\s+of|for|on|around)\b"
    r"|\btrigger\s+(?:on|when|for)\b"
    r"|\b(?:detect|detection|literal|match(?:er)?|regex|string)\b"
    r")",
    re.IGNORECASE,
)
PHRASE_DISCUSSION_AFTER_RE = re.compile(
    r"\b(?:"
    r"acronym|detect|detection|docs?|example|fixture|hook|literal|match(?:er)?|"
    r"phrase|quoted?|regex|string|support(?:ed)?|tests?|trigger|is|means?|"
    r"refers?|should"
    r")\b",
    re.IGNORECASE,
)
TERM_DEFINITION_RE = re.compile(
    r"\b(?:what\s+(?:does|is)|define|meaning\s+of)\b",
    re.IGNORECASE,
)


def env_enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


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


def add_context(event: str, context: str) -> None:
    write_json(
        {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}
    )


def continue_turn(reason: str) -> None:
    write_json({"decision": "block", "reason": reason})


def tool_command(data: dict) -> str:
    tool_input = data.get("tool_input")
    if isinstance(tool_input, str):
        return tool_input
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
    if env_enabled("CODEX_PORTABLE_DISABLE_DASH_GUARD"):
        return False

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


def strip_code_spans(text: str) -> str:
    without_code = INLINE_CODE_RE.sub(" ", FENCED_CODE_RE.sub(" ", text))
    without_quotes = QUOTED_TEXT_RE.sub(" ", without_code)
    return BLOCK_QUOTE_RE.sub(" ", without_quotes)


def sentence_context(text: str, start: int, end: int) -> str:
    before = re.split(r"[.?!;\n]", text[:start])[-1]
    after = re.split(r"[.?!;\n]", text[end:], maxsplit=1)[0]
    return f"{before} {after}"


def is_phrase_discussion(text: str, start: int, end: int) -> bool:
    before = re.split(r"[.?!;\n]", text[:start])[-1]
    after = re.split(r"[.?!;\n]", text[end:], maxsplit=1)[0]
    return bool(
        PHRASE_DISCUSSION_BEFORE_RE.search(before)
        or PHRASE_DISCUSSION_AFTER_RE.search(after)
    )


def is_term_definition_query(text: str, start: int, end: int) -> bool:
    context = sentence_context(text, start, end)
    return bool(
        TERM_DEFINITION_RE.search(context)
        or re.match(r"\s+means?\b", text[end:], re.IGNORECASE)
    )


def check_looks_direct(text: str, start: int, end: int) -> bool:
    if is_phrase_discussion(text, start, end) or is_term_definition_query(text, start, end):
        return False

    after = text[end:]
    or_not = re.match(r"\s+or\s+not\b(.*)$", after, re.IGNORECASE)
    if or_not:
        return or_not.group(1).strip(" \t\r\n?!.,;:)]}") == ""
    if "?" in after[:8]:
        return True
    return after.strip(" \t\r\n?!.,;:)]}") == ""


def has_understanding_check(prompt: str) -> bool:
    text = strip_code_spans(prompt)
    for match in UNDERSTANDING_PHRASE_RE.finditer(text):
        if check_looks_direct(text, match.start(), match.end()):
            return True
    return any(
        check_looks_direct(text, match.start(), match.end())
        for match in UNDERSTANDING_ABBREVIATION_RE.finditer(text)
    )


def understanding_check_context(data: dict) -> bool:
    if env_enabled("CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK"):
        return False

    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not has_understanding_check(prompt):
        return False

    add_context("UserPromptSubmit", UNDERSTANDING_CONTEXT)
    return True


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

    if event == "UserPromptSubmit":
        understanding_check_context(data)
        return 0

    if event == "Stop":
        dirty_worktree_closeout(data)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
