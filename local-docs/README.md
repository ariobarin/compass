# Local Docs

These docs are for maintaining this repository. They are not installed into a
live Codex home, user skill home, or Claude home and are not part of the
portable allowlist.

Use them when changing this repo so updates preserve the current design:
portable config stays small, workflow detail lives in focused files, and checks
catch drift before config is copied into a live machine.

## Files

- [maintenance-learnings.md](maintenance-learnings.md): local principles for
  making useful changes to Compass without bloating the portable setup.
- [compass-surface-inventory.md](compass-surface-inventory.md): current map of
  installed skills, agents, hooks, maintainer surfaces, mechanical checks, and
  first audit packets for the Compass review program.
- [compass-review-state.md](compass-review-state.md): current handoff state for
  choosing the next Compass review-program PR without manufacturing runtime
  edits from completed audit packets.
- [compass-orientation-audit.md](compass-orientation-audit.md): audit packet
  for Compass orientation surfaces before deeper skill and agent reviews.
- [loop-governance-skills-audit.md](loop-governance-skills-audit.md): audit
  packet for the installed skills that govern goals, orchestration, subagents,
  waiting, context cost, and root-cause discipline.
- [skill-retrieval-audit.md](skill-retrieval-audit.md): audit packet for
  installed skill descriptions as retrieval context.
- [agent-retrieval-audit.md](agent-retrieval-audit.md): audit packet for
  installed agent descriptions as delegation context.
- [subagent-pruning-audit.md](subagent-pruning-audit.md): focused comparison
  of `subagent-driven-development` against `orchestration-controller` before
  pruning overlapping controller language.
- [pr-review-surfaces-audit.md](pr-review-surfaces-audit.md): audit packet for
  PR loops, branch resolution, action-item grouping, specialist review, and
  reviewer agents.
- [domain-shaped-skills-audit.md](domain-shaped-skills-audit.md): audit packet
  for benchmark, WebMCP, and workspace stewardship skills.
- [creation-writing-skills-audit.md](creation-writing-skills-audit.md): audit
  packet for planning, PRD, Compass update, and skill-authoring skills.
- [maintainer-workflows-audit.md](maintainer-workflows-audit.md): audit for
  repo-local workflows that guide Compass maintenance without entering runtime
  context.
- [mechanical-truth-audit.md](mechanical-truth-audit.md): audit for manifests,
  scripts, doctor checks, live verification, and reviewed config fragments.
- [hook-surfaces-audit.md](hook-surfaces-audit.md): audit for installed Codex
  hook definitions, guard modules, launchers, and hook doctor checks.
- [carried-capabilities-design.md](carried-capabilities-design.md): design for
  useful Compass capabilities that should travel in the repo but not load into
  every session.
- [../workflows/addition-intake.md](../workflows/addition-intake.md): promotion
  flow for new repo-maintenance workflows, installed skills, agents, hooks,
  repo-side scripts and manifests, and config fragments. Workflows guide repo
  maintenance and are not installed into a live Codex home, user skill home, or
  Claude home.
- [../workflows/compass-review-program.md](../workflows/compass-review-program.md):
  audit method for reviewing installed skills, agents, hooks, and maintainer
  guidance for audience fit, pruning, rerouting, and global-install eligibility.

## Boundary

Local docs may describe practices, tradeoffs, and repo maintenance habits. They
should not contain secrets, machine-specific runtime paths, generated plugin
state, or instructions that must apply to every agent session.
