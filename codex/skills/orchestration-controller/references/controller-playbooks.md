# Controller Playbooks

Load this reference when the controller needs concrete prompts, status repair
patterns, review fallback, or long-running monitor behavior. The playbooks keep
the controller moving toward the requested result instead of reporting failure
back to the user as if it were completion.

## Contents

- Kickoff Playbook
- Status Repair Playbook
- Worker Unblock Questions
- Review Fallback Ladder
- Ownership Boundary
- Monitor Cadence Playbook
- Thrash Reset Playbook
- Morning Handoff Template

## Kickoff Playbook

At startup:

1. Restate the parent objective and the real completion evidence.
2. List each worker, owned slice, current branch or PR, and current claim.
3. Tell each child to apply its own goal when active goal state matters.
4. Set the expected evidence format: findings, checks, PR state, logs, or
   artifacts.
5. Name the first unblock question for any reported blocker or partial state.
6. Set the next heartbeat and the condition that would justify early
   intervention.

Child-goal activation snippet:

```text
First action: if goal tools are available, call create_goal with this
objective: <slice objective>.
Then call get_goal and confirm the active objective before working.
Treat this text as activation instructions. The child applies goal tools itself.
```

## Status Repair Playbook

Convert worker statuses and controller-observed states into the next real
action:

- Worker `DONE`: verify against the parent objective, not the worker's
  interpretation.
- Worker `DONE_WITH_CONCERNS`: split concerns into fixes, reviews, reruns,
  defers, or accepted risks.
- Worker `BLOCKED`: treat as an agency reset. Ask the worker what failed, what
  proves it is impossible, what was tried, what the next smallest action is,
  and what they would do if the user replied only with "continue".
- Worker `NEEDS_CONTEXT`: search docs, prior chat, live docs, issues, PRs, and
  handoff notes before asking the user.
- Controller `WAITING_ON_REVIEW`: move to the review fallback ladder.
- Controller `NO_RESULTS`: choose the next executable launch, smoke, patch,
  rerun, review, or owner route.

Do not accept "I am blocked" as the final answer. The controller's normal move
is to restore agency with questions, route execution to the owner, validate
evidence, and continue the parent objective.

## Worker Unblock Questions

Use these before solving anything for the worker:

```text
What exactly failed?
What did you try, and what did each attempt prove?
What evidence says this is impossible inside your assigned scope?
What is the next smallest reversible test, patch, rerun, or lookup?
What would you do next if the user replied only with "continue"?
Are you repeating attempts or running out of context, and should a fresh worker
take over?
```

Route the worker's answer back to the worker or to a fresh owner. The controller
does not become the implementer.

## Review Fallback Ladder

Launch independent review paths as soon as they are useful. Always start with a
fresh local `neutral-critic` review. Add GitHub Codex review only when the
repository is public, owned, or otherwise has an accessible reviewer.

1. Use a fresh local `neutral-critic` subagent.
2. Use `@codex` when that is the normal repo path and the reviewer is
   accessible.
3. Run local checks and CI.
4. Spawn or message a focused reviewer with exact files, diff, and acceptance
   criteria.
5. Route findings back to the implementation owner and re-request review after
   fixes.

Continue to the next review path after a silent or unavailable reviewer. Treat
review exhaustion as a claim that needs evidence, not a reason to stall.

## Ownership Boundary

The controller keeps work moving while implementation stays with the assigned
owner by default.

- Route code or doc edits back to the worker that owns the repo or PR.
- Use helper threads for review, precedent search, or log inspection.
- Edit only controller-owned control surfaces: assignments, status notes,
  monitor schedules, review requests, handoff state, and routing comments.
- Never edit worker-owned implementation, config, docs, or task output. If
  those artifacts need changes, route them to a worker or a fresh worker.
- When ownership changes, record why it changed and who now owns the work.

## Monitor Cadence Playbook

For long-running work:

- choose the slowest cadence that still protects the objective, often 30 to 60
  minutes for long runs and 5 to 15 minutes only for active CI, review,
  deployment, data collection, or other short feedback loops;
- sleep between checks when the current state has a plausible next event;
- on wake-up, ask whether the system can still move right now;
- intervene when a worker drifts, accepts a false blocker, accepts false
  completion, or ignores a viable review or repair path.

A named time creates the next inspection point. Progress still comes from
evidence, repair, review, or owner routing.
Each wake-up should produce a worker question, an owner reroute, a verified
external wait, or a next heartbeat.

## Thrash Reset Playbook

Use this when a worker repeats attempts, loses the objective, expands scope, or
reports logs instead of a next repair action:

```text
Pause implementation. Step back and answer:
1. What is the original objective?
2. What is the current evidence?
3. What attempts changed the state?
4. What is the next smallest reversible action?
5. What should a fresh worker take over if your context is saturated?

Then continue with that next action, or return the exact remaining dependency.
```

## Morning Handoff Template

Use this shape only after the controller has asked the unblock questions, routed
every viable owner action, and set the next heartbeat:

```text
Objective:
Current state:
Running now:
Completed with evidence:
Invalid or partial, with repair path:
Review state:
Exact next owners and actions:
User-accepted deferrals and why they are safe:
```
