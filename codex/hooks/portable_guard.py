#!/usr/bin/env python3
"""Portable Codex hook guard launcher."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def main() -> int:
    return 0


def load_guard_main():
    guard_root = Path(__file__).with_name("guard")
    if not guard_root.exists():
        return None

    package_spec = importlib.util.spec_from_file_location(
        "guard",
        guard_root / "__init__.py",
        submodule_search_locations=[str(guard_root)],
    )
    if package_spec is None or package_spec.loader is None:
        raise ModuleNotFoundError("guard", name="guard")

    runner_spec = importlib.util.spec_from_file_location("guard.runner", guard_root / "runner.py")
    if runner_spec is None or runner_spec.loader is None:
        raise ModuleNotFoundError("guard.runner", name="guard.runner")

    for module_name in list(sys.modules):
        if module_name == "guard" or module_name.startswith("guard."):
            del sys.modules[module_name]

    package_module = importlib.util.module_from_spec(package_spec)
    sys.modules["guard"] = package_module
    package_spec.loader.exec_module(package_module)

    runner_module = importlib.util.module_from_spec(runner_spec)
    sys.modules["guard.runner"] = runner_module
    runner_spec.loader.exec_module(runner_module)
    return runner_module.main


try:
    guard_main = load_guard_main()
except PermissionError:
    guard_main = None

if guard_main is not None:
    main = guard_main


if __name__ == "__main__":
    raise SystemExit(main())
