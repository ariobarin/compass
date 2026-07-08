# Compass Surface Inventory

Use this inventory with `workflows/compass-review-program.md`. It is a current
map for deciding what to audit next. It is not runtime guidance.

Source inspected:

- `manifests/portable-files.toml`
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
- Claude direct skills: 13
- Claude derived skills: 2
- Claude agents: 7
- Repo workflows: 10

## Runtime Context

Runtime context is installed into live agent sessions. It must speak to the
agent using it while doing work.

Codex global files:

- `codex/AGENTS.md`
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
  `subagent-driven-development`, `to-prd`, `workspace-steward`,
  `write-a-skill`
- derived skills: `input-token-economy`, `monitor-to-completion`
- agents: `algorithm-critic`, `neutral-critic`, `repo-explorer`,
  `research-critic`, `reuse-critic`, `reviewer`, `verifier`

Audit pressure:

- Runtime skill text must be audited for audience fit before any rewrite.
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
- There is no dedicated carried-but-not-global skill area yet.
- No skill should be moved there until the route is designed and reviewed.

Route design questions:

- What directory should hold carried skills or agents?
- Should carried material keep normal `SKILL.md` shape or use a different
  package format?
- How does a target project opt in?
- How does `doctor.ps1` prevent accidental global installation?
- How does the Claude mirror handle carried material?

Recommended PR:

- Define the carried-but-not-global route before moving any installed skill out
  of global availability.

## First Audit Queues

Queue 1: Compass orientation surfaces.

- `AGENTS.md`
- `README.md`
- `philosophy.md`
- `workflows/compass-review-program.md`
- `local-docs/maintenance-learnings.md`

Purpose: make a fresh maintainer understand Compass fast, with no runtime bloat.

Queue 2: Loop governance skills.

- `compass`
- `using-codex-goals`
- `orchestration-controller`
- `subagent-driven-development`
- `monitor-to-completion`
- `input-token-economy`
- `root-cause-not-symptom`

Purpose: strengthen the agent loops that will run the review program.

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

Queue 4: Domain-shaped skills.

- `benchmark-infra-reviewer`
- `benchmark-run-operator`
- `webmcp-eval-triage`
- `webmcp-tool-authoring`
- `webmcp-verify-tool`
- `workspace-steward`

Purpose: decide what deserves global install, what should be carried, and what
needs pruning for audience fit.

Queue 5: Creation and writing skills.

- `grill-me`
- `to-prd`
- `update-compass`
- `write-a-skill`

Purpose: ensure planning, writing, and Compass update surfaces embody the same
show-don't-tell standard as the rest of the repo.

## Inventory Maintenance

Update this file when:

- installed skill or agent counts change;
- a carried-but-not-global route is added;
- a skill moves between global and carried status;
- an audit queue is completed or reordered;
- a workflow becomes stale or moves.

Do not update this file for every small wording cleanup. It is the map, not the
work log.
