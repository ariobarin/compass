# Compass Surface Inventory

Use this inventory with `workflows/compass-review-program.md`. It is a current
map for deciding what to audit next. It is not runtime guidance.

Source inspected:

- `manifests/portable-files.toml`
- `AGENTS.md`
- `README.md`
- `philosophy.md`
- `codex/hooks.json`
- `codex/hooks/`
- `codex/skills/`
- `codex/agents/`
- `claude/skills/`
- `claude/agents/`
- `workflows/`
- `local-docs/`
- `scripts/`

## Current Counts

- Codex installed skills: 22
- Codex installed agents: 7
- Codex installed hook configs: 1
- Codex hook guard modules: 1
- Hook doctor test files: 2
- Claude direct skills: 12
- Claude derived skills: 4
- Claude agents: 7
- Repo workflows: 10

## Runtime Context

Runtime context is installed into live agent sessions. It must speak to the
agent using it while doing work.

Codex global files:

- `codex/AGENTS.md`
- `codex/hooks.json`
- `codex/hooks/`
- `codex/agents/`
- `codex/skills/`

Codex installed skills:

- `action-items-to-prs`
- `benchmark-infra-reviewer`
- `benchmark-run-operator`
- `compass`
- `git-branch-resolver`
- `grill-me`
- `input-token-economy`
- `monitor-to-completion`
- `orchestration-controller`
- `pr-merge-closeout`
- `pr-review-loop`
- `root-cause-not-symptom`
- `specialist-review`
- `subagent-driven-development`
- `to-prd`
- `update-compass`
- `using-codex-goals`
- `webmcp-eval-triage`
- `webmcp-tool-authoring`
- `webmcp-verify-tool`
- `workspace-steward`
- `write-a-skill`

Codex installed agents:

- `algorithm-critic`
- `neutral-critic`
- `repo-explorer`
- `research-critic`
- `reuse-critic`
- `reviewer`
- `verifier`

Claude runtime mirror:

- direct skills: `action-items-to-prs`, `benchmark-infra-reviewer`,
  `benchmark-run-operator`, `compass`, `git-branch-resolver`, `grill-me`,
  `orchestration-controller`, `pr-review-loop`, `specialist-review`,
  `subagent-driven-development`, `to-prd`, `write-a-skill`
- derived skills: `input-token-economy`, `monitor-to-completion`,
  `root-cause-not-symptom`, `workspace-steward`
- agents: `algorithm-critic`, `neutral-critic`, `repo-explorer`,
  `research-critic`, `reuse-critic`, `reviewer`, `verifier`

Audit pressure:

- Runtime skill text, retrieval descriptions, and agent descriptions must be
  audited for audience fit before any rewrite.
- Any Codex skill cleanup needs a Claude mirror decision in the same PR or a
  stated reason why no Claude change applies.
- Benchmark and WebMCP skills need a global-install eligibility review because
  they are strong, useful, and more domain-shaped than the core Compass loop.
- PR, review, goal, orchestration, and monitor skills are core loop surfaces.
  They should be audited first because they shape how future audit work runs.

## Maintainer Context

Maintainer context helps agents and humans change Compass. It should not be
installed into normal runtime sessions.

Primary maintainer surfaces:

- `AGENTS.md`
- `README.md`
- `philosophy.md`
- `local-docs/maintenance-learnings.md`
- `local-docs/compass-surface-inventory.md`
- `local-docs/compass-review-state.md`
- `workflows/addition-intake.md`
- `workflows/agent-failures.md`
- `workflows/claude-config.md`
- `workflows/codex-restart-recovery.md`
- `workflows/compass-review-program.md`
- `workflows/multi-thread-pr-coordination.md`
- `workflows/plan-template.md`
- `workflows/portable-config.md`
- `workflows/read-only-research.md`
- `workflows/which-llm-plugin.md`

Audit pressure:

- `AGENTS.md`, `README.md`, `philosophy.md`, and
  `workflows/compass-review-program.md` are the fastest path to orient a fresh
  maintainer. They must be sharp before deeper skill rewrites.
- `workflows/agent-failures.md` and `local-docs/maintenance-learnings.md` may
  hold history that should stay out of runtime context. Keep them useful, but
  do not let them become storage for every past thought.
- `local-docs/compass-review-state.md` is handoff state for continuing this
  program. Keep it current when state classes change, but do not turn it into a
  work log.
- Workflows should route action. If they mainly explain background, move that
  background to local docs or cut it.

## Mechanical Truth

Mechanical truth should be checked, not remembered.

Key files:

- `manifests/portable-files.toml`
- `manifests/tool-surfaces.md`
- `codex/config.review.toml`
- `scripts/common.ps1`
- `scripts/doctor.ps1`
- `scripts/install.ps1`
- `scripts/verify-live.ps1`
- `scripts/update-live.ps1`
- `scripts/diff-live.ps1`
- `scripts/snapshot.ps1`
- `scripts/codex-restart-recovery.ps1`
- `scripts/doctor/checks/*.ps1`

Audit pressure:

- Manifest entries define what is global. Any skill-set pruning must update the
  manifest, installer behavior, retired maps, docs, and Claude route together.
- `doctor.ps1` should catch repeated drift after a pattern is proven. Do not
  turn every preference into a check.
- `verify-live.ps1` proves live install state. Use it when a change claims live
  behavior or install parity.

## Carried But Not Global Gap

The review program needs a route for useful material that should travel with
Compass but should not be installed for every session.

Current state:

- The manifest has global install surfaces and repo-only surfaces.
- `carried/` is the dedicated carried-but-not-global source root.
- No skill has been moved there yet.

Design packet: `local-docs/carried-capabilities-design.md`

Resolved route contract:

- `carried/` holds reviewed source that travels with Compass without loading
  into every Codex or Claude session.
- Carried skills may keep normal `SKILL.md` shape. Their location keeps them
  out of global runtime.
- Target projects opt in from their own repos, or the capability becomes a
  plugin when it should be shared without becoming personal global context.
- `doctor.ps1` checks that carried entries are repo-only, present, and not also
  installed globally.
- Claude carried material uses `carried/claude/` only when runtime-specific
  wording is needed.

Status:

- The carried-but-not-global route is now defined in
  `local-docs/carried-capabilities-design.md`, `carried/`,
  `manifests/portable-files.toml`, and `doctor.ps1`.
- No skill has been moved there yet.
- The first carried demotion PR should move one audited capability only, and
  only after current evidence proves it fails the global-install test.

## First Audit Queues

Status: every first audit queue now has an audit packet. Treat those packets as
the active work surface for findings and follow-up PRs. Update this inventory
when the queue map changes, not for routine packet edits.

Cross-cutting packet:

- `local-docs/skill-retrieval-audit.md`: installed skill descriptions as
  retrieval context. Refresh it when a skill description changes or real use
  shows retrieval noise.
- `local-docs/agent-retrieval-audit.md`: installed agent descriptions as
  delegation context. Refresh it when agent metadata changes or real use shows
  delegation noise.

Queue 1: Compass orientation surfaces.

- `AGENTS.md`
- `README.md`
- `philosophy.md`
- `workflows/compass-review-program.md`
- `local-docs/maintenance-learnings.md`

Purpose: make a fresh maintainer understand Compass fast, with no runtime bloat.

Audit packet: `local-docs/compass-orientation-audit.md`

Queue 2: Loop governance skills.

- `compass`
- `using-codex-goals`
- `orchestration-controller`
- `subagent-driven-development`
- `monitor-to-completion`
- `input-token-economy`
- `root-cause-not-symptom`

Purpose: strengthen the agent loops that will run the review program.

Audit packet: `local-docs/loop-governance-skills-audit.md`

Focused pruning packet:
`local-docs/subagent-pruning-audit.md`

Queue 3: PR and review surfaces.

- `pr-review-loop`
- `pr-merge-closeout`
- `specialist-review`
- `action-items-to-prs`
- `git-branch-resolver`
- `algorithm-critic`
- `neutral-critic`
- `repo-explorer`
- `research-critic`
- `reuse-critic`
- `reviewer`
- `verifier`

Purpose: ensure review produces evidence, not ceremony.

Audit packet: `local-docs/pr-review-surfaces-audit.md`

Queue 4: Domain-shaped skills.

- `benchmark-infra-reviewer`
- `benchmark-run-operator`
- `webmcp-eval-triage`
- `webmcp-tool-authoring`
- `webmcp-verify-tool`
- `workspace-steward`

Purpose: decide what deserves global install, what should be carried, and what
needs pruning for audience fit.

Audit packet: `local-docs/domain-shaped-skills-audit.md`

Queue 5: Creation and writing skills.

- `grill-me`
- `to-prd`
- `update-compass`
- `write-a-skill`

Purpose: ensure planning, writing, and Compass update surfaces embody the same
show-don't-tell standard as the rest of the repo.

Audit packet: `local-docs/creation-writing-skills-audit.md`

Queue 6: Maintainer workflows.

- `workflows/addition-intake.md`
- `workflows/agent-failures.md`
- `workflows/claude-config.md`
- `workflows/codex-restart-recovery.md`
- `workflows/compass-review-program.md`
- `workflows/multi-thread-pr-coordination.md`
- `workflows/plan-template.md`
- `workflows/portable-config.md`
- `workflows/read-only-research.md`
- `workflows/which-llm-plugin.md`

Purpose: ensure repo-local workflows route maintainer action without becoming
runtime behavior, stale history storage, or process-shaped bloat.

Audit packet: `local-docs/maintainer-workflows-audit.md`

Queue 7: Mechanical truth.

- `manifests/portable-files.toml`
- `manifests/tool-surfaces.md`
- `codex/config.review.toml`
- `scripts/common.ps1`
- `scripts/doctor.ps1`
- `scripts/install.ps1`
- `scripts/verify-live.ps1`
- `scripts/update-live.ps1`
- `scripts/diff-live.ps1`
- `scripts/snapshot.ps1`
- `scripts/codex-restart-recovery.ps1`
- `scripts/doctor/checks/*.ps1`

Purpose: make sure Compass boundaries are checked by scripts and manifests
instead of remembered by future agents.

Audit packet: `local-docs/mechanical-truth-audit.md`

Queue 8: Hook surfaces.

- `codex/hooks.json`
- `codex/hooks/`
- `scripts/doctor/checks/hooks.ps1`
- `scripts/doctor/hooks/`

Purpose: keep installed hook behavior narrow, mechanical, reviewed, and tested
without turning hook code into broad agent prose.

Audit packet: `local-docs/hook-surfaces-audit.md`

## Inventory Maintenance

Update this file when:

- installed skill or agent counts change;
- a carried-but-not-global route is added;
- a skill moves between global and carried status;
- an audit queue is completed or reordered;
- review-program state classes change;
- a workflow becomes stale or moves.

Do not update this file for every small wording cleanup. It is the map, not the
work log.
