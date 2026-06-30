"""Dispatch portable Codex hook events to guard modules."""

from __future__ import annotations

import re
import sys
from importlib import import_module
from types import ModuleType

from .common import read_input

MODULE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
RESERVED_MODULES = {"common", "runner"}


def iter_guard_modules(module_names: list[str]) -> list[ModuleType]:
    modules: list[ModuleType] = []
    package = __package__ or "guard"
    seen: set[str] = set()

    for module_name in module_names:
        if module_name in seen:
            continue
        if (
            not MODULE_NAME_RE.fullmatch(module_name)
            or module_name in RESERVED_MODULES
            or module_name.startswith("_")
        ):
            raise ValueError(f"invalid guard module: {module_name}")
        seen.add(module_name)
        modules.append(import_module(f"{package}.{module_name}"))
    return modules


def dispatch(data: dict, module_names: list[str]) -> bool:
    event = str(data.get("hook_event_name") or "")
    for module in iter_guard_modules(module_names):
        handlers = getattr(module, "HANDLERS", {})
        handler = handlers.get(event)
        if handler and handler(data):
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    dispatch(read_input(), argv[1:])
    return 0
