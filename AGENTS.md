# Repository Guidance

Compass is the reviewed source for portable Codex setup. It is not a raw backup
of `~/.codex` or `$HOME/.agents`.

- `codex/AGENTS.md` is the portable source for the live global
  `~/.codex/AGENTS.md`. Only put session-wide defaults there.
- Installed agentic guidance belongs under `codex/AGENTS.md`,
  `codex/agents/`, or `codex/skills/`.
- This repo-root `AGENTS.md` is for Compass maintenance guidance.
- If a rule only makes sense while editing Compass, put it here or in
  `workflows/` or `local-docs/`, not in installed agentic docs.
- Repo-maintainer guidance belongs in this file, `workflows/`, `local-docs/`,
  `manifests/`, or `scripts/`. These surfaces are not copied into live install
  targets as agent behavior.
- Keep `codex/AGENTS.md` short and global.
- Put detailed operating behavior in the narrowest surface: installed agents or
  skills for reusable agent capability, repo workflows for Compass
  maintenance, scripts for mechanical checks, and manifests for boundaries.
- Treat `codex/agents` and manifest-listed `codex/skills` as one portable
  bundle. When editing bundled skills or agents, reference bundled capabilities
  directly instead of making them sound optional. Keep conditional wording for
  external services, permissions, credentials, CI, browser state, MCP tools,
  goal tools, or repository access.
- For Compass-owned capabilities, fix the config, install map, verifier, or
  agent contract. Do not add alternate-path, best-effort, or compatibility
  prose to installed skills when this repo can make the capability exact.
- `claude/skills/` and `claude/agents/` are the Claude Code mirror of the Codex
  portable bundle. The same install map covers both surfaces. Keep the two in
  step when a change applies to both runtimes, and document the port in
  `workflows/claude-config.md`.
- For nontrivial changes to this repo, read
  `local-docs/maintenance-learnings.md` before editing.
- Do not commit auth, sessions, logs, caches, browser state, SQLite files, or
  generated plugin caches.
- Run `.\scripts\doctor.ps1` before committing.
- Use `.\scripts\verify-live.ps1 -SkipCodexCommand` to inspect live drift.
- Review `codex/config.review.toml` manually before copying any config into a
  live Codex home.

## Review guidelines

- Flag changes that accidentally expand the portable scope by committing auth,
  sessions, logs, caches, browser state, SQLite files, generated plugin state,
  or other local-only Codex data.
- Flag changes that hardcode `~/.codex`, `%USERPROFILE%\\.codex`, or
  `$HOME/.agents` when the path should respect `CODEX_HOME` or `-AgentsHome`.
- Flag config changes that introduce undocumented keys, stale settings, or
  stronger default authority without a current-doc justification.
- Flag guidance that routes project-specific behavior into Compass
  when it should live in the target project repo instead.
- Flag tracked `AGENTS.override.md` or `rules/` files unless they were
  intentionally adopted as reviewed portable policy.
- Flag project-specific agents or skills routed into Compass when they
  should live in the target repo.

## Skill authoring

Skills should shape judgment before they prescribe steps. Start by making the
agent understand the role it is taking on, why that role exists, what failure
mode it prevents, and what boundaries preserve good judgment.

- Front-load action-critical guidance. If only the first screen or first 10
  lines are read, the agent should still see the role, non-negotiables, next
  action, and failure mode to avoid.
- Lead with the mental model, not a checklist.
- Use procedures only for fragile or exact operations.
- Prefer principles, boundaries, and short examples over exhaustive branches.
- Trust the agent to reason from the right stance instead of turning the skill
  into a flowchart.
- Keep concrete prompts and templates where they teach the role or preserve a
  handoff contract.
