# which-llm Plugin Workflow

Use this workflow when the local Codex install should include the
`which-llm` plugin.

This is repo-maintainer guidance. It documents how to install and refresh the
plugin without making Compass own the plugin source or generated cache state.

## Boundary

- `ariobarin/which-llm` owns the skill package, plugin wrapper, model snapshot,
  and release history.
- Compass owns only the durable install route and review boundary.
- The live Codex home owns marketplace checkouts, generated plugin cache
  entries, installed plugin state, and cached model artifacts.
- Do not copy plugin cache files, generated marketplace paths, snapshots,
  credentials, or local runtime paths into Compass.

## Install

Compass declares the marketplace and plugin in `manifests/plugins.json`.
Preview or apply the declared plugin state with:

```powershell
.\scripts\sync-plugins.ps1
.\scripts\sync-plugins.ps1 -Apply
```

The regular `install.ps1 -Apply` path also installs missing declared plugins.
Generated marketplace and plugin state remains local.

Start a new Codex session after installing so the plugin skill is discovered.

## Update

After `ariobarin/which-llm` merges a change that should be active locally,
refresh the marketplace and installed plugin through the reviewed script:

```powershell
.\scripts\sync-plugins.ps1 -Apply -Refresh
```

The update-live workflow uses this refresh path after updating Compass. It
refreshes the active installed plugin cache without copying cache files by
hand.

## Verify

Confirm the plugin is installed and enabled:

```powershell
codex plugin list
```

Use the installed plugin root reported by `codex plugin list` for any direct
filesystem smoke check. From the plugin's `skills/which-llm` directory, run:

```powershell
python pick.py best --top 3
```

For the atomic script refactor, `pick.py`, `compare.py`, `profile.py`,
`slug.py`, `frontier.py`, and `export.py` should be present in the installed
skill directory.

## Compass Changes

Change Compass only when the durable declaration, install route, local review
boundaries, or tool-surface notes change. Changes to model data, atomic
commands, plugin packaging, or generated artifacts belong in
`ariobarin/which-llm`.
