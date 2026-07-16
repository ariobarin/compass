# Compass

Reviewed source for my human-owned Codex setup.

Compass preserves useful capability while reducing recurring context, duplication,
state, and maintenance overhead. This repository is an allowlist, not a backup of
a live Codex, user skill, or Claude home. Auth, logs, sessions, caches, databases,
browser state, generated plugin state, and machine-specific runtime paths stay
local.

For the design philosophy, see [philosophy.md](philosophy.md). Public users should
also read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[SUPPORT.md](SUPPORT.md).

## Layout

- `codex/AGENTS.md`: session-wide Codex defaults installed into the active Codex
  home.
- `AGENTS.md`: repository maintenance guidance for Compass itself.
- `codex/keybindings.json`: portable keyboard bindings.
- `codex/hooks.json` and `codex/hooks/`: reviewed Codex hooks.
- `codex/agents/`: reusable global Codex custom agents.
- `codex/skills/`: reviewed source for reusable user skills installed into
  `$HOME/.agents/skills`.
- `claude/agents/`: platform-specific Claude agent sources when a direct Claude
  surface is required. Shared agents still derive from `codex/agents/`.
- Claude skills listed in `[claude].derived_skills` derive from the reviewed
  `codex/skills/` source at install time.
- `carried/`: opt-in project packs retained in the repository but excluded from
  global installation.
- `codex/config.review.toml`: reviewed scalar config contract overlaid into the
  live `config.toml` during install and update. Keys absent from the fragment,
  including generated and machine-local state, are preserved.
- `workflows/`: repository-side operating notes.
- `local-docs/`: repository-only maintenance evidence and lessons.
- `manifests/portable-files.toml`: install allowlist, repository-only paths, and
  local-only denylist.
- `manifests/plugins.json`: reviewed external plugin sources.
- `manifests/tool-surfaces.md`: review notes for stateful tool surfaces.
- `scripts/`: snapshot, diff, install, validation, and health-check helpers.

Project-specific agents and skills belong in the target repository. Broader
distribution should usually use a plugin. A carried pack may be copied into a
target project only when that project opts in.

## Common commands

Preview differences from the live install targets:

```powershell
.\scripts\diff-live.ps1
```

Check repository portability and policy contracts:

```powershell
.\scripts\doctor.ps1
```

Preview local Codex sessions that would resume after a restart:

```powershell
.\scripts\codex-restart-recovery.ps1 -DryRun
```

Verify the live Codex, user skill, and Claude targets:

```powershell
.\scripts\verify-live.ps1
```

Preview or apply the reviewed file install and reviewed Codex config overlay:

```powershell
.\scripts\install.ps1
.\scripts\install.ps1 -Apply
```

Fetch reviewed `origin/main`, install files and config, and verify the live
targets:

```powershell
.\scripts\update-live.ps1
```

Preview or apply a snapshot from the current live allowlist:

```powershell
.\scripts\snapshot.ps1
.\scripts\snapshot.ps1 -Apply
```

Review mode reports exact reviewed config key changes before apply. Scripts use
`-CodexHome`, `-AgentsHome`, and `-ClaudeHome` when supplied, then fall back to
the matching environment or home defaults.

## Rules

- Keep the repository small and predictable.
- Every durable addition should remove, merge, move, derive, or mechanize
  something, or explicitly justify its recurring cost.
- Prefer copy-based installation over symlink-based setup.
- Treat every key in `codex/config.review.toml` as authoritative during install
  while preserving every live key absent from the fragment.
- Keep `AGENTS.override.md`, local approvals, credentials, runtime state, and
  generated caches out of the repository.
- Capture reusable automation as a skill, workflow, script, or reviewed config
  change rather than tracking live automation state.
- Keep skill descriptions concise and detailed guidance in `SKILL.md` or linked
  references.
- Promote changes through a focused PR after checking nearby docs, manifests, and
  install maps for stale guidance.
