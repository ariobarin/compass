# Compass

Reviewed source for a human-owned Codex and Claude Code setup.

Compass preserves capability while reducing the context, duplication, state,
and maintenance overhead required to use agents well. Its central concern is
coherence: one intention should survive long sessions, compaction, delegation,
model changes, and machine changes without turning intelligent work into a rigid
script.

This repository is an allowlist, not a backup of runtime homes. Authentication,
sessions, logs, caches, databases, browser state, generated plugin state,
machine paths, hosted settings, cloud task history, and connector installs stay
outside the reviewed source.

Read [philosophy.md](philosophy.md) for the governing ideas and
[glossary.md](glossary.md) for terms whose distinctions change behavior.

For public use, treat this repository as a worked example. Review
[CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[SUPPORT.md](SUPPORT.md) before copying its files or proposing changes.

## Layout

### Runtime instruction sources

- `codex/AGENTS.md` is the separately authored global instruction source for
  Codex, normally installed as `~/.codex/AGENTS.md`.
- `claude/CLAUDE.md` is the separately authored global instruction source for
  Claude Code, normally installed as `~/.claude/CLAUDE.md`.
- `codex/agents/` contains reusable Codex agent roles. Most derive into Claude
  agent files during installation. Platform-specific Claude agents live under
  `claude/agents/` only when the shared transform cannot express their contract.
- `codex/skills/` contains reviewed reusable skills installed into
  `$HOME/.agents/skills`. Runtime-neutral skills listed in the manifest derive
  into `$HOME/.claude/skills` from the same reviewed source.
- `codex/hooks.json` and `codex/hooks/` contain reviewed Codex hooks. Hooks
  require runtime trust review after installation.
- `codex/keybindings.json` contains portable Codex keyboard bindings.
- `codex/config.review.toml` is the reviewed scalar config fragment overlaid on
  the live Codex config. Live keys absent from the fragment remain untouched.

Global Codex and Claude instruction files remain separate because their runtime,
model, context, and delegation contracts differ. Shared skills and most shared
agent roles derive when the behavior is genuinely runtime-neutral.

### Narrower and maintainer surfaces

- `carried/` contains portable opt-in domain packs that do not belong in every
  session. The benchmark operations pack and WebMCP pack live here.
- `workflows/` contains recurring Compass maintenance procedures. Start with
  [workflows/README.md](workflows/README.md).
- `local-docs/` contains reviewed maintenance reasoning and dated calibration
  that should not enter runtime context.
- `manifests/` contains install boundaries, skill ownership, policy contracts,
  plugins, and mechanical schemas.
- `scripts/` contains deterministic install, diff, validation, status,
  orchestration-ledger, and recovery mechanics.
- `AGENTS.md` is repository-local guidance for maintaining Compass itself.

Project-specific `AGENTS.md`, `CLAUDE.md`, agents, and skills belong in their
project. `AGENTS.override.md` and machine-only rules remain local unless they are
deliberately adopted as reviewed portable policy.

## Long-Running Work

Long-running work uses durable control documents rather than conversation
history as authority. The user-facing principal, or the user directly, authors
the goal, plan, catalog, assignments, and checkpoints. Delegates receive
reviewed assignments and return artifacts plus evidence. A fresh principal
context resumes the same logical role by reopening and verifying those anchors.

See [workflows/long-running-work.md](workflows/long-running-work.md) and
[workflows/orchestration-ledger.md](workflows/orchestration-ledger.md).

## Common Commands

Preview the difference between reviewed source and live install targets:

```powershell
.\scripts\diff-live.ps1
```

Check portability, manifests, policies, skills, agents, hooks, and text rules:

```powershell
.\scripts\doctor.ps1
```

Preview unfinished Codex sessions that restart recovery would resume:

```powershell
.\scripts\codex-restart-recovery.ps1 -DryRun
```

Check live Codex, user-skill, and Claude files against the allowlist:

```powershell
.\scripts\verify-live.ps1
```

Preview an installation:

```powershell
.\scripts\install.ps1
```

Apply the reviewed installation and config overlay:

```powershell
.\scripts\install.ps1 -Apply
```

Fetch the requested reviewed ref, install it, and verify live state:

```powershell
.\scripts\update-live.ps1
```

Refresh reviewed source from the current live allowlist:

```powershell
.\scripts\snapshot.ps1 -Apply
```

Read local orchestration state:

```powershell
.\scripts\compass.ps1 orchestration
```

Without `-Apply`, mutation scripts stay in review mode and report exact planned
changes. Scripts use `-CodexHome`, then `$env:CODEX_HOME`, then
`%USERPROFILE%\.codex`; `-AgentsHome`, then `$HOME\.agents`; and `-ClaudeHome`,
then `$HOME\.claude`.

## Repository Rules

- Keep Compass small, explicit, and auditable.
- Every durable addition removes, merges, narrows, derives, or mechanizes
  recurring cost, or states why its distinct behavior earns that cost.
- Lead guidance with the role and desired state. Use prohibitions for crisp
  boundaries and known failure shapes.
- Shape judgment before procedure. Exact steps protect fragile mechanics,
  irreversible actions, and handoff contracts.
- Preserve one logical principal author across long-running contexts. Delegates
  return evidence instead of inventing parallel control state.
- Keep model-specific observations dated and revisable in maintainer docs.
- Copy ordinary files into normal runtime locations. Avoid symlink-based setup.
- Keep secrets, auth, databases, logs, sessions, browser profiles, caches,
  generated plugin state, and machine paths outside the repository.
- Keep plugin source in a normal repository and install routes in workflows.
- Keep skill descriptions concise. Put action-critical behavior in `SKILL.md`,
  optional detail in references, and deterministic mechanics in scripts.
- Use a pull request as the durable review unit. Readiness never grants merge or
  other public-mutation authority.
