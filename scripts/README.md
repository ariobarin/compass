# Compass Commands

Use `compass.ps1` as the stable operator-facing entry point. It dispatches to the
focused scripts in this directory; those scripts remain the implementation and
can still be called directly.

```powershell
.\scripts\compass.ps1 status
.\scripts\compass.ps1 status -Json
.\scripts\compass.ps1 skills
.\scripts\compass.ps1 skills -ProjectPath . -Json
.\scripts\compass.ps1 skills -AdditionalSkillRoot @("path-one", "path-two")
.\scripts\compass.ps1 skills-audit
.\scripts\compass.ps1 skills-audit -ProjectPath . -NoLive -Json
.\scripts\compass.ps1 skills-audit -Check
.\scripts\compass.ps1 orchestration
.\scripts\compass.ps1 orchestration -Plain
.\scripts\compass.ps1 orchestration -GoalId release-42 -Json
.\scripts\compass.ps1 doctor
.\scripts\compass.ps1 diff
.\scripts\compass.ps1 install
.\scripts\compass.ps1 install -Apply
.\scripts\compass.ps1 snapshot
.\scripts\compass.ps1 snapshot -Apply
.\scripts\compass.ps1 verify -SkipCodexCommand -RequireInSync
.\scripts\compass.ps1 update
.\scripts\compass.ps1 update -Ref v2026.07.10
.\scripts\compass.ps1 update -Ref <commit-sha>
```

`install` and `snapshot` preserve their preview-first behavior. They mutate only
when `-Apply` is present. `status` runs the live verifier in a child PowerShell
process so drift can be reported without terminating the dispatcher. Use
`-RequireInSync` when drift should produce a failing exit code.

`skills` reports each portable skill, its canonical owner and source, activation
profile, Codex and Claude install targets, optional reviewed upstream provenance,
and same-name collisions. Ownership records live in
`manifests/skill-sources.json`; `doctor` verifies that they match the portable
install manifest and the source tree. Add `-ProjectPath` to scan project-owned
`.agents` and `.claude` skill roots, or pass an array to `-AdditionalSkillRoot`
for plugin or neighboring-repository roots.

`skills-audit` measures the model-visible skill routing surface. It reports the
estimated prompt budget, long descriptions, same-name collisions, near duplicate
skills, manifest drift, and optional aggregate usage evidence. It asks Codex for
the exact live inventory when available and otherwise uses the portable manifest.
Use `-NoLive` for deterministic repository-only output and `-Check` when
structural findings or an exceeded budget should fail the command. Run
`scripts/skills-audit.ps1` directly for usage-log, context-window, and threshold
options. Usage scanning is opt-in and never emits raw log content.

`orchestration` reads the local mechanical control index from
`.local/orchestration-ledger.json` by default. Use `-GoalId` for one goal and
`-Ledger` for an explicit path under `.local/`. Durable meaning remains in the
principal-authored Markdown goal, plan, catalog, assignment, and checkpoint
documents referenced by the ledger.

Mutations go through `scripts/orchestration-ledger.ps1`. The current ledger
schema records anchors, control-document links, planning or implementation
phase, current routing, principal-verified evidence with producer and
observation time, public-mutation gates, decisions, timestamps, and recovery
circuits. Every mutation requires the named principal and expected revision.
Delegated workers return artifacts and evidence; they cannot mutate control
state. Legacy schema versions migrate on load and are rewritten to the current
version on the next successful write.

Use `check-recovery` for read-only observation. Use `begin-recovery` after the
principal reviews an assignment. A failure with no new discriminating evidence
opens the circuit. Resume after a changed hypothesis, input, runtime path, or
root-cause finding is recorded through `reset-recovery`. The ledger stays local,
uses exclusive locking, validates before write, and replaces files atomically.

`update` accepts a branch, tag, commit SHA, or other resolvable Git commit with
`-Ref`; `-Branch` remains an alias for compatibility. Branch refs keep the
fast-forward-only behavior. Tags and commit SHAs are checked out detached so
`HEAD` exactly matches the requested commit before installation. Remote tags are
fetched with pruning so a tag deleted upstream cannot be selected from stale
local state.

All commands accept `-CodexHome`, `-AgentsHome`, and `-ClaudeHome`. The `update`
command also accepts `-Remote` and `-Ref`.

Use `Get-Help .\scripts\compass.ps1 -Detailed` for parameter help. See
[../workflows/portable-config.md](../workflows/portable-config.md) for the
maintenance workflow and install boundary.
