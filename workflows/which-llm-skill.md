# which-llm Skill Workflow

Use this workflow to review and refresh the portable `which-llm` skill without
installing its plugin wrapper.

## Boundary

- `ariobarin/which-llm` owns the skill package, model snapshot, and release
  history.
- Compass owns the reviewed skill copy, exact upstream provenance, install map,
  and live drift verification.
- The live user skill home owns runtime-generated refresh data and local cache
  state.
- Compass manages skill code separately from `artifacts/`, exports, and Python
  caches so normal use does not create portable drift.
- Do not install the `which-llm` marketplace or plugin. The normal Compass skill
  installer retires that legacy route and is the only live route.
- This Compass route targets Codex. Upstream also supports Claude, but Compass
  does not derive it because the command modules live at the skill root.

## Review An Update

Import `skills/which-llm` from an exact upstream commit with the system skill
installer into `codex/skills`, then preserve the upstream MIT license in the
skill directory. Review the complete diff, update the exact commit and tree hash
in `manifests/skill-sources.json`, and run the normal Compass validation.

Do not import the plugin wrapper, marketplace metadata, generated plugin cache,
credentials, or machine-local paths.

## Install

Preview or apply the normal portable install:

```powershell
.\scripts\install.ps1
.\scripts\install.ps1 -Apply
```

Apply mode checks or installs `cryptography`, then refreshes a missing or stale
live snapshot. It preserves live data and exports across later Compass updates.
If refresh is unavailable, installation preserves the bundled snapshot and
warns that recommendations must wait for a successful refresh.
Run refresh commands only from the installed skill, not the reviewed source
copy.

The reviewed skill installs to the user skill home declared in
`manifests/portable-files.toml`. Start a fresh Codex session after installation
so the skill is discovered.

## Verify

Run:

```powershell
.\scripts\doctor.ps1
.\scripts\verify-live.ps1 -SkipCodexCommand -RequireInSync
python "$HOME\.agents\skills\which-llm\pick.py" --help
```

Run `python "$HOME\.agents\skills\which-llm\query.py" data status` separately
to check snapshot freshness. Refresh stale data before making recommendations.

`pick.py`, `compare.py`, `profile.py`, `resolve.py`, `slug.py`, `frontier.py`,
and `export.py` should be present in the installed skill directory.

Changes to model data or command behavior belong in `ariobarin/which-llm`.
