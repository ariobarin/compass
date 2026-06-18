# Controller Playbooks

Load this reference when the controller needs concrete prompts, status repair
patterns, review fallback, or long-running monitor behavior.

## Contents

- Kickoff Playbook
- Status Repair Playbook
- Review Fallback Ladder
- Ownership Boundary
- Monitor Cadence Playbook
- Morning Handoff Template

## Kickoff Playbook

At startup:

1. Restate the parent objective and the real completion evidence.
2. List each worker, owned slice, current branch or PR, and current claim.
3. Tell each child to apply its own goal when active goal state matters.
4. Set the expected evidence format: findings, checks, PR state, logs, or
   artifacts.
5. Set the next check time and the condition that would justify early
   intervention.

Child-goal activation snippet:

```text
First action: if goal tools are available, call create_goal with this
objective: <slice objective>.
Then call get_goal and confirm the active objective before working.
Do not treat this prompt as a slash command.
```

## Status Repair Playbook

Convert worker claims into the next real action:

- `DONE`: verify against the parent objective, not the worker's interpretation.
- `DONE_WITH_CONCERNS`: split concerns into fixes, reviews, reruns, defers, or
  accepted risks.
- `BLOCKED`: demand a repro, patch path, review path, precedent, or owner
  reroute.
- `NEEDS_CONTEXT`: search docs, prior chat, live docs, issues, PRs, and handoff
  notes before asking the user.
- `WAITING_ON_REVIEW`: move to the review fallback ladder.
- `NO RESULTS`: choose the next executable launch, smoke, patch, or deferral.

## Review Fallback Ladder

When one review path is silent or unavailable:

1. Use `@codex` when that is the normal repo path.
2. Use a fresh local `neutral-critic` subagent when available.
3. Run local checks and CI.
4. Spawn or message a focused reviewer with exact files, diff, and acceptance
   criteria.
5. Route findings back to the implementation owner and re-request review after
   fixes.

Do not stop after one silent review path.

## Ownership Boundary

The controller keeps work moving, but does not absorb implementation by
default.

- Route code or doc edits back to the worker that owns the repo or PR.
- Use helper threads for review, precedent search, or log inspection.
- Edit directly only when the user assigned controller-owned docs, routing
  notes, emergency cleanup, or explicitly reassigned implementation ownership.
- If ownership changes, record why it changed and what the controller edited.

## Monitor Cadence Playbook

For long-running work:

- choose a cadence that matches the system half-life, often 5 to 15 minutes for
  active CI, review, or benchmark work;
- sleep between checks only when the current state has a plausible next event;
- on wake-up, ask whether the system can still move right now;
- intervene when a worker drifts, accepts a false blocker, accepts false
  completion, or ignores a viable review or repair path.

Waiting until a named time is not the same as making progress toward the goal.

## Morning Handoff Template

Use this shape when the controller hands work back to a human or a new thread:

```text
Objective:
Current state:
Running now:
Completed with evidence:
Invalid or partial:
Review state:
Exact next owners and actions:
Explicit deferrals and why they are safe:
```
