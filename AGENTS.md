# Repository Guidance

This repo is the reviewed source for portable Codex setup. It is not a raw
backup of `~/.codex`.

- `codex/AGENTS.md` is the portable source for the live global
  `~/.codex/AGENTS.md`. Only put session-wide defaults there.
- This repo-root `AGENTS.md` is for codex-portable maintenance guidance.
- If a rule only makes sense while editing codex-portable, put it here or in
  `workflows/` or `local-docs/`, not in `codex/AGENTS.md`.
- Keep `codex/AGENTS.md` short and global.
- Put detailed operating behavior in `workflows/`, skills, scripts, or
  manifests.
- For nontrivial changes to this repo, read
  `local-docs/maintenance-learnings.md` before editing.
- Do not commit auth, sessions, logs, caches, browser state, SQLite files, or
  generated plugin caches.
- Run `.\scripts\doctor.ps1` before committing.
- Use `.\scripts\verify-live.ps1 -SkipCodexCommand` to inspect live drift.
- Review `codex/config.review.toml` manually before copying any config into a
  live Codex home.

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
