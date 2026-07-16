# Portable Codex Config Workflow

Use this workflow when changing Compass setup that should survive a new machine,
fresh profile, or copied checkout. This is repository-maintainer guidance and is
not installed into Codex, the user skill home, or Claude.

Installed Codex guidance comes from `codex/AGENTS.md`, `codex/agents/`, and
`codex/skills/`. Shared Claude guidance derives from those sources at install
time. Claude-specific direct agents may live under `claude/agents/` and must be
listed explicitly in the portable manifest.

The scripts accept `-CodexHome`, `-AgentsHome`, and `-ClaudeHome`, then fall back
to the corresponding environment or home defaults. See
[claude-config.md](claude-config.md) for Claude-specific source rules.

## Change Flow

1. Edit repository sources first.
2. Run `.\scripts\doctor.ps1`.
3. Run `.\scripts\verify-live.ps1 -SkipCodexCommand` when a quick drift report
   is enough.
4. Run `.\scripts\diff-live.ps1` for a full review against live files.
5. Review the file diff and planned reviewed-config key changes.
6. Run `.\scripts\install.ps1 -Apply` only after the plan is accepted.

## Latest To Live

Use `.\scripts\update-live.ps1` when the live targets should follow the latest
reviewed `origin/main`. It refuses dirty checkouts and non-fast-forward updates,
protects ignored files, runs the doctor, applies the file install and reviewed
config overlay, and verifies sync.

For unattended use, schedule the exact updater command from a trusted checkout.
Do not make automation resolve dirty state or divergent branches.

## Snapshot Flow

1. Run `.\scripts\snapshot.ps1` to preview the allowlist.
2. Run `.\scripts\snapshot.ps1 -Apply` to copy live allowlisted files into the
   repository.
3. Review the Git diff before committing.

## Config Handling

Treat `codex/config.review.toml` as the authoritative contract for the settings
it contains. Normal install and update flows structurally overlay every reviewed
scalar key into the live `config.toml`; they do not replace the live file.
Review mode lists the exact managed key paths that would change. Apply mode backs
up an existing live file before a changed overlay, writes atomically, and skips
both backup and rewrite when the reviewed keys already match.

Keys absent from the reviewed fragment are not managed and remain in the live
file. This includes generated paths, project trust, MCP transport and OAuth,
desktop UI state, plugin caches, auth, browser state, migration state, and other
machine-local values. Verification compares every reviewed key and ignores
unrelated live keys.

The reviewed fragment may reflect a trusted-machine default. Lower-trust work
should still use bounded workflows, read-only helper agents, or narrower runtime
flags. Do not mix old and new permission models without a deliberate migration.
Do not copy `AGENTS.override.md` or local rules approvals into portable setup
merely because they exist in the live home.

## Durable Guidance

When a change affects future behavior across sessions or machines:

1. Read the current source and nearest maintenance guidance.
2. Choose the narrowest owning surface: global skill, custom agent, hook,
   deterministic script, carried pack, workflow, manifest, or local note.
3. Prefer default locations and copy-based sync.
4. Update source, install wiring, policy contracts, and stale documentation in
   the same PR.
5. Run the doctor before calling the change complete.

Live automation state is not a portable workflow. Capture reusable behavior as a
skill, workflow, script, or reviewed config change.

## Skill And Agent Boundaries

Compass installs reusable global skills from `codex/skills/` into
`$HOME/.agents/skills`. Project-specific skills belong in the target repository's
`.agents/skills` folder. Carried packs remain under `carried/` until a target
project explicitly copies or adopts them.

Shared Claude skills are generated from `[claude].derived_skills`. Shared Claude
agents are generated from `[claude].derived_agents`. Direct Claude agents are
copied from `claude/agents/` when listed in `[claude].agents`.

Old Compass-owned copies under `$CODEX_HOME/skills`, explicitly retired user
skills under `$HOME/.agents/skills`, and retired Claude-derived skills are stale
artifacts. Installation may back up and remove those owned copies, but it must
not delete unrelated personal skills.

Before changing install paths again:

1. Confirm the active runtime instruction roots.
2. Check for stale owned duplicates.
3. Update README, manifest comments, validation, and this workflow together.

## New Machines

1. Install Codex and any supported companion runtime normally.
2. Clone Compass.
3. Run `.\scripts\doctor.ps1`.
4. Run `.\scripts\install.ps1` and inspect the file and reviewed-key plan.
5. Run `.\scripts\install.ps1 -Apply`.
6. Run `.\scripts\verify-live.ps1 -SkipCodexCommand -RequireInSync` to confirm
   every reviewed key was overlaid while machine-local config remained present.

## Related Workflows

- [addition-intake.md](addition-intake.md)
- [compass-review-program.md](compass-review-program.md)
- [codex-restart-recovery.md](codex-restart-recovery.md)
- [multi-thread-pr-coordination.md](multi-thread-pr-coordination.md)
- [read-only-research.md](read-only-research.md)
- [agent-failures.md](agent-failures.md)
