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

Install through the Codex plugin marketplace wrapper:

```powershell
codex plugin marketplace add ariobarin/which-llm --sparse .agents/plugins --sparse plugins/which-llm
codex plugin add which-llm@which-llm
```

The first sparse path includes the marketplace catalog. The second includes
the plugin payload referenced by that catalog.

Start a new Codex session after installing so the plugin skill is discovered.

## Update

After `ariobarin/which-llm` merges a change that should be active locally,
refresh the marketplace and installed plugin through the Codex plugin CLI:

```powershell
codex plugin marketplace upgrade which-llm
codex plugin remove which-llm@which-llm
codex plugin add which-llm@which-llm
```

The marketplace upgrade refreshes the configured Git marketplace. The remove
and add steps refresh the active installed plugin cache from that marketplace.
Use the CLI sequence instead of copying files into the cache by hand.

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

Change Compass only when the durable route changes: install commands, local
review boundaries, or tool-surface notes. Changes to model data, atomic
commands, plugin packaging, or generated artifacts belong in
`ariobarin/which-llm`.
