# codex-portable

Portable source for the human-owned Codex setup.

This repo is intentionally an allowlist, not a backup of the whole Codex home. The
live Codex directory contains auth, logs, sessions, caches, databases, generated
plugin state, browser state, and machine-specific runtime paths. Those are not
portable and should not be committed.

Hosted Codex web settings, cloud task history, repository connections, and
workspace connector installs such as Slack or Linear are also out of scope for
this repo. They are service-side state, not portable files.

## Layout

- `codex/AGENTS.md`: portable source for the live global `~/.codex/AGENTS.md`.
  Keep only session-wide defaults there.
- `AGENTS.md`: repo-local maintenance guidance for this portable config repo.
  Use this for codex-portable process and review rules.
- `codex/keybindings.json`: portable keyboard bindings.
- `codex/agents/`: custom agents.
- `codex/skills/`: custom skills, excluding system and plugin cache skills.
- `codex/config.review.toml`: reviewed config fragments that are useful on a new
  machine. This is not installed automatically.
- `workflows/`: durable operating notes for recurring work.
- `local-docs/`: repo-local maintenance learnings that are not installed into a
  live Codex home.
- `manifests/portable-files.toml`: the allowlist and local-only denylist.
- `manifests/tool-surfaces.md`: review notes for tools that can touch local or
  external state.
- `scripts/`: snapshot, diff, install, and health check helpers.

## Common commands

Preview the difference between this repo and the live Codex home:

```powershell
.\scripts\diff-live.ps1
```

Check the repo for obvious portability mistakes:

```powershell
.\scripts\doctor.ps1
```

Check whether live Codex files match the portable allowlist and ask Codex to
report active instruction sources:

```powershell
.\scripts\verify-live.ps1
```

Install reviewed portable files into the live Codex home:

```powershell
.\scripts\install.ps1 -Apply
```

Refresh the repo from the current live allowlist:

```powershell
.\scripts\snapshot.ps1 -Apply
```

Without `-Apply`, `snapshot.ps1` and `install.ps1` run in review mode and explain
what they would change.

## Rules

- Keep this repo small and boring.
- Copy ordinary files into normal Codex locations. Avoid symlink-based setup.
- Treat `codex/config.review.toml` as a draft for manual review, not a direct
  replacement for the live generated `config.toml`.
- Do not commit secrets, auth files, SQLite state, logs, session history, caches,
  browser profiles, generated plugin caches, or machine runtime paths.
- If you intentionally author a plugin, keep the plugin source and marketplace
  metadata in a normal repo path or dedicated plugin repo, not in live cache
  directories.
- Keep machine-specific values in ignored local files or in live config only.
- Keep skill descriptions concise. Put detailed instructions in `SKILL.md` and
  references.
