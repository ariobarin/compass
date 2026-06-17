# Local Docs

These docs are for maintaining this repository. They are not installed into the
live Codex home and are not part of the portable allowlist.

Use them when changing this repo so updates preserve the current design:
portable config stays small, workflow detail lives in focused files, and checks
catch drift before config is copied into a live machine.

## Files

- [maintenance-learnings.md](maintenance-learnings.md): local principles for
  making useful changes to this repo without bloating the portable Codex setup.
- [../workflows/addition-intake.md](../workflows/addition-intake.md): promotion
  flow for new portable workflows, skills, agents, scripts, manifests, and
  config fragments.

## Boundary

Local docs may describe practices, tradeoffs, and repo maintenance habits. They
should not contain secrets, machine-specific runtime paths, generated plugin
state, or instructions that must apply to every Codex session.
