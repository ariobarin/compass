# Local Docs

These docs are for maintaining this repository. They are not installed into a
live Codex home or user skill home and are not part of the portable allowlist.

Use them when changing this repo so updates preserve the current design:
portable config stays small, workflow detail lives in focused files, and checks
catch drift before config is copied into a live machine.

## Files

- [maintenance-learnings.md](maintenance-learnings.md): local principles for
  making useful changes to Compass without bloating the portable setup.
- [compass-surface-inventory.md](compass-surface-inventory.md): current map of
  installed skills, agents, maintainer surfaces, mechanical checks, and audit
  queues for the Compass review program.
- [compass-orientation-audit.md](compass-orientation-audit.md): first queue
  audit for Compass orientation surfaces before deeper skill and agent reviews.
- [loop-governance-skills-audit.md](loop-governance-skills-audit.md): second
  queue audit for the installed skills that govern goals, orchestration,
  subagents, waiting, context cost, and root-cause discipline.
- [subagent-pruning-audit.md](subagent-pruning-audit.md): focused comparison
  of `subagent-driven-development` against `orchestration-controller` before
  pruning overlapping controller language.
- [pr-review-surfaces-audit.md](pr-review-surfaces-audit.md): third queue
  audit for PR loops, branch resolution, action-item grouping, specialist
  review, and reviewer agents.
- [domain-shaped-skills-audit.md](domain-shaped-skills-audit.md): fourth queue
  audit for benchmark, WebMCP, and workspace stewardship skills.
- [creation-writing-skills-audit.md](creation-writing-skills-audit.md): fifth
  queue audit for planning, PRD, Compass update, and skill-authoring skills.
- [maintainer-workflows-audit.md](maintainer-workflows-audit.md): audit for
  repo-local workflows that guide Compass maintenance without entering runtime
  context.
- [mechanical-truth-audit.md](mechanical-truth-audit.md): audit for manifests,
  scripts, doctor checks, live verification, and reviewed config fragments.
- [carried-capabilities-design.md](carried-capabilities-design.md): design for
  useful Compass capabilities that should travel in the repo but not load into
  every session.
- [../workflows/addition-intake.md](../workflows/addition-intake.md): promotion
  flow for new repo-maintenance workflows, installed skills and agents,
  repo-side scripts and manifests, and config fragments. Workflows guide repo
  maintenance and are not installed into a live Codex home or user skill home.
- [../workflows/compass-review-program.md](../workflows/compass-review-program.md):
  audit method for reviewing installed skills, agents, and maintainer guidance
  for audience fit, pruning, rerouting, and global-install eligibility.

## Boundary

Local docs may describe practices, tradeoffs, and repo maintenance habits. They
should not contain secrets, machine-specific runtime paths, generated plugin
state, or instructions that must apply to every Codex session.
