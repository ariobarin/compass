---
name: orchestration-controller
description: Coordinate worker threads, benchmark monitoring, PR review routing, and parent goals through evidence checks and owner actions.
---

# Orchestration Controller

Use this skill when the job is to keep delegated work moving. The controller
owns state, evidence, routing, escalation, and parent completion. Implementation
stays with the assigned worker unless the user or current state assigns the
controller a direct edit.

## Required Reference

Read [controller-playbooks.md](references/controller-playbooks.md) for concrete
kickoff, status-repair, review-fallback, monitor-cadence, and handoff
templates.

## Core Rule

Classify worker statuses as evidence claims.

For each `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, `NEEDS_CONTEXT`, or
`WAITING_ON_REVIEW` report, inspect the artifacts behind the claim and map it to
the next true state: complete, needs repair, needs context, needs review,
explicitly deferred, or truly blocked.

## Goal Ownership

When a child needs active goal state, tell it to apply its own goal. Delegated
`/goal` text is not enough by itself.

The controller keeps parent-goal ownership and parent completion authority. Use
the goal templates from `using-codex-goals` when the controller needs a
goal-shaped parent, worker, or monitor contract.

## Controller Loop

1. Restate the parent objective and the actual completion evidence.
2. List each worker or thread, its owned slice, and its current claim.
3. Compare each claim against artifacts, PRs, logs, tests, docs, or runtime
   state.
4. Convert every non-terminal claim into a next action with a named owner.
5. Prefer reversible PRs, bounded smokes, local repros, neutral critique, CI,
   and precedent lookup over stopping.
6. Update live docs when they reflect real operational state changes.
7. Repeat until each slice is complete, explicitly deferred, or truly blocked.

## Monitor Cadence

For long-running controller work, sleeping between checks is fine. Each wake-up
should still answer:

- the next event that can move the system;
- the worker or artifact that needs inspection;
- the repair path for any claimed blocker;
- the review fallback or owner reroute to apply now.

A time gate creates an inspection point. Completion comes from matching
evidence.

## Status Conversion

Use this table before accepting a worker report.

| Worker claim | Controller response |
| --- | --- |
| `DONE` | Verify against the original objective, not the worker's narrowed task. Require artifacts, checks, PR state, or runtime evidence. |
| `DONE_WITH_CONCERNS` | Resolve each concern as a fix, PR, review, bounded rerun, explicit defer, or accepted risk. |
| `BLOCKED` | Assume solvable. Ask what exact repro, patch, branch, PR, review path, config change, precedent search, or owner handoff would move it. |
| `NEEDS_CONTEXT` | Search docs, repo history, prior handoffs, issues, PRs, and thread logs before asking the user. |
| `WAITING_ON_REVIEW` | Use available review paths. Request `@codex` when it is a remote repo convention, and spawn a fresh local `neutral-critic` subagent when available before treating review wait as exhausted. |
| `NO RESULTS` | Keep the run objective live. Route to the next executable launch, smoke, patch, or accepted-deferral decision. |

## Blocker Discipline

Use `BLOCKED` only after the controller has tried the reasonable ladder:

1. Reproduce or inspect the failure.
2. Search repo docs, live objective docs, handoffs, runbooks, prior PRs, issues,
   and thread logs for precedent.
3. Make or route a small PR-sized fix when the failure is code, config, docs, or
   launch contract.
4. Use a bounded smoke or narrow check to prove the fix.
5. Use an alternate review path when the preferred reviewer is absent.
6. Choose a conservative reversible default when precedent supports it.
7. Ask the user only for serious decisions: irreversible changes, external-owned
   mutation, large compute spend, benchmark comparability risk, paper-claim
   changes, credentials, or unsafe operations.

When a worker says a user decision is needed, first search docs, history, and
prior chat for an existing decision.

## Ownership Boundaries

Keep ownership explicit while moving work forward.

- Send implementation back to the responsible worker when that worker owns the
  repo or PR.
- Use helper agents or threads to search precedent, inspect logs, or critique a
  PR when that helps the owner move.
- Edit directly when the user assigned controller-owned docs, routing notes, or
  emergency cleanup, or when the controller has been reassigned as implementer.
- When ownership changes, record why it changed and what the controller edited.

## Evidence Gates

Treat these as status signals that need matching objective evidence:

- a status word from a worker;
- a blocker report;
- a live doc checkbox;
- a green unrelated check;
- a PR that only requested review;
- a partial benchmark run;
- a smoke passing when the objective requires full results;
- a handoff that explains failure but does not route the next action.

Completion requires evidence that matches the parent objective, or explicit user
acceptance of an incomplete endpoint.

## Review Paths

When a PR or patch needs review, move through the available review paths until
one produces actionable findings or an approval signal.

Use the best available combination, with the fresh local critic as a required
step when that agent is available:

- request `@codex` review when that is the repo convention;
- spawn a fresh local `neutral-critic` subagent for an independent review;
- run local checks and CI;
- spawn or message a focused reviewer with exact files, diff, and acceptance
  criteria;
- route actionable findings back through the implementation owner;
- re-request review after concrete fixes.

## Morning Or Long-Running Handoffs

For overnight or time-gated controller work, a good handoff is a control surface:

- current objective state;
- what is running now;
- what completed with evidence;
- what is partial or invalid;
- exact blockers that survived the blocker ladder;
- exact next commands, PRs, owners, and review paths;
- explicit deferrals and why they are safe.

A time gate creates the next inspection point. Sleeping between checks is useful
when each wake-up asks whether the system can move.

## Related Skills

- Use `using-codex-goals` when the parent work should be expressed as a durable
  goal contract or when workers need self-applied slice goals.
- Use `subagent-driven-development` when the controller is sequencing
  implementation tasks with staged review in the same session.
- Use `benchmark-run-operator` when the controlled work is a live benchmark run
  with stack, artifact, and run-validity concerns.
