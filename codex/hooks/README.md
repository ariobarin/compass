# Portable Codex Hooks

These hooks are global Codex hooks carried by Compass.

Hook commands resolve from the active Codex home. If `CODEX_HOME` is set, they
run from that home instead of assuming the default `~/.codex`.

The launchers fail open if the guard script or Python runner is missing. The
portable repo checks catch that state before hook definitions are treated as
accepted.

Codex requires hook trust review after hooks are installed into a live Codex
home. Open `/hooks` and trust the current definitions.
