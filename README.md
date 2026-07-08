# Compass

Reviewed source for my human-owned Codex setup.

This repo is intentionally an allowlist, not a backup of the whole Codex home or
user skill home. The live Codex directory contains auth, logs, sessions, caches,
databases, generated plugin state, browser state, and machine-specific runtime
paths. Those are not portable and should not be committed.

Hosted Codex web settings, cloud task history, repository connections, and
workspace connector installs such as Slack or Linear are also out of scope for
this repo. They are service-side state, not portable files.

For the philosophy behind this repo's shape, see [philosophy.md](philosophy.md).

For public use, treat this repository as a worked example of a reviewed portable
Codex setup. Read [CONTRIBUTING.md](CONTRIBUTING.md),
[SECURITY.md](SECURITY.md), and [SUPPORT.md](SUPPORT.md) before copying its
files or proposing changes.

## Layout

- `codex/AGENTS.md`: portable source for the live global `AGENTS.md` in the
  active Codex home, usually `~/.codex/AGENTS.md`. Keep only session-wide
  defaults there. Keep `AGENTS.override.md` local, and keep project
  `AGENTS.md` files in the target repo.
- `AGENTS.md`: repo-local maintenance guidance for this portable config repo.
  Use this for Compass process and review rules.
- `codex/keybindings.json`: portable keyboard bindings.
- `codex/hooks.json` and `codex/hooks/`: reviewed Codex hooks installed into
  the live Codex home. Hooks require `/hooks` trust review after install.
- `codex/agents/`: reusable global custom agents installed into the live Codex
  home. Project-specific custom agents belong in the target repo.
- `codex/skills/`: reviewed source for reusable user skills installed into
  `$HOME/.agents/skills`, excluding system and plugin cache skills.
  Project-specific `.agents/skills` belong in the target repo. Broader sharing
  should usually happen through a plugin.
- `claude/skills/` and `claude/agents/`: Claude Code skills and agents installed
  into `$HOME/.claude`. They all derive from `codex/` at install time (listed in
  `[claude].derived_skills` and `[claude].derived_agents`); there are no
  hand-maintained `claude/` source files in the repo. See
  `workflows/claude-config.md`.
- `codex/config.review.toml`: reviewed config fragments that are useful on a new
  machine. This is not installed automatically.
- `workflows/`: repo-side operating notes for recurring maintenance work. These
  are not installed into a live Codex home or user skill home.
  Use `workflows/addition-intake.md` before promoting new portable artifacts.
  Use `workflows/compass-review-program.md` when auditing installed skills,
  agents, and maintainer guidance for pruning or rerouting.
  Use `workflows/codex-restart-recovery.md` for restart-only recovery of
  unfinished local Codex sessions.
  Use `workflows/which-llm-plugin.md` for the durable `which-llm` plugin
  install and update route.
- `local-docs/`: repo-local maintenance learnings that are not installed into a
  live Codex home or user skill home.
- `carried/`: reviewed optional capability source that travels with Compass but
  is not installed into every Codex or Claude session.
- `manifests/portable-files.toml`: the install allowlist, repo-only list, and
  local-only denylist.
- `manifests/tool-surfaces.md`: repo-side review notes for tools that can touch
  local or external state.
- `scripts/`: repo-side snapshot, diff, install, and health check helpers.

## Common commands

Preview the difference between this repo and the live install targets:

```powershell
.\scripts\diff-live.ps1
```

Check the repo for obvious portability mistakes:

```powershell
.\scripts\doctor.ps1
```

Preview local Codex sessions that would be resumed after a restart:

```powershell
.\scripts\codex-restart-recovery.ps1 -DryRun
```

Check whether live Codex and user skill files match the portable allowlist and
ask Codex to report active instruction sources:

```powershell
.\scripts\verify-live.ps1
```

Install reviewed portable files into the live Codex home and user skill home:

```powershell
.\scripts\install.ps1 -Apply
```

Fetch latest `main`, fast-forward the checkout, install reviewed portable
files, and verify the live allowlist:

```powershell
.\scripts\update-live.ps1
```

Refresh the repo from the current live allowlist:

```powershell
.\scripts\snapshot.ps1 -Apply
```

Without `-Apply`, `snapshot.ps1` and `install.ps1` run in review mode and explain
what they would change.

Scripts use `-CodexHome` for Codex-home files, otherwise `$env:CODEX_HOME`,
otherwise `%USERPROFILE%\.codex`. They use `-AgentsHome` for user skills,
otherwise `$HOME\.agents`. They use `-ClaudeHome` for Claude-home files,
otherwise `$HOME\.claude`.

## Rules

- Keep this repo small and boring.
- Copy ordinary files into normal Codex locations. Avoid symlink-based setup.
- Treat `codex/config.review.toml` as a draft for manual review, not a direct
  replacement for the live generated `config.toml`.
- Keep `AGENTS.override.md` and `rules/` local unless you deliberately decide
  they are reviewed portable policy.
- Do not commit secrets, auth files, SQLite state, logs, session history, caches,
  browser profiles, generated plugin caches, or machine runtime paths.
- If an automation should become portable, capture it as a skill, workflow, or
  reviewed config change, not by tracking live `automations/` state.
- If you intentionally author a plugin, keep the plugin source and marketplace
  metadata in a normal repo path or dedicated plugin repo, not in live cache
  directories.
- Keep plugin install routes in workflows. Keep installed plugin cache and
  generated marketplace state local.
- Keep machine-specific values in ignored local files or in live config only.
- Keep skill descriptions concise. Put detailed instructions in `SKILL.md` and
  references.
- Promote additions through a PR after checking nearby docs, manifests, and
  install maps for stale guidance.
