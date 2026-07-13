#!/usr/bin/env python3
"""Inventory repository-owned prompt surfaces without judging their content."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

TEXT_SUFFIXES = {".json", ".md", ".toml", ".txt", ".yaml", ".yml"}
FRONTMATTER_FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")


@dataclass(frozen=True)
class Surface:
    path: str
    category: str
    activation: str
    bytes: int
    characters: int
    estimated_tokens: int
    owner: str | None = None


@dataclass(frozen=True)
class AgentRoute:
    name: str
    path: str
    model: str | None
    reasoning_effort: str | None


@dataclass(frozen=True)
class SkillRoute:
    name: str
    path: str
    description_characters: int
    description_estimated_tokens: int


def estimate_tokens(characters: int, chars_per_token: float) -> int:
    return math.ceil(characters / chars_per_token) if characters else 0


def relative_path(root: Path, path: Path) -> str:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError as error:
        raise ValueError(f"prompt path escapes repository: {path.name}") from error


def read_text(root: Path, path: Path) -> str:
    relative_path(root, path)
    return path.read_text(encoding="utf-8")


def parse_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    closing = next(
        (index for index in range(1, len(lines)) if lines[index].strip() == "---"),
        -1,
    )
    if closing < 0:
        return {}, text

    fields: dict[str, str] = {}
    index = 1
    while index < closing:
        match = FRONTMATTER_FIELD_RE.match(lines[index])
        if not match:
            index += 1
            continue
        key, raw = match.groups()
        if raw.strip() in {"|", ">"}:
            block: list[str] = []
            index += 1
            while index < closing and (
                not lines[index].strip() or lines[index].startswith((" ", "\t"))
            ):
                block.append(lines[index].strip())
                index += 1
            fields[key] = " ".join(part for part in block if part).strip()
            continue
        fields[key] = parse_scalar(raw)
        index += 1
    return fields, "\n".join(lines[closing + 1 :])


def load_skill_names(root: Path) -> list[str]:
    manifest_path = root / "manifests" / "portable-files.toml"
    with manifest_path.open("rb") as handle:
        manifest = tomllib.load(handle)
    raw = manifest.get("agents", {}).get("skills")
    if not isinstance(raw, list) or any(
        not isinstance(item, str) or not item.strip() for item in raw
    ):
        raise ValueError("portable manifest requires [agents].skills as a string array")
    names = list(dict.fromkeys(item.strip() for item in raw))
    if any(
        Path(name).name != name or name in {".", ".."} or "\\" in name
        for name in names
    ):
        raise ValueError("portable skill names must be single path components")
    return names


def make_surface(
    root: Path,
    path: Path,
    category: str,
    activation: str,
    chars_per_token: float,
    owner: str | None = None,
) -> Surface:
    text = read_text(root, path)
    return Surface(
        path=relative_path(root, path),
        category=category,
        activation=activation,
        bytes=len(text.encode("utf-8")),
        characters=len(text),
        estimated_tokens=estimate_tokens(len(text), chars_per_token),
        owner=owner,
    )


def discover_agents(
    root: Path, chars_per_token: float
) -> tuple[list[Surface], list[AgentRoute]]:
    surfaces: list[Surface] = []
    routes: list[AgentRoute] = []
    agents_root = root / "codex" / "agents"
    if not agents_root.is_dir():
        return surfaces, routes

    for path in sorted(agents_root.glob("*.toml")):
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        name = data.get("name") if isinstance(data.get("name"), str) else path.stem
        model = data.get("model") if isinstance(data.get("model"), str) else None
        effort = (
            data.get("model_reasoning_effort")
            if isinstance(data.get("model_reasoning_effort"), str)
            else None
        )
        surfaces.append(
            make_surface(root, path, "agent", "routed", chars_per_token, name)
        )
        routes.append(
            AgentRoute(
                name=name,
                path=relative_path(root, path),
                model=model,
                reasoning_effort=effort,
            )
        )
    return surfaces, routes


def iter_payload_files(skill_root: Path) -> Iterable[tuple[Path, str]]:
    interface = skill_root / "agents" / "openai.yaml"
    if interface.is_file():
        yield interface, "skill_interface"

    for folder_name, category in (
        ("references", "reference"),
        ("templates", "template"),
        ("assets", "template"),
    ):
        folder = skill_root / folder_name
        if not folder.is_dir():
            continue
        for path in sorted(candidate for candidate in folder.rglob("*") if candidate.is_file()):
            if path.suffix.lower() in TEXT_SUFFIXES:
                yield path, category


def discover_skills(
    root: Path, chars_per_token: float
) -> tuple[list[Surface], list[SkillRoute]]:
    surfaces: list[Surface] = []
    routes: list[SkillRoute] = []
    for skill_name in load_skill_names(root):
        skill_root = root / "codex" / "skills" / skill_name
        skill_file = skill_root / "SKILL.md"
        if not skill_file.is_file():
            raise ValueError(f"manifest skill is missing SKILL.md: {skill_name}")
        text = read_text(root, skill_file)
        fields, _ = parse_frontmatter(text)
        routed_name = fields.get("name", skill_name).strip() or skill_name
        description = re.sub(r"\s+", " ", fields.get("description", "")).strip()
        surfaces.append(
            make_surface(root, skill_file, "skill", "routed", chars_per_token, routed_name)
        )
        routes.append(
            SkillRoute(
                name=routed_name,
                path=relative_path(root, skill_file),
                description_characters=len(description),
                description_estimated_tokens=estimate_tokens(
                    len(description), chars_per_token
                ),
            )
        )
        for path, category in iter_payload_files(skill_root):
            surfaces.append(
                make_surface(
                    root,
                    path,
                    category,
                    "loaded_by_reference",
                    chars_per_token,
                    routed_name,
                )
            )
    return surfaces, routes


def build_report(root: Path, chars_per_token: float) -> dict[str, object]:
    root = root.resolve()
    surfaces: list[Surface] = []

    for path in (root / "AGENTS.md", root / "codex" / "AGENTS.md"):
        if path.is_file():
            surfaces.append(
                make_surface(root, path, "global", "always_loaded", chars_per_token)
            )

    agent_surfaces, agent_routes = discover_agents(root, chars_per_token)
    skill_surfaces, skill_routes = discover_skills(root, chars_per_token)
    surfaces.extend(agent_surfaces)
    surfaces.extend(skill_surfaces)

    review_config = root / "codex" / "config.review.toml"
    if review_config.is_file():
        surfaces.append(
            make_surface(
                root,
                review_config,
                "config",
                "manually_selected",
                chars_per_token,
            )
        )

    surfaces.sort(key=lambda item: item.path)
    agent_routes.sort(key=lambda item: (item.name, item.path))
    skill_routes.sort(key=lambda item: (item.name, item.path))

    by_category: dict[str, dict[str, int]] = {}
    for surface in surfaces:
        bucket = by_category.setdefault(
            surface.category, {"files": 0, "bytes": 0, "estimated_tokens": 0}
        )
        bucket["files"] += 1
        bucket["bytes"] += surface.bytes
        bucket["estimated_tokens"] += surface.estimated_tokens

    return {
        "schema_version": 1,
        "kind": "prompt_inventory",
        "estimator": {
            "kind": "character_ratio",
            "chars_per_token": chars_per_token,
            "note": "Token values are deterministic estimates, not tokenizer output.",
        },
        "summary": {
            "files": len(surfaces),
            "bytes": sum(item.bytes for item in surfaces),
            "characters": sum(item.characters for item in surfaces),
            "estimated_tokens": sum(item.estimated_tokens for item in surfaces),
            "by_category": {key: by_category[key] for key in sorted(by_category)},
        },
        "surfaces": [asdict(item) for item in surfaces],
        "agent_routing": [asdict(item) for item in agent_routes],
        "skill_routing": [asdict(item) for item in skill_routes],
        "interpretation": {
            "size_is_not_quality": True,
            "no_behavioral_gate": True,
            "omitted_analyses": [
                "instruction_strength",
                "semantic_duplication",
                "prompt_quality",
                "behavioral_equivalence",
            ],
        },
    }


def render_text(report: dict[str, object]) -> str:
    summary = report["summary"]
    assert isinstance(summary, dict)
    lines = [
        "prompt inventory",
        f"files: {summary['files']}",
        f"bytes: {summary['bytes']}",
        f"estimated tokens: {summary['estimated_tokens']}",
        "",
        "tokens category activation path",
    ]
    surfaces = report["surfaces"]
    assert isinstance(surfaces, list)
    for surface in sorted(
        surfaces,
        key=lambda item: (-item["estimated_tokens"], item["path"]),
    ):
        lines.append(
            f"{surface['estimated_tokens']:>6} "
            f"{surface['category']:<15} "
            f"{surface['activation']:<19} "
            f"{surface['path']}"
        )
    lines.extend(["", "agent routing", "name model effort path"])
    routes = report["agent_routing"]
    assert isinstance(routes, list)
    for route in routes:
        lines.append(
            f"{route['name']} {route['model'] or '-'} "
            f"{route['reasoning_effort'] or '-'} {route['path']}"
        )
    lines.extend(
        [
            "",
            "interpretation: descriptive inventory only; size is not a quality gate",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--chars-per-token", type=float, default=4.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.chars_per_token <= 0:
        parser.error("chars per token must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(args.root, args.chars_per_token)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
        print(f"prompt inventory failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
