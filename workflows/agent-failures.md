# Agent Failure Journal

Use this file to convert repeated agent mistakes into targeted workflow changes.
Do not add global rules for one-off failures. Record enough detail to identify
the first upstream failure and decide whether the fix belongs in instructions,
a skill, a script, a test, or repo documentation.

This is repo-maintainer guidance and is not installed into a live Codex home,
user skill home, or Claude home. When a failure should change future agent
behavior, route the fix into the reviewed source under `codex/AGENTS.md`,
`codex/agents/`, or `codex/skills/`. The Claude surface derives from those
sources at install time.

## Entry Template

```text
date:
repo or workflow:
task:
first failure:
downstream effects:
evidence:
root cause category:
fix made:
verification:
should become durable guidance:
```

## Categories

- missing context: the agent did not inspect required files, docs, logs, or
  runtime state;
- incorrect context: the agent relied on stale, guessed, or irrelevant facts;
- noisy context: useful evidence was buried under low-value output;
- weak verification: completion was claimed without a check that covered the
  changed behavior;
- unsafe mutation: files, branches, services, or external state changed outside
  the intended scope;
- workflow mismatch: the task needed planning, research, browser validation,
  or PR handling but ran as a simple edit;
- tool-surface risk: a plugin, MCP server, browser, shell, or network tool had
  broader capability than the task required.

## Review Loop

1. Record the first failure, not every downstream symptom.
2. Group similar entries after several traces.
3. Add durable guidance only when the same category repeats.
4. Prefer a script or focused workflow over a broad global rule.
5. Remove stale guidance when the underlying failure no longer appears.

## Recorded Failures

These records preserve the first upstream failure and durable correction. Keep
detailed evidence with the reviewable change that adopted it, not repeated here.

### 2026-07-13: Goal lost its operational map

- Failure: a prep-only benchmark child amended and reconstructed a
  controller-owned Markdown control file without edit authority. Later, the
  long-running goal kept driving output after controller, worker, monitor, and
  repair roles collapsed together and required control files became large,
  contradictory, and partly historical.
- Cause: missing context, incorrect context, noisy context, workflow mismatch.
- Durable response: mutable control surfaces have one named writer and delegated
  roles need exact edit authority; goal contracts name authoritative inputs in
  precedence order, one short mutable-state surface, and a compaction or handoff
  re-anchor; orchestration restores separate controller and execution owners
  before new dispatches; benchmark recovery stops after two failed successors
  until the complete child runtime path receives fresh root-cause review.

### 2026-07-08: Inline review visibility

- Failure: top-level PR comments, reviews, and checks hid actionable inline
  comments.
- Cause: missing context, weak verification.
- Durable response: `compass-review-program` and `pr-review-loop` require
  current-head inline-comment inspection alongside top-level review state.

### 2026-07-02: Specialist review delegation

- Failure: a parent shell-launched CLI children after missing the subagent route,
  then risked reporting that output as coordinated specialist review.
- Cause: workflow mismatch, tool-surface risk.
- Durable response: `specialist-review` and `reviewer` require direct specialist
  subagents; a manual prompt is explicitly outside coordinated review.

### 2026-06-12: Multi-thread public-branch sprawl

- Failure: workers combined local tracking with public PR authority, producing
  overlapping drafts and scratch content.
- Cause: workflow mismatch.
- Durable response: `multi-thread-pr-coordination.md` separates local tracking
  from focused PR branches, with current-head review gates for publication.

### 2026-06-18 and 2026-06-22: Controller recovery posture

- Failure: controllers accepted blocker or waiting claims as endpoints, then
  overcorrected by taking worker-owned execution.
- Cause: workflow mismatch, weak verification.
- Durable response: controller, goal, subagent, and benchmark guidance treat
  those claims as evidence to diagnose, route to a named owner, and keep moving.

### 2026-06-23: Invalid benchmark rows as terminal blockers

- Failure: timeout and provider-failure rows stopped healthy comparable work and
  pulled the controller into the runner role.
- Cause: workflow mismatch, weak verification.
- Durable response: benchmark and goal guidance treat invalid rows as recovery
  work, preserve a named runner owner, and continue unaffected safe slices.
