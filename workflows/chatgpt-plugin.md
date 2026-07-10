# Compass Plugin Workflow

Use this workflow when packaging or testing the reviewed Compass skill bundle as a ChatGPT and Codex plugin.

## Boundary

- `codex/.codex-plugin/plugin.json` is the plugin manifest inside the `codex/` plugin package root.
- The manifest points at `./skills/`, which is the existing reviewed `codex/skills/` source of truth.
- `.agents/plugins/marketplace.json` points the Compass marketplace entry at `./codex` for local and branch testing.
- Installed plugin cache, generated marketplace snapshots, auth, sessions, logs, and runtime state stay local.
- The plugin currently packages skills only. Global Codex config, hooks, custom agent TOML files, and machine-specific state are not included.

## Test a branch

Use an isolated Codex home when testing so the marketplace and installed plugin do not change the normal live setup.

```powershell
$env:CODEX_HOME = Join-Path $env:TEMP "compass-plugin-test"
codex plugin marketplace add ariobarin/compass --ref <branch> --json
codex plugin list --available --json
codex plugin add compass@compass --json
codex plugin list --json
```

A successful install should report the `compass@compass` plugin and an installed path under the isolated Codex home. Start a new ChatGPT Work or Codex session before testing bundled skill discovery.

## Remove the test install

```powershell
codex plugin remove compass@compass --json
codex plugin marketplace remove compass --json
Remove-Item -Recurse -Force $env:CODEX_HOME
Remove-Item Env:CODEX_HOME
```

## Release changes

Increment the plugin version when the installable package changes. Run `scripts/doctor.ps1`, repeat the isolated install test, and let GitHub Actions complete before merging.
