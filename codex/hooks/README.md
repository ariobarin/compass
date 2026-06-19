# Portable Codex Hooks

These hooks are global Codex hooks carried by `codex-portable`.

- Dirty worktree closeout: on `Stop`, asks Codex to continue once when the current repo or immediate child repos have dirty files or unpushed commits, so the final answer names the leftover state.
- Public artifact dash guard: on `PreToolUse`, blocks public commit, tag, and PR commands that contain Unicode dash characters, and blocks patches that add those characters.

The hook commands resolve from the active Codex home. If `CODEX_HOME` is set,
they run from that home instead of assuming the default `~/.codex`.

Codex requires hook trust review after these hooks are installed into a live Codex home. Open `/hooks` and trust the current definitions.
