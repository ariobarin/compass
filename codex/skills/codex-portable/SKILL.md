---
name: codex-portable
description: Edit the codex-portable repo for durable Codex setup changes. Use when updating Codex config, skills, agents, workflows, manifests, or install wiring.
---

# Codex Portable

Use this skill when the task is to change the reviewed portable Codex setup in
this repo, not just explain it.

## Start Here

1. Read the repo-root `AGENTS.md` and `local-docs/maintenance-learnings.md`.
2. Read `workflows/portable-config.md` for the repo-to-live flow.
3. Read `workflows/addition-intake.md` when deciding whether the change belongs
   in a skill, agent, workflow, script, manifest entry, or config fragment.

## Core Rule

Treat the current portable configuration as editable source, not a frozen
snapshot.

When the user wants durable Codex behavior changed, modify or append the right
files in this repo. Treat existing portable files as editable source.

Use the reviewed repo copy as the change surface when it owns the behavior.
Reserve live `~/.codex` edits for validation, drift checks, or explicitly live
state.

## Route The Change

- Update `codex/AGENTS.md` for session-wide defaults that should travel with the
  portable setup.
- Update `codex/config.review.toml` for stable config fragments that should be
  reviewed, not auto-installed.
- Update `codex/skills/` for specialized agent behavior.
- Update `codex/agents/` for focused reviewer or researcher personas.
- Update `workflows/` for repeated human processes.
- Update `scripts/` for mechanical checks or sync logic.
- Update `local-docs/` for repo-only maintenance lessons.
- Update `manifests/portable-files.toml` and `scripts/common.ps1` when adding an
  installed skill or changing an install surface that those files map.

## Validate The Repo Change

1. Update the durable artifact and any required install wiring in the same
   branch.
2. Run `.\scripts\doctor.ps1`.
3. Run `python $env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py <skill-folder>`
   for skill edits.
4. Run `.\scripts\verify-live.ps1 -SkipCodexCommand` when live drift matters.
5. Use a PR as the review unit.
