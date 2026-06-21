---
name: codex-portable
description: Maintain codex-portable durable setup. Use when editing installed skills or agents, repo workflows, manifests, scripts, or install wiring.
---

# Codex Portable

Use this skill when changing `codex-portable` itself. Its job is to route durable
setup changes to the right source file while preserving the install boundary.

## Stance

Treat this repo as reviewed source, not a backup of live `~/.codex`. Keep
installed agentic behavior separate from repo-maintainer guidance. Let repo-local
docs carry procedure instead of reconstructing the maintenance flow from memory.

## Read First

- Read the repo-root `AGENTS.md` and `local-docs/maintenance-learnings.md`.
- Read `workflows/portable-config.md` for repo-to-live install, snapshot, or
  drift work.
- Read `workflows/addition-intake.md` before adding rules, skills, agents,
  workflows, scripts, manifests, or config fragments.

## Route Changes

- Installed agentic behavior: `codex/AGENTS.md`, `codex/agents/`,
  `codex/skills/`.
- Repo-maintainer guidance: root `AGENTS.md`, `workflows/`, `local-docs/`,
  `manifests/`, `scripts/`.
- Reviewed config fragments: `codex/config.review.toml`; do not treat it as a
  direct replacement for live `config.toml`.
- Installed skill additions: update `manifests/portable-files.toml` and
  `scripts/common.ps1` together.

## Validate The Repo Change

- Run `.\scripts\doctor.ps1` before calling the change done.
- For skill edits, run the local skill validator when present, using the active
  Codex home instead of a hard-coded user path.
- Run `.\scripts\verify-live.ps1 -SkipCodexCommand` when live drift matters.
- Use a PR as the review unit.
