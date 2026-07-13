#!/usr/bin/env python3
"""Plan and verify safe overlays from a reviewed Codex TOML fragment."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

BARE_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TABLE_RE = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")


@dataclass(frozen=True)
class ReviewedEntry:
    table: tuple[str, ...]
    key: str
    value: str | int | bool
    raw_value: str
    order: int

    @property
    def path_parts(self) -> tuple[str, ...]:
        return (*self.table, self.key)

    @property
    def path(self) -> str:
        return ".".join(self.path_parts)


@dataclass(frozen=True)
class AssignmentLocation:
    line_index: int
    value_start: int
    value_end: int


class ReviewedConfigError(ValueError):
    pass


def read_text(path: Path, *, missing_ok: bool = False) -> str:
    try:
        return path.read_bytes().decode("utf-8-sig")
    except FileNotFoundError:
        if missing_ok:
            return ""
        raise ReviewedConfigError(f"missing reviewed config fragment: {path}")
    except UnicodeDecodeError as error:
        raise ReviewedConfigError(f"config is not valid UTF-8: {path}") from error


def scan_code(line: str) -> tuple[str, int | None]:
    """Return text before an unquoted comment and that comment's index."""
    quote: str | None = None
    escaped = False
    for index, char in enumerate(line):
        if quote == '"':
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = None
            continue
        if quote == "'":
            if char == "'":
                quote = None
            continue
        if char in ('"', "'"):
            quote = char
            continue
        if char == "#":
            return line[:index], index
    if quote is not None:
        raise ReviewedConfigError("multiline or unterminated strings are not supported")
    return line, None


def find_multiline_end(line: str, delimiter: str, start: int) -> int | None:
    search_from = start
    while True:
        end = line.find(delimiter, search_from)
        if end < 0:
            return None
        if delimiter == '"""':
            backslashes = 0
            cursor = end - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 1:
                search_from = end + len(delimiter)
                continue
        return end


def scan_live_code(
    line: str, multiline_quote: str | None
) -> tuple[str, str | None, bool]:
    """Return statement code while skipping unrelated multiline strings."""
    if multiline_quote is not None:
        end = find_multiline_end(line, multiline_quote, 0)
        return "", (multiline_quote if end is None else None), True

    quote: str | None = None
    escaped = False
    index = 0
    while index < len(line):
        if quote == '"':
            char = line[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = None
            index += 1
            continue
        if quote == "'":
            if line[index] == "'":
                quote = None
            index += 1
            continue
        delimiter = None
        if line.startswith('"""', index):
            delimiter = '"""'
        elif line.startswith("'''", index):
            delimiter = "'''"
        if delimiter is not None:
            end = find_multiline_end(line, delimiter, index + len(delimiter))
            return line[:index], (delimiter if end is None else None), True
        char = line[index]
        if char in ('"', "'"):
            quote = char
            index += 1
            continue
        if char == "#":
            return line[:index], None, False
        index += 1
    return line, None, False

def find_unquoted_equals(code: str) -> int | None:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(code):
        if quote == '"':
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = None
            continue
        if quote == "'":
            if char == "'":
                quote = None
            continue
        if char in ('"', "'"):
            quote = char
            continue
        if char == "=":
            return index
    return None


def parse_scalar(raw: str, *, context: str) -> str | int | bool:
    if not raw:
        raise ReviewedConfigError(f"missing scalar value for {context}")
    try:
        parsed = tomllib.loads(f"value = {raw}\n")["value"]
    except tomllib.TOMLDecodeError as error:
        raise ReviewedConfigError(f"invalid scalar for {context}: {error}") from error
    if type(parsed) not in (str, int, bool):
        raise ReviewedConfigError(
            f"unsupported reviewed value for {context}: only strings, integers, and booleans are allowed"
        )
    return parsed


def parse_reviewed(text: str) -> list[ReviewedEntry]:
    entries: list[ReviewedEntry] = []
    table: tuple[str, ...] = ()
    seen: set[tuple[str, ...]] = set()

    for line_number, line in enumerate(text.splitlines(), 1):
        code, _ = scan_code(line)
        stripped = code.strip()
        if not stripped:
            continue
        if stripped.startswith("[[") or stripped.endswith("]]"):
            raise ReviewedConfigError(
                f"unsupported reviewed TOML at line {line_number}: arrays of tables are not allowed"
            )
        if stripped.startswith("["):
            if not stripped.endswith("]") or stripped.count("[") != 1 or stripped.count("]") != 1:
                raise ReviewedConfigError(
                    f"unsupported reviewed TOML table at line {line_number}"
                )
            table_name = stripped[1:-1].strip()
            if not TABLE_RE.fullmatch(table_name):
                raise ReviewedConfigError(
                    f"unsupported reviewed table name at line {line_number}: {table_name!r}"
                )
            table = tuple(table_name.split("."))
            continue

        equals = find_unquoted_equals(code)
        if equals is None:
            raise ReviewedConfigError(
                f"unsupported reviewed TOML at line {line_number}: expected scalar assignment"
            )
        key = code[:equals].strip()
        raw_value = code[equals + 1 :].strip()
        if not BARE_KEY_RE.fullmatch(key):
            raise ReviewedConfigError(
                f"unsupported reviewed key at line {line_number}: {key!r}"
            )
        value = parse_scalar(raw_value, context=f"line {line_number}")
        path = (*table, key)
        if path in seen:
            raise ReviewedConfigError(f"duplicate reviewed config key: {'.'.join(path)}")
        seen.add(path)
        entries.append(
            ReviewedEntry(
                table=table,
                key=key,
                value=value,
                raw_value=raw_value,
                order=len(entries),
            )
        )

    if not entries:
        raise ReviewedConfigError("reviewed config fragment contains no managed settings")

    try:
        parsed = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ReviewedConfigError(f"invalid reviewed TOML: {error}") from error
    for entry in entries:
        actual = lookup(parsed, entry.path_parts)
        if actual is MISSING or type(actual) is not type(entry.value) or actual != entry.value:
            raise ReviewedConfigError(
                f"reviewed parser disagreement for {entry.path}; unsupported TOML structure"
            )
    return entries


MISSING = object()


def lookup(data: dict[str, Any], path: Iterable[str]) -> Any:
    current: Any = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return MISSING
        current = current[part]
    return current


def parse_live(text: str, entries: list[ReviewedEntry]) -> dict[str, Any]:
    if not text.strip():
        return {}
    try:
        parsed = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ReviewedConfigError(f"invalid live config.toml: {error}") from error
    if not isinstance(parsed, dict):
        raise ReviewedConfigError("live config.toml root must be a table")
    return parsed


def table_header(stripped: str) -> tuple[str, ...] | None:
    if not stripped.startswith("["):
        return None
    if stripped.startswith("[[") or not stripped.endswith("]"):
        return None
    name = stripped[1:-1].strip()
    if not TABLE_RE.fullmatch(name):
        return None
    return tuple(name.split("."))


def locate_assignments(
    text: str, entries: list[ReviewedEntry], parsed_live: dict[str, Any]
) -> tuple[list[str], dict[tuple[str, ...], AssignmentLocation], dict[tuple[str, ...], int]]:
    lines = text.splitlines(keepends=True)
    managed = {entry.path_parts for entry in entries}
    locations: dict[tuple[str, ...], AssignmentLocation] = {}
    table_starts: dict[tuple[str, ...], int] = {(): 0}
    current_table: tuple[str, ...] = ()
    multiline_quote: str | None = None

    for line_index, line in enumerate(lines):
        logical = line.rstrip("\r\n")
        code, multiline_quote, contains_multiline = scan_live_code(
            logical, multiline_quote
        )
        stripped = code.strip()
        if not stripped:
            continue
        header = table_header(stripped)
        if header is not None:
            current_table = header
            table_starts.setdefault(header, line_index)
            continue
        if stripped.startswith("["):
            current_table = (f"<unsupported-table-{line_index}>",)
            continue
        equals = find_unquoted_equals(code)
        if equals is None:
            continue
        key = code[:equals].strip()
        if not BARE_KEY_RE.fullmatch(key):
            continue
        path = (*current_table, key)
        if path not in managed:
            continue
        if contains_multiline:
            raise ReviewedConfigError(
                f"managed key uses unsupported or ambiguous live TOML syntax: {'.'.join(path)}"
            )
        if path in locations:
            raise ReviewedConfigError(f"duplicate managed key in live config.toml: {'.'.join(path)}")
        value_segment = code[equals + 1 :]
        leading = len(value_segment) - len(value_segment.lstrip())
        trailing = len(value_segment) - len(value_segment.rstrip())
        start = equals + 1 + leading
        end = len(code) - trailing if trailing else len(code)
        locations[path] = AssignmentLocation(line_index, start, end)

    for entry in entries:
        actual = lookup(parsed_live, entry.path_parts)
        if actual is not MISSING and entry.path_parts not in locations:
            raise ReviewedConfigError(
                f"managed key uses unsupported or ambiguous live TOML syntax: {entry.path}"
            )
    return lines, locations, table_starts


def detect_newline(text: str, reviewed_text: str) -> str:
    match = re.search(r"\r\n|\n|\r", text)
    if match:
        return match.group(0)
    match = re.search(r"\r\n|\n|\r", reviewed_text)
    return match.group(0) if match else "\n"


def toml_display(value: Any) -> str:
    if value is MISSING:
        return "missing"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return repr(value)


def build_changes(
    entries: list[ReviewedEntry], parsed_live: dict[str, Any]
) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for entry in entries:
        actual = lookup(parsed_live, entry.path_parts)
        if actual is MISSING:
            changes.append(
                {
                    "path": entry.path,
                    "kind": "missing",
                    "actual": "missing",
                    "expected": toml_display(entry.value),
                }
            )
        elif type(actual) is not type(entry.value) or actual != entry.value:
            changes.append(
                {
                    "path": entry.path,
                    "kind": "mismatch",
                    "actual": toml_display(actual),
                    "expected": toml_display(entry.value),
                }
            )
    return changes


def merge_text(
    live_text: str,
    reviewed_text: str,
    entries: list[ReviewedEntry],
    parsed_live: dict[str, Any],
) -> str:
    changes = build_changes(entries, parsed_live)
    if not changes:
        return live_text

    newline = detect_newline(live_text, reviewed_text)
    lines, locations, table_starts = locate_assignments(live_text, entries, parsed_live)
    by_path = {entry.path_parts: entry for entry in entries}

    for path, location in sorted(locations.items(), key=lambda item: item[1].line_index, reverse=True):
        entry = by_path[path]
        line = lines[location.line_index]
        logical = line.rstrip("\r\n")
        ending = line[len(logical) :]
        lines[location.line_index] = (
            logical[: location.value_start]
            + entry.raw_value
            + logical[location.value_end :]
            + ending
        )

    missing_by_table: dict[tuple[str, ...], list[ReviewedEntry]] = {}
    for entry in entries:
        if lookup(parsed_live, entry.path_parts) is MISSING:
            missing_by_table.setdefault(entry.table, []).append(entry)

    if not live_text:
        output: list[str] = []
        root_entries = missing_by_table.pop((), [])
        output.extend(f"{entry.key} = {entry.raw_value}{newline}" for entry in root_entries)
        for table, table_entries in missing_by_table.items():
            if output and output[-1].strip():
                output.append(newline)
            output.append(f"[{'.'.join(table)}]{newline}")
            output.extend(
                f"{entry.key} = {entry.raw_value}{newline}" for entry in table_entries
            )
        return "".join(output)

    existing_tables = set(table_starts)
    insertions: list[tuple[int, list[str]]] = []
    header_indexes = sorted(
        (index, table) for table, index in table_starts.items() if table
    )
    first_table_index = header_indexes[0][0] if header_indexes else len(lines)

    for table, table_entries in missing_by_table.items():
        if table not in existing_tables:
            continue
        if table == ():
            insert_at = first_table_index
        else:
            start = table_starts[table]
            later = [index for index, _ in header_indexes if index > start]
            insert_at = later[0] if later else len(lines)
        insertion_lines = [
            f"{entry.key} = {entry.raw_value}{newline}" for entry in table_entries
        ]
        if insert_at > 0 and lines[insert_at - 1].strip() != "":
            insertion_lines.insert(0, newline)
        if insert_at < len(lines) and lines[insert_at].lstrip().startswith("["):
            insertion_lines.append(newline)
        insertions.append((insert_at, insertion_lines))

    for insert_at, insertion_lines in sorted(insertions, reverse=True):
        lines[insert_at:insert_at] = insertion_lines

    missing_tables = [
        table for table in missing_by_table if table and table not in existing_tables
    ]
    for table in missing_tables:
        if lines and not lines[-1].endswith(("\n", "\r")):
            lines[-1] = lines[-1] + newline
        if lines and lines[-1].strip() != "":
            lines.append(newline)
        lines.append(f"[{'.'.join(table)}]{newline}")
        lines.extend(
            f"{entry.key} = {entry.raw_value}{newline}"
            for entry in missing_by_table[table]
        )

    return "".join(lines)


def evaluate(reviewed_path: Path, live_path: Path) -> dict[str, Any]:
    reviewed_text = read_text(reviewed_path)
    live_text = read_text(live_path, missing_ok=True)
    entries = parse_reviewed(reviewed_text)
    parsed_live = parse_live(live_text, entries)
    changes = build_changes(entries, parsed_live)
    merged = merge_text(live_text, reviewed_text, entries, parsed_live)
    if not changes and merged != live_text:
        raise ReviewedConfigError("internal error: unchanged config produced rewritten text")
    return {
        "schema_version": 1,
        "reviewed_count": len(entries),
        "changed_count": len(changes),
        "changed": bool(changes),
        "live_exists": live_path.exists(),
        "changes": changes,
        "merged_text": merged,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewed-config", type=Path, required=True)
    parser.add_argument("--live-config", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = evaluate(args.reviewed_config, args.live_config)
    except ReviewedConfigError as error:
        print(error, file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
