# Contributing

This repo is reviewed source for a portable Codex setup. It is not a raw
backup of a live Codex home, and contributions should preserve that boundary.

Good changes make the setup easier to review, reinstall, explain, or verify.
They do not add private machine state, generated runtime state, or broad agent
behavior just because it happened to be useful once.

## Before A PR

- Read `README.md`, `philosophy.md`, `AGENTS.md`, and
  `local-docs/maintenance-learnings.md`.
- Keep the change narrow enough that a reviewer can see the portable boundary.
- Run `.\scripts\doctor.ps1`.
- If the change affects live install behavior, also run
  `.\scripts\verify-live.ps1 -SkipCodexCommand`.
- Leave auth, sessions, logs, caches, browser state, SQLite files, generated
  plugin caches, and local override files out of the PR.

## Scope

Installed agentic behavior belongs under `codex/AGENTS.md`, `codex/agents/`,
or `codex/skills/`. Repo-maintainer guidance belongs in `AGENTS.md`,
`workflows/`, `local-docs/`, `manifests/`, or `scripts/`.

Use the narrowest surface that fits the change. A skill should teach a durable
role or capability. A workflow should capture a recurring repo process. A script
should handle a mechanical check. A manifest should define a boundary.

## Review Expectations

Prefer small PRs with clear motivation. In the title and body, name the
boundary, behavior, or risk the change improves.

When in doubt, explain why a file belongs in this portable repo instead of in a
target project, local Codex home, plugin cache, or ignored machine-local file.
