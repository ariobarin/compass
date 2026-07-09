"""Block non-ASCII dashes in public artifact writes."""

from __future__ import annotations

import re

from .common import deny_pre_tool, env_enabled

DASH_CHARS = chr(0x2013) + chr(0x2014)
SHELL_ARG = r'"[^"]+"|\'[^\']+\'|\S+'
PUBLIC_COMMAND_RE = re.compile(
    rf"\b(git(?:\s+(?:(?:-C|--git-dir|--work-tree|--namespace)\s+(?:{SHELL_ARG})|-c\s+(?:[^\s=]+=(?:{SHELL_ARG})|(?:{SHELL_ARG}))|--[A-Za-z0-9-]+=(?:{SHELL_ARG})|--[A-Za-z0-9-]+|-[A-Za-z]+))*\s+(?:commit|merge|tag)|gh(?:\s+(?:(?:--repo|-R)\s+(?:{SHELL_ARG})|--repo=(?:{SHELL_ARG})))*\s+(?:pr\s+(?:create|edit|comment|close|merge|ready|review|reopen)|release)\b)\b",
    re.IGNORECASE,
)


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
            deny_pre_tool(
                "Public artifact command contains an en dash or em dash. Use a plain hyphen instead."
            )
            return True
        return False

    if tool_name == "apply_patch":
        for path, line in added_patch_lines(command):
            if has_unicode_dash(line):
                target = path or "patch"
                deny_pre_tool(
                    f"Patch adds an en dash or em dash in {target}. Use a plain hyphen instead."
                )
                return True
    return False


HANDLERS = {"PreToolUse": dash_guard}
