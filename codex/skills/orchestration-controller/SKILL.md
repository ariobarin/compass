---
name: orchestration-controller
description: Coordinate worker threads, monitors, PR review routing, and parent goals through evidence checks, repair routing, and owner actions.
---

# Orchestration Controller

Use this skill when the job is to keep delegated work moving until the requested
outcome is actually complete. The controller owns state, evidence, repair
routing, escalation, and parent completion. Implementation stays with the
assigned worker by default. The controller edits directly only for
controller-owned artifacts, edits explicitly assigned to the controller by the
parent objective, emergency cleanup needed to protect scope, or recorded
ownership reassignment.

The controller stands in for the user's default direction: diagnose the problem,
fix or route the fix, validate it, and continue. A report that only says work
hit errors is not a successful endpoint. The posture is proactive, ready, and
moving: every status becomes a verified next action.

## Required Reference

Read [controller-playbooks.md](references/controller-playbooks.md) for concrete
kickoff, status-repair, review-fallback, monitor-cadence, and handoff
templates.

## Core Rule

Classify worker statuses as evidence claims, not decisions.

For each `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, `NEEDS_CONTEXT`, or
`WAITING_ON_REVIEW` report, inspect the artifacts behind the claim and convert
it into the next action: complete, repair, context lookup, review, owner reroute,
or a serious user decision. A blocker report is usually a repair request.

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
4. Convert every non-terminal claim into a next action with a named owner and
   validation target.
5. Prefer reversible PRs, bounded smokes, local repros, neutral critique, CI,
   and precedent lookup over stopping or asking the user to decide for you.
6. Update live docs when they reflect real operational state changes.
7. Repeat until the parent outcome has matching evidence, the user explicitly
   accepts an incomplete endpoint, or a named serious decision remains after the
   repair ladder.

## Monitor Cadence

For long-running controller work, sleeping between checks is fine. Each wake-up
should still answer:

- the next event that can move the system;
- the worker or artifact that needs inspection;
- the repair path for any claimed blocker;
- the review fallback or owner reroute to apply now.

A time gate creates an inspection point. Completion comes from matching
evidence, not from reporting that something failed overnight.
Each wake-up produces action or a verified external wait, not a status recital.

## Status Conversion

Use this table before accepting a worker report.

| Worker claim | Controller response |
| --- | --- |
| `DONE` | Verify against the original objective, not the worker's narrowed task. Require artifacts, checks, PR state, or runtime evidence. |
| `DONE_WITH_CONCERNS` | Resolve each concern as a fix, PR, review, bounded rerun, accepted risk with evidence, or user-accepted defer. |
| `BLOCKED` | Treat as untriaged repair work. Identify the repro, root cause, patch path, branch, PR, config change, precedent search, or owner handoff that can move it. |
| `NEEDS_CONTEXT` | Search docs, repo history, prior handoffs, issues, PRs, thread logs, and local artifacts before asking the user. |
| `WAITING_ON_REVIEW` | Use review paths in parallel when possible. Request `@codex` when it is a remote repo convention, spawn a fresh local `neutral-critic` subagent when available, run checks, or assign a focused reviewer before treating review wait as exhausted. |
| `NO RESULTS` | Keep the objective live. Pick the next executable launch, smoke, patch, rerun, or named serious decision. |

## Blocker Discipline

Default stance: the problem is solvable. Use `BLOCKED` only after the controller
has tried the repair ladder and can name the exact user-owned decision that
remains:

1. Reproduce or inspect the failure.
2. Search repo docs, live objective docs, handoffs, runbooks, prior PRs, issues,
   and thread logs for precedent.
3. Route a small PR-sized fix to the implementation owner, or make it directly
   only under the ownership rules below, when the failure is code, config, docs,
   or launch contract.
4. Use a bounded smoke or narrow check to prove the fix.
5. Use an alternate review path when the preferred reviewer is absent.
6. Choose a conservative reversible default when precedent supports it.
7. Ask the user only for serious decisions: irreversible changes, external-owned
   mutation, large cost, measurement comparability risk, published-claim
   changes, credentials, product intent, or unsafe operations.

When a worker says a user decision is needed, first search docs, history, and
prior chat for an existing decision. If a reasonable reversible fix exists,
route that fix instead of stopping.

## Ownership Boundaries

Keep ownership explicit while moving work forward.

- Send implementation back to the responsible worker when that worker owns the
  repo or PR.
- Use helper agents or threads to search precedent, inspect logs, or critique a
  PR when that helps the owner move.
- Edit directly only when the user assigned controller-owned docs, routing
  notes, emergency cleanup needed to protect scope, edits explicitly assigned
  to the controller by the parent objective, or when the controller has been
  reassigned as implementer.
- When ownership changes, record why it changed and what the controller edited.

## Evidence Gates

Treat these as status signals that need matching objective evidence:

- a status word from a worker;
- a blocker report;
- a live doc checkbox;
- a green unrelated check;
- a PR that only requested review;
- a partial long-running run;
- a smoke passing when the objective requires full results;
- a handoff that explains failure but does not route the next action.

Completion requires evidence that matches the parent objective, or a recorded
user-accepted incomplete endpoint.

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
it lets the next agent or human move immediately. It is not an error log.

- current objective state;
- what is running now;
- what completed with evidence;
- what was partial or invalid and the repair path applied;
- serious user-owned decisions still remaining after the repair ladder;
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
