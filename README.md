# Compass

Compass is reviewed source for portable Codex configuration, with manifest
support for direct Claude Code definitions. The current bundle contains
portable Codex defaults and selects no Claude definitions.

It is an allowlist, not a runtime-home backup. Auth, sessions, logs, caches,
databases, browser state, generated plugins, and machine-only values stay local.

## Portable Sources

`manifests/portable-files.json` selects the current bundle:

- `codex.files` installs files from `codex/` into the Codex home.
- `codex.config` overlays reviewed keys from `codex/config.toml` while keeping
  unlisted live configuration intact.
- `codex.agents` installs selected `codex/agents/<name>.toml` subagents without
  copying repository documentation.
- `agents.skills` installs `codex/skills/<name>/` into `$HOME/.agents/skills`.
- `claude.files`, `claude.skills`, and `claude.agents` install direct Claude
  definitions.

`codex/AGENTS.md` carries reviewed global user preferences. `codex/config.toml`
carries durable global defaults while machine paths, generated plugin state,
project trust, and app-local settings stay in the live file. Skills and agents
are added only when a reviewed change includes both the definition and its
manifest entry.

## Commands

Preview the current bundle:

```powershell
.\scripts\install.ps1
```

Install it:

```powershell
.\scripts\install.ps1 -Apply
```

Verify installed targets:

```powershell
.\scripts\verify-live.ps1 -RequireInSync
```

Run the portable test suite:

```powershell
.\scripts\test-all.ps1
```

Install backs up a selected target before replacing it. It does not remove or
inspect unlisted runtime state. Git contains the configuration history, so
Compass carries no retirement or backwards compatibility database.
