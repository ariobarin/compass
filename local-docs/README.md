# Local Docs

These docs are for maintaining this repository. They are not installed into a
live Codex home or user skill home and are not part of the portable allowlist.

Use them when changing this repo so updates preserve the current design:
portable config stays small, workflow detail lives in focused files, and checks
catch drift before config is copied into a live machine.

## Files

- [maintenance-learnings.md](maintenance-learnings.md): local principles for
  making useful changes to Compass without bloating the portable setup.
- [../workflows/addition-intake.md](../workflows/addition-intake.md): promotion
  flow for new repo-maintenance workflows, installed skills and agents,
  repo-side scripts and manifests, and config fragments. Workflows guide repo
  maintenance and are not installed into a live Codex home or user skill home.

## Boundary

Local docs may describe practices, tradeoffs, and repo maintenance habits. They
should not contain secrets, machine-specific runtime paths, generated plugin
state, or instructions that must apply to every Codex session.
