---
name: compass
description: Maintain Compass durable setup. Use when editing installed skills or agents, repo workflows, manifests, scripts, or install wiring.
---

# Compass

Use this skill when changing Compass itself. Its job is to route durable setup
changes to the right source file while preserving the install boundary.

Repository: [ariobarin/compass](https://github.com/ariobarin/compass).

## Stance

Treat this repo as reviewed source, not a backup of a live config home
(`~/.codex`, `~/.agents`, or `~/.claude`). Keep installed agentic behavior
separate from repo-maintainer guidance. Let repo-local docs carry procedure
instead of reconstructing the maintenance flow from memory.

Compass owns the portable bundle. When a bundled skill, agent, hook, script, or
reviewed config fragment depends on another bundled capability, make the
capability exact. Fix the source, install map, reviewed config, live verifier,
or agent contract. Do not add alternate-path, best-effort, or compatibility
guidance for a capability Compass can provide.

## Read First

- Read the repo-root `AGENTS.md` and `local-docs/maintenance-learnings.md`.
- Read `workflows/portable-config.md` for repo-to-live install, snapshot, or
  drift work.
- Read `workflows/addition-intake.md` before adding rules, skills, agents,
  workflows, scripts, manifests, or config fragments.

## Route Changes

- Installed agentic behavior: `codex/AGENTS.md`, `codex/agents/`,
  `codex/skills/`, and the Claude mirrors `claude/skills/`, `claude/agents/`.
- Repo-maintainer guidance: root `AGENTS.md`, `workflows/`, `local-docs/`,
  `manifests/`, `scripts/`.
- Reviewed config fragments: `codex/config.review.toml`; do not treat it as a
  direct replacement for live `config.toml`.
- Installed skill additions: update `manifests/portable-files.toml`;
  `scripts/common.ps1` reads that manifest for the install map.

## Validate The Repo Change

- Run `.\scripts\doctor.ps1` before calling the change done.
- For skill edits, run the local skill validator when present, using the active
  config home for bundled system tooling instead of a hard-coded user path.
- Run `.\scripts\verify-live.ps1 -SkipCodexCommand` when live drift matters.
- Use a PR as the review unit.
