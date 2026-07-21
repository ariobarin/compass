#!/usr/bin/env python3
"""Derive carried-pack Claude agent files from their Codex TOML sources.

Each carried pack may define agents under carried/<pack>/agents/<name>.toml.
The Codex TOML is canonical; the parallel Claude markdown file under
carried/<pack>/claude-agents/<name>.md is generated from it so the pair cannot
drift. Pass --check to verify committed files are fresh; pass no flag to write.
"""
from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARRIED = ROOT / "carried"

# Claude install wiring for carried agents (tools and color). The Codex TOML is
# the canonical source for identity and instructions; this table supplies the
# platform-specific frontmatter that has no TOML home.
CARRIED_FRONTMATTER = {
    "benchmark-infra-reviewer": {"tools": "Read, Grep, Glob, Bash", "color": "red"},
}


def render_agent(toml_path: Path) -> str:
    with toml_path.open("rb") as handle:
        data = tomllib.load(handle)
    name = data["name"]
    description = data["description"]
    body = data["developer_instructions"].strip()
    frontmatter = CARRIED_FRONTMATTER.get(name)
    if frontmatter is None:
        raise SystemExit(f"no carried frontmatter entry for agent: {name}")
    lines = ["---", f"name: {name}", f"description: {description}"]
    if frontmatter.get("tools"):
        lines.append(f"tools: {frontmatter['tools']}")
    lines.append("model: inherit")
    if frontmatter.get("color"):
        lines.append(f"color: {frontmatter['color']}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body + "\n"


def carried_targets() -> list[tuple[Path, Path]]:
    targets = []
    for toml_path in sorted(CARRIED.glob("*/agents/*.toml")):
        pack = toml_path.parents[1].name
        md_path = CARRIED / pack / "claude-agents" / f"{toml_path.stem}.md"
        targets.append((toml_path, md_path))
    return targets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    stale = []
    for toml_path, md_path in carried_targets():
        desired = render_agent(toml_path)
        current = md_path.read_text(encoding="utf-8") if md_path.exists() else None
        if desired != current:
            if args.check:
                stale.append(str(md_path))
            else:
                md_path.parent.mkdir(parents=True, exist_ok=True)
                with md_path.open("w", encoding="utf-8", newline="\n") as handle:
                    handle.write(desired)
    if stale:
        for path in stale:
            print(path)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
