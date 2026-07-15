# Repository Guidance

Compass is the reviewed source for portable Codex setup. It is not a raw backup
of `~/.codex`, `$HOME/.agents`, or `$HOME/.claude`.

- `codex/AGENTS.md` is the portable source for the live global
  `~/.codex/AGENTS.md`. Only put session-wide defaults there.
- Installed agentic guidance source belongs under `codex/AGENTS.md`,
  `codex/agents/`, or `codex/skills/`.
- Installed Codex hook behavior belongs under `codex/hooks.json` or
  `codex/hooks/`.
- This repo-root `AGENTS.md` is for Compass maintenance guidance.
- If a rule only makes sense while editing Compass, put it here or in
  `workflows/` or `local-docs/`, not in installed agentic docs.
- Repo-maintainer guidance belongs in this file, `workflows/`, `local-docs/`,
  `manifests/`, or `scripts/`. These surfaces are not copied into live install
  targets as agent behavior.
- Keep `codex/AGENTS.md` short and global.
- Put detailed operating behavior in the narrowest surface: installed agents or
  skills for reusable agent capability, hook docs for hook operation, repo
  workflows for Compass maintenance, scripts for mechanical checks, and
  manifests for boundaries.
- Treat `codex/agents` and manifest-listed `codex/skills` as one portable
  bundle. When editing bundled skills or agents, reference bundled capabilities
  directly instead of making them sound optional. Keep conditional wording for
  external services, permissions, credentials, CI, browser state, MCP tools,
  goal tools, or repository access.
- For Compass-owned capabilities, fix the config, install map, verifier, or
  agent contract. Do not add alternate-path, best-effort, or compatibility
  prose to installed skills when this repo can make the capability exact.
- Codex is the reviewed source of truth for shared skills and agents. Claude
  skills and most agents derive from `codex/skills/<name>` and
  `codex/agents/<name>.toml` at install time, so a shared change lands on both
  runtimes. A platform-specific direct agent may live under `claude/agents/`
  only when the shared transform cannot express its frontmatter, tools, or
  isolation contract. See `workflows/claude-config.md`.
- For nontrivial changes to this repo, read
  `local-docs/maintenance-learnings.md` before editing.
- For Compass audits, use `workflows/compass-review-program.md` before pruning
  installed skills, agents, hooks, or maintainer guidance.
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
- Flag changes that hardcode `$HOME/.claude` when the path should respect
  `-ClaudeHome`.
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
  lines are read, the agent should still see the role, terminal result,
  non-negotiables, and failure mode to avoid.
- For goal-bearing or long-lived guidance, put the finished state and completion
  evidence before the current next action. Keep changing owners, blockers, and
  next actions in a named live state surface rather than in the durable
  objective.
- Lead with the mental model, not a checklist.
- Use procedures only for fragile or exact operations.
- Prefer principles, boundaries, and short examples over exhaustive branches.
- Trust the agent to reason from the right stance instead of turning the skill
  into a flowchart.
- Keep concrete prompts and templates where they teach the role or preserve a
  handoff contract.
