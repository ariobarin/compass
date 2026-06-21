# Repository Guidance

This repo is the reviewed source for portable Codex setup. It is not a raw
backup of `~/.codex`.

- `codex/AGENTS.md` is the portable source for the live global
  `~/.codex/AGENTS.md`. Only put session-wide defaults there.
- Installed agentic guidance belongs under `codex/AGENTS.md`,
  `codex/agents/`, or `codex/skills/`.
- This repo-root `AGENTS.md` is for codex-portable maintenance guidance.
- If a rule only makes sense while editing codex-portable, put it here or in
  `workflows/` or `local-docs/`, not in installed agentic docs.
- Repo-maintainer guidance belongs in this file, `workflows/`, `local-docs/`,
  `manifests/`, or `scripts/`. These surfaces are not copied into live Codex as
  agent behavior.
- Keep `codex/AGENTS.md` short and global.
- Put detailed operating behavior in the narrowest surface: installed agents or
  skills for reusable agent capability, repo workflows for codex-portable
  maintenance, scripts for mechanical checks, and manifests for boundaries.
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
- Flag changes that hardcode `~/.codex` or `%USERPROFILE%\\.codex` when the
  path should respect `CODEX_HOME`.
- Flag config changes that introduce undocumented keys, stale settings, or
  stronger default authority without a current-doc justification.
- Flag guidance that routes project-specific behavior into `codex-portable`
  when it should live in the target project repo instead.
- Flag tracked `AGENTS.override.md` or `rules/` files unless they were
  intentionally adopted as reviewed portable policy.
- Flag project-specific agents or skills routed into `codex-portable` when they
  should live in the target repo.

## Skill authoring

Skills should shape judgment before they prescribe steps. Start by making the
agent understand the role it is taking on, why that role exists, what failure
mode it prevents, and what boundaries preserve good judgment.

- Lead with the mental model, not a checklist.
- Use procedures only for fragile or exact operations.
- Prefer principles, boundaries, and short examples over exhaustive branches.
- Trust the agent to reason from the right stance instead of turning the skill
  into a flowchart.
- Keep concrete prompts and templates where they teach the role or preserve a
  handoff contract.
