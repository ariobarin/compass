# Local Docs

These files preserve Compass maintenance reasoning. They are not installed into
Codex, user-skill, or Claude runtime homes.

## Files

- [2026-07-17-compass-revision.md](2026-07-17-compass-revision.md): the
  reviewed architecture, routing, skill-set, continuity, isolation, and install
  changes in this revision.
- [maintenance-learnings.md](maintenance-learnings.md): durable lessons for
  changing Compass without bloating runtime context.
- [context-economy.md](context-economy.md): why durable anchors, compact
  handoffs, targeted reads, bounded waits, and fresh workers replace a callable
  token-economy reminder.
- [model-calibration.md](model-calibration.md): dated current Sol, Luna, Terra,
  GLM-5.2, and effort-routing observations.
- [benchmark-run-evidence.md](benchmark-run-evidence.md): evidence behind the
  carried benchmark operations pack and long-running recovery doctrine.
- [../glossary.md](../glossary.md): shared terms whose distinctions change
  behavior.
- [../workflows/long-running-work.md](../workflows/long-running-work.md):
  principal-authored continuity protocol.
- [../workflows/compass-review-program.md](../workflows/compass-review-program.md):
  audit method for installed and maintainer surfaces.

## Boundary

Local docs may contain dates, tradeoffs, model observations, failure history,
and maintainer rationale when those facts change future decisions. Keep secrets,
machine-only runtime state, raw private logs, and action-critical global rules
out of this directory.

When a lesson should change future runtime behavior, compress the current rule
into the narrowest `AGENTS.md`, `CLAUDE.md`, skill, agent, hook, script, or
manifest. Leave the history here.
