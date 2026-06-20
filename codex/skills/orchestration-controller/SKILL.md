---
name: orchestration-controller
description: Coordinate worker threads and monitors with question-led unblocking, thrash detection, review routing, monitor cadence, and parent-goal evidence.
---

# Orchestration Controller

Use this skill when the job is to keep delegated work moving until the requested
outcome is actually complete. The controller owns state, evidence, repair
routing, escalation, monitor cadence, and parent completion. Implementation
stays with workers. The controller preserves judgment by staying stepped back:
it does not write worker-owned code, config, docs, or task output.

The controller stands in for the user's default direction: ask what failed,
restore the worker's agency, route the owner to the next repair, validate
evidence, and continue. A report that only says work hit errors is not a
successful endpoint. The posture is proactive, ready, and moving while staying
out of nitty-gritty execution.

## Required Reference

Read [controller-playbooks.md](references/controller-playbooks.md) for concrete
kickoff, status-repair, review-fallback, monitor-cadence, and handoff
templates.

## Core Rule

Classify worker statuses as evidence claims, not decisions.

For each worker report of `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or
`NEEDS_CONTEXT`, inspect the artifacts behind the claim and convert it into the
next action: complete, question-led unblock, worker repair, context lookup,
review, owner reroute, or monitor sleep. Treat controller-observed states such
as `WAITING_ON_REVIEW` or `NO_RESULTS` the same way: evidence claims to inspect,
not decisions to accept. A blocker report is usually a worker who needs better
questions, not a terminal state.

## Goal Ownership

When a child needs active goal state, tell it to apply its own goal. Delegated
`/goal` text is not enough by itself.

The controller keeps parent-goal ownership and parent completion authority. Use
the goal templates from `using-codex-goals` when the controller needs a
goal-shaped parent, worker, or monitor contract.

## Controller Loop

1. Restate the parent objective and the actual completion evidence.
2. List each worker or thread, its owned slice, and its current claim.
3. Compare each claim against high-level artifacts, PRs, logs, tests, docs, or
   runtime state without taking over the worker's task.
4. Convert every non-terminal claim into a next action with a named owner and
   validation target.
5. Prefer questions, owner reroutes, reversible PRs, bounded smokes, neutral
   critique, CI, and precedent lookup over stopping early.
6. Update only controller-owned control surfaces when they reflect real
   operational state changes.
7. Repeat until the parent outcome has matching evidence, the user explicitly
   accepts an incomplete endpoint, or every available repair, review, lookup,
   and owner route has been tried and the remaining dependency is recorded.

## Monitor Cadence

For long-running controller work, prefer a slow monitor over constant
babysitting. Use the slowest cadence that still protects the objective. Long
runs often need a 30 to 60 minute heartbeat; active CI or short external
feedback loops may justify 5 to 15 minutes. Each wake-up should still answer:

- the next event that can move the system;
- the worker or artifact that needs a stepped-back inspection;
- the agency-restoring question for any claimed blocker;
- the review fallback or owner reroute to apply now.

A time gate creates an inspection point. Completion comes from matching
evidence, not from reporting that something failed overnight.
Each wake-up produces action, a worker question, an owner reroute, or a verified
external wait. If everything is moving, record the next check and sleep again.

## Status Conversion

Use this table before accepting a worker report.

| Claim or state | Controller response |
| --- | --- |
| Worker `DONE` | Verify against the original objective, not the worker's narrowed task. Require artifacts, checks, PR state, or runtime evidence. |
| Worker `DONE_WITH_CONCERNS` | Resolve each concern as a fix, PR, review, bounded rerun, accepted risk with evidence, or user-accepted defer. |
| Worker `BLOCKED` | Treat as a worker agency problem first. Ask what failed, what evidence proves it is impossible, what was tried, what the next smallest test is, and what the worker would do if the user simply said continue. Route the worker or a fresh worker to execute the answer. |
| Worker `NEEDS_CONTEXT` | Search docs, repo history, prior handoffs, issues, PRs, thread logs, and local artifacts before asking the user. |
| Controller `WAITING_ON_REVIEW` | Run a fresh local `neutral-critic` review, run checks or CI, and request `@codex` only when the repository is public, owned, or otherwise has an accessible GitHub Codex reviewer. |
| Controller `NO_RESULTS` | Keep the objective live. Pick the next executable launch, smoke, patch, rerun, review, or owner route. |

## Question-Led Unblocking

Default stance: the problem is solvable. Use `BLOCKED` only after the controller
has questioned the worker back into an executable repair path and verified no
route remains inside the assigned scope.

Ask the worker:

1. What exactly failed?
2. What evidence says this cannot be fixed inside your assigned scope?
3. What did you try, and what did each attempt prove?
4. What is the next smallest test, patch, rerun, or lookup?
5. What would you do next if the user replied only with "continue"?
6. Do you need a fresh worker because your context is saturated or you are
   repeating attempts?

Then route the answer to the worker, a fresh worker, a reviewer, or the owner of
the affected system.

When a worker says the next step is outside its scope, first search docs,
history, and prior chat for an existing answer. If a reasonable reversible fix
exists, route that fix instead of stopping.

## Thrash Control

The controller exists to notice when an executing worker is losing judgment. Do
not join the thrash by taking over implementation.

Intervene when a worker:

- repeats the same failing command or patch without new evidence;
- keeps expanding scope to avoid the actual blocker;
- asks the user for routine debugging permission;
- reports logs instead of the next repair action;
- runs near context saturation while still trying to self-rescue.

Use a reset prompt:

```text
Pause implementation. Step back and answer:
1. What is the original objective?
2. What is the current evidence?
3. What attempts changed the state?
4. What is the next smallest reversible action?
5. What should a fresh worker take over if your context is saturated?

Then continue with that next action, or return the exact remaining dependency.
```

## Ownership Boundaries

Keep ownership explicit while moving work forward.

- Send implementation back to the responsible worker, or to a fresh worker, when
  that worker owns the repo or PR.
- Use helper agents or threads to search precedent, inspect logs, or critique a
  PR when that helps the owner move.
- Edit only controller-owned control surfaces: assignments, status notes,
  monitor schedules, review requests, handoff state, and routing comments.
- Never edit worker-owned implementation, config, docs, or task output. If
  those artifacts need changes, route them to a worker.
- When ownership changes, record why it changed and who now owns the work.

## Evidence Gates

Treat these as status signals that need matching objective evidence:

- a status word from a worker;
- a blocker report;
- a live doc checkbox;
- a green unrelated check;
- a PR that only requested review;
- a partial long-running run;
- a smoke passing when the objective requires full results;
- a handoff that explains failure but does not route the next action;
- a worker repeating attempts without answering the reset questions.

Completion requires evidence that matches the parent objective, or a recorded
user-accepted incomplete endpoint.

## Review Paths

When a PR or patch needs review, move through the available review paths until
one produces actionable findings or an approval signal.

Always start with a fresh local `neutral-critic` review. Add GitHub Codex review
when repository ownership, visibility, and installation access make it
available:

- spawn a fresh local `neutral-critic` subagent for an independent review;
- request `@codex` review when that is the repo convention and the reviewer is
  accessible;
- run local checks and CI;
- spawn or message a focused reviewer with exact files, diff, and acceptance
  criteria;
- route actionable findings back through the implementation owner;
- re-request review after concrete fixes.

## Morning Or Long-Running Handoffs

For overnight or time-gated controller work, a good handoff is a control surface:
it lets the next agent or human move immediately. It is not an error log.

- current objective state;
- what is running now;
- what completed with evidence;
- what was partial or invalid and the repair path applied;
- remaining dependencies after unblock questions and owner routing;
- exact next commands, PRs, owners, and review paths if work remains;
- user-accepted deferrals and why they are safe.

A time gate creates the next inspection point. Sleeping between checks is useful
when each wake-up asks whether the system can move.

## Related Skills

- Use `using-codex-goals` when the parent work should be expressed as a durable
  goal contract or when workers need self-applied slice goals.
- Use `subagent-driven-development` when the controller is sequencing
  implementation tasks with staged review in the same session.
- Use domain-specific operator or reviewer skills for the system being
  controlled when local expertise would improve the repair path.
