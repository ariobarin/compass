# Portable Config Workflow

Use this workflow to diff, install, snapshot, verify, or update the reviewed
Compass allowlist.

This is maintainer guidance. It is not installed into a Codex home, user-skill
home, or Claude home.

## Reviewed Sources

- Codex global guidance: `codex/AGENTS.md`
- Claude global guidance: `claude/CLAUDE.md`
- Shared agents and skills: `codex/agents/` and `codex/skills/`
- Direct Claude agents: `claude/agents/`
- Codex hooks, keybindings, and config fragment: `codex/`
- Install and retirement boundaries: `manifests/portable-files.toml`
- Ownership and provenance: `manifests/skill-sources.json`

Claude global guidance is separately authored. Runtime-neutral skills and most
agents derive from Codex source during installation.

## Preview First

```powershell
.\scripts\diff-live.ps1
.\scripts\install.ps1
.\scripts\snapshot.ps1
```

Without `-Apply`, install and snapshot report exact planned changes. Inspect the
copy, retirement, and reviewed-config overlay plan before mutation.

## Validate

```powershell
.\scripts\doctor.ps1
.\scripts\verify-live.ps1 -SkipCodexCommand
```

Use `-RequireInSync` when drift should fail the command. Doctor validates source
boundaries, manifests, skills, agents, policies, hooks, Claude derivation, and
required files.

## Apply

```powershell
.\scripts\install.ps1 -Apply
```

The installer:

- copies reviewed Codex and Claude global files;
- installs Compass-owned user skills;
- derives selected Claude skills and agents;
- copies direct Claude agents;
- backs up and removes explicitly retired Compass-owned paths;
- overlays every reviewed Codex config key;
- preserves generated and machine-local live config keys.

## Update

```powershell
.\scripts\update-live.ps1
.\scripts\update-live.ps1 -Ref <tag-or-commit>
```

Branch refs remain fast-forward only. Tags and commit SHAs resolve to an exact
detached commit before installation.

## Snapshot

```powershell
.\scripts\snapshot.ps1 -Apply
```

Snapshot only the current allowlist. Runtime-generated state, secrets, sessions,
caches, local overrides, and plugin caches remain local.

## Path Resolution

Scripts use:

- `-CodexHome`, then `$env:CODEX_HOME`, then `%USERPROFILE%\.codex`;
- `-AgentsHome`, then `$HOME\.agents`;
- `-ClaudeHome`, then `$HOME\.claude`.

## Ownership Changes

A rename, move, or retirement updates in one reviewed change:

- source path;
- install manifest;
- skill-source catalog;
- derivation transform;
- retired live paths;
- policy contracts and required-file checks;
- install round-trip tests;
- nearby documentation and MCP catalog expectations.

Use [addition-intake.md](addition-intake.md) before promoting a new durable
surface and [claude-config.md](claude-config.md) for Claude-specific routing.
