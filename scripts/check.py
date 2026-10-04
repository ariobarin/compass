#!/usr/bin/env python3
"""Check the published skill catalog and its local source files (Python 3.11+)."""

import json
from pathlib import Path
import re
import sys
import tomllib
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def frontmatter_value(frontmatter, key, path):
    values = re.findall(rf"^{key}:[ \t]*(.*)$", frontmatter, re.MULTILINE)
    if len(values) != 1 or re.search(rf"^{key}:[^\n]*\n[ \t]+\S", frontmatter, re.MULTILINE):
        raise ValueError(f"{path}: expected one single-line {key}")
    value = values[0].strip()
    if value.startswith('"'):
        value = json.loads(value)
    if not isinstance(value, str) or not value.strip() or value.startswith(("|", ">")) or "\n" in value:
        raise ValueError(f"{path}: {key} must be a nonempty single-line string")
    return value


def check():
    manifest = json.loads((ROOT / "manifests/portable-files.json").read_text(encoding="utf-8"))
    names = manifest["agents"]["skills"]
    if not isinstance(names, list) or any(
        not isinstance(name, str)
        or len(name) > 64
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
        for name in names
    ):
        raise ValueError(
            "agents.skills must be an array of names of 1 to 64 lowercase letters, digits, "
            "and single internal hyphens"
        )
    if len(set(names)) != len(names):
        raise ValueError("agents.skills contains duplicate names")

    skills = {
        path.name: path / "SKILL.md"
        for path in (ROOT / "codex/skills").iterdir()
        if path.is_dir()
    }
    missing = sorted(set(names) - skills.keys())
    unlisted = sorted(skills.keys() - set(names))
    if missing or unlisted:
        raise ValueError(f"catalog mismatch: missing SKILL.md for {missing}; unlisted skills {unlisted}")

    (ROOT / "codex/AGENTS.md").read_text(encoding="utf-8")
    for name in names:
        path = skills[name]
        text = path.read_text(encoding="utf-8")
        header = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
        if not header:
            raise ValueError(f"{path.relative_to(ROOT)}: missing frontmatter")
        frontmatter = header.group(1)
        if frontmatter_value(frontmatter, "name", path.relative_to(ROOT)) != name:
            raise ValueError(f"{path.relative_to(ROOT)}: name must match directory {name}")
        description = frontmatter_value(frontmatter, "description", path.relative_to(ROOT))
        if len(description) > 1024:
            raise ValueError(f"{path.relative_to(ROOT)}: description exceeds 1024 characters")

        metadata = path.parent / "agents/openai.yaml"
        if not metadata.read_text(encoding="utf-8").strip():
            raise ValueError(f"{metadata.relative_to(ROOT)}: empty host metadata")

    for path in (ROOT / "codex/agents").glob("*.toml"):
        with path.open("rb") as source:
            tomllib.load(source)

    documents = [
        *ROOT.glob("*.md"),
        *(ROOT / "codex").rglob("*.md"),
        *(ROOT / "scripts").glob("*.md"),
    ]
    for path in documents:
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text):
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                raise ValueError(f"{path.relative_to(ROOT)}: missing local link {link}")

    print(f"catalog checks passed: {len(names)} skills")


if __name__ == "__main__":
    try:
        check()
    except (OSError, ValueError, KeyError, TypeError) as error:
        sys.exit(f"catalog check failed: {error}")
