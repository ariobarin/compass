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
