# Agent Failure Journal

Use this file to convert repeated agent mistakes into targeted system changes.
Record the first upstream failure, the evidence that exposes it, and the narrowest
surface that can prevent recurrence.

This is maintainer evidence. Runtime corrections belong in the separately
reviewed Codex or Claude global source, a focused skill or agent, a project
surface, or a mechanical check.

## Entry Template

```text
date:
runtime and model:
repo or workflow:
task:
first failure:
downstream effects:
evidence:
root cause category:
durable response:
verification:
review date:
```

## Categories

- missing context: authoritative files, runtime state, or prior decisions were
  not inspected;
- incorrect context: stale, guessed, or irrelevant material drove the route;
- noisy context: useful evidence was buried under low-value transcript or logs;
- lossy delegation: an assignment or compaction handoff weakened the original
  understanding;
- distributed control authorship: delegates invented or rewrote the goal, plan,
  catalog, ledger, or checkpoint;
- premature implementation: production mutation began before the objective and
  authority were stable;
- accretive repair: repeated guards, wrappers, or rewrites accumulated around a
  cause that remained uncorrected;
- weak verification: completion was claimed without evidence covering the
  required behavior;
- objective drift: the current route replaced the requested finished state;
- unsafe mutation: files, branches, services, or external state changed outside
  granted authority;
- workflow mismatch: the task needed planning, research, experimentation,
  monitoring, review, or orchestration but used the wrong operating shape;
- tool-surface risk: a tool had broader capability than the assignment needed.

## Review Loop

1. Capture the first failure and current evidence.
2. Group repeated instances by cause rather than visible symptom.
3. Select the narrowest durable correction.
4. Prefer mechanics for exact properties and guidance for judgment.
5. Forward-test behavioral corrections with a fresh context.
6. Revisit dated model counterweights when the model profile changes.
7. Remove guidance after evidence shows the failure no longer justifies its
   recurring cost.

## Recorded Failures

### 2026-07-17: Delegates became authors of control state

- Failure: control guidance assigned separate goal, catalog, and worker-ledger
  writers. Each delegation added another interpretation layer and another state
  format.
- Cause: lossy delegation, distributed control authorship, noisy context.
- Durable response: one logical user-facing principal authors the goal, plan,
  catalog, assignments, ledger shape, and checkpoints across contexts. Delegates
  receive reviewed assignments and return artifacts plus evidence. Principal-only
  ledger mutation is mechanically enforced.
- Verification: schema version 4 rejects delegated control grants and records
  evidence provenance while preserving optimistic revision checks.

### 2026-07-17: Negative-only guidance left the route undefined

- Failure: several instructions described forbidden behavior without naming the
  desired replacement, leaving a broad unstable action space.
- Cause: incorrect context, workflow mismatch.
- Durable response: Compass guidance leads with role, desired state, evidence,
  and authority. Crisp prohibitions remain for secrets, worktree scope, public
  mutation, and similarly observable boundaries.
- Verification: philosophy, skill-authoring guidance, runtime globals, and policy
  contracts encode desired-state-first prompting.

### 2026-07-17: Eager implementation outran understanding

- Failure: production edits began while the user was still shaping the plan.
  Early motion made a weak interpretation costly to stop.
- Cause: premature implementation, objective drift.
- Durable response: goals and control state carry a planning or implementation
  phase. Material plans and assignments remain reviewable before dispatch unless
  the user has granted or waived that review boundary.
- Verification: long-running-work guidance, plan templates, global instructions,
  and ledger phase state preserve the implementation gate.

### 2026-07-17: Persistent repair accumulated code around symptoms

- Failure: repeated patches added guards, wrappers, and broad rewrites instead
  of repairing the owning boundary.
- Cause: accretive repair, weak verification.
- Durable response: `root-cause-not-symptom` reopens the causal model when the
  symptom recurs and ends with a subtractive review for duplicate state,
  unnecessary branches, and obsolete compatibility paths.
- Verification: the skill and code-quality review template require causal and
  subtractive evidence.

### 2026-07-13: Goal substituted a route for the requested result

- Failure: a parent goal described a repair sequence instead of the observable
  state the user wanted at the end.
- Cause: objective drift, workflow mismatch, weak verification.
- Durable response: `using-goals` separates stable finished state and assertions
  from mutable route, owner, blocker, and next action. Completion reconciles the
  whole goal after every material return.

### 2026-07-13: Long-running work lost its operational map

- Failure: a child reconstructed a control file from partial context, then role
  boundaries collapsed and the surviving documents became contradictory.
- Cause: lossy delegation, distributed control authorship, noisy context.
- Durable response: principal-authored anchors, a compact current checkpoint,
  evidence provenance, and the fresh-context resume test preserve one intention
  across compaction and replacement contexts.

### 2026-07-08: Inline review findings remained hidden

- Failure: top-level PR comments, reviews, and checks hid actionable inline
  comments.
- Cause: missing context, weak verification.
- Durable response: `pr-review-loop` inspects current-head inline threads beside
  top-level review state.

### 2026-07-02: Specialist review lost independence

- Failure: a parent substituted shell-launched prompts for the dedicated
  specialist route, then risked reporting the output as coordinated review.
- Cause: workflow mismatch, tool-surface risk.
- Durable response: `specialist-review` routes a neutral handoff through the
  dedicated reviewer and reports failure when that capability is unavailable.

### 2026-06-12: Parallel work created public-branch sprawl

- Failure: workers combined local tracking with public PR authority, producing
  overlapping drafts and scratch content.
- Cause: workflow mismatch, unsafe mutation.
- Durable response: `multi-thread-pr-coordination.md` gives one principal public
  branch authority, principal-authored assignments, and a focused PR budget.

### 2026-06-18 and 2026-06-22: Controllers alternated between passivity and takeover

- Failure: controllers accepted blocker or waiting claims as endpoints, then
  overcorrected by absorbing worker-owned execution.
- Cause: workflow mismatch, weak verification.
- Durable response: the controller stays above execution, treats returns as
  evidence, prepares the next reviewed route, and lets coherent workers continue
  without babysitting.

### 2026-06-23: Invalid benchmark rows became terminal blockers

- Failure: timeout and provider-failure rows stopped healthy comparable work and
  pulled the principal into the runner role.
- Cause: workflow mismatch, weak verification.
- Durable response: the carried benchmark pack treats invalid rows as attributable
  recovery work, preserves a named runner, and continues unaffected comparable
  slices while provenance remains clean.
