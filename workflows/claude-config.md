# Portable Claude Config Workflow

Claude Code is a first-class Compass install target with its own global runtime
instructions. Shared runtime-neutral skills and most agent roles still derive
from reviewed Codex sources.

## Separate Global Guidance

Maintain `claude/CLAUDE.md` directly and install it as
`$HOME/.claude/CLAUDE.md`. Maintain `codex/AGENTS.md` separately.

The two files may share values such as writing rules, worktree discipline,
planning authority, and evidence standards. They should state runtime-specific
model, delegation, tools, and context behavior directly instead of pretending
both environments are identical.

The current Claude profile uses GLM-5.2 for delegated work. Claude guidance
names that fact so generic examples do not cause invented Opus, Sonnet, Haiku,
or other unavailable routes.

## Shared Skills And Agents

- Author a shared skill under `codex/skills/<name>`.
- List it in `[claude].derived_skills` when its behavior is runtime-neutral.
- Author a shared agent under `codex/agents/<name>.toml`.
- List it in `[claude].derived_agents` when the transform can express its
  frontmatter and isolation contract.
- Put a platform-specific direct agent under `claude/agents/<name>.md` and list
  it in `[claude].agents` only when derivation is insufficient.
- Keep carried packs out of Claude global installation unless a target project
  explicitly adopts them.

At install time, a derived skill copies `SKILL.md`, `references/`, `scripts/`,
and `assets/` while excluding `agents/openai.yaml`. A derived agent receives
Claude frontmatter from the reviewed transform and the role body from its Codex
TOML source. Direct Claude agents copy as authored.

## Install Map

`manifests/portable-files.toml` owns:

- `[claude].files` for separately authored top-level files;
- `[claude].derived_skills` for shared skills;
- `[claude].agents` for direct platform-specific agents;
- `[claude].derived_agents` for shared derived roles.

With `-ClaudeHome`, installation targets that root. Otherwise the target is
`$HOME/.claude`.

The manifest, installer transform, retirement map, doctor checks, and install
round-trip tests are the mechanical source of truth. Update them together.

## Review

Before accepting a Claude change:

- confirm whether the behavior is global, shared, direct, carried, or
  project-specific;
- inspect `claude/CLAUDE.md` for concise, current runtime truth;
- inspect the derived output contract rather than maintaining a duplicate source;
- verify model names and routing against dated current calibration;
- remove retired files from every previously owned live location;
- run doctor and install round-trip validation.
