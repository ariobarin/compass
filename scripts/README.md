# Compass Commands

Use `compass.ps1` as the stable operator-facing entry point. It dispatches to the
focused scripts in this directory; those scripts remain the implementation and
can still be called directly.

```powershell
.\scripts\compass.ps1 status
.\scripts\compass.ps1 status -Json
.\scripts\compass.ps1 skills
.\scripts\compass.ps1 skills -ProjectPath . -Json
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
and `.claude` skill roots, or repeat `-AdditionalSkillRoot` for plugin or
neighboring-repository roots. Same-name canonical sources are reported as
collisions rather than silently assigned precedence.

All commands accept `-CodexHome`, `-AgentsHome`, and `-ClaudeHome`. The `update`
command also accepts `-Remote` and `-Branch`.

Use `Get-Help .\scripts\compass.ps1 -Detailed` for parameter help. See
[../workflows/portable-config.md](../workflows/portable-config.md) for the
maintenance workflow and install boundary.
