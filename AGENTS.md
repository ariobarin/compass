# Repository Guidance

This repo is the reviewed source for portable Codex setup. It is not a raw
backup of `~/.codex`.

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
