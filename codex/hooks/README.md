# Portable Codex Hooks

These hooks are global Codex hooks carried by `codex-portable`.

- Dirty worktree closeout: on `Stop`, asks Codex to continue once when the current repo or immediate child repos have dirty files or unpushed commits, so the final answer names the leftover state.
- Public artifact dash guard: on `PreToolUse`, blocks public commit, tag, and PR commands that contain Unicode dash characters, and blocks patches that add those characters.

Codex requires hook trust review after these hooks are installed into a live Codex home. Open `/hooks` and trust the current definitions.
