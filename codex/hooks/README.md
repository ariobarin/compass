# Portable Codex Hooks

These hooks are global Codex hooks carried by `codex-portable`.

- Dirty worktree closeout: on `Stop`, asks Codex to continue once when the current repo or immediate child repos have dirty files or unpushed commits, so the final answer names the leftover state.
- Public artifact dash guard: on `PreToolUse`, blocks public commit, tag, and PR commands that contain Unicode dash characters, and blocks any patch that adds those characters.

The hook commands resolve from the active Codex home. If `CODEX_HOME` is set,
they run from that home instead of assuming the default `~/.codex`.

The launchers fail open if the guard script or Python runner is missing. The
portable repo checks catch that state before the hook is treated as accepted.

Opt-outs:

- `CODEX_PORTABLE_DISABLE_DASH_GUARD=1` disables dash blocking.
- `CODEX_PORTABLE_DISABLE_GIT_CLOSEOUT=1` disables dirty or unpushed git
  closeout.
- `CODEX_PORTABLE_DISABLE_CHILD_REPO_SCAN=1` keeps git closeout limited to the
  current repository.

Codex requires hook trust review after these hooks are installed into a live Codex home. Open `/hooks` and trust the current definitions.
