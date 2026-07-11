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
.\scripts\compass.ps1 doctor
.\scripts\compass.ps1 diff
.\scripts\compass.ps1 install
.\scripts\compass.ps1 install -Apply
.\scripts\compass.ps1 snapshot
.\scripts\compass.ps1 snapshot -Apply
.\scripts\compass.ps1 verify -SkipCodexCommand -RequireInSync
.\scripts\compass.ps1 update
```

`install` and `snapshot` preserve their preview-first behavior. They mutate only
when `-Apply` is present. `status` runs the live verifier in a child PowerShell
process so drift can be reported without terminating the dispatcher. Use
`-RequireInSync` when drift should produce a failing exit code.

`skills` reports each Compass-owned skill, its canonical source, and its Codex
and Claude install targets. Add `-ProjectPath` to scan project-owned `.agents`
and `.claude` skill roots, or pass an array to `-AdditionalSkillRoot` for plugin
or neighboring-repository roots. Same-name canonical sources are reported as
collisions rather than silently assigned precedence.

`skills-audit` measures the model-visible skill routing surface. It reports the
estimated prompt budget, long descriptions, same-name collisions, near duplicate
skills, manifest drift, and optional aggregate usage evidence. It asks Codex for
the exact live inventory when available and otherwise uses the portable manifest.
Use `-NoLive` for deterministic repository-only output and `-Check` when
structural findings or an exceeded budget should fail the command. Run
`scripts/skills-audit.ps1` directly for usage-log, context-window, and threshold
options. Usage scanning is opt-in and never emits raw log content.

All commands accept `-CodexHome`, `-AgentsHome`, and `-ClaudeHome`. The `update`
command also accepts `-Remote` and `-Branch`.

Use `Get-Help .\scripts\compass.ps1 -Detailed` for parameter help. See
[../workflows/portable-config.md](../workflows/portable-config.md) for the
maintenance workflow and install boundary.
