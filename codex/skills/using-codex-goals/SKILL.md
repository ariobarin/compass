---
name: using-codex-goals
description: Draft and run durable Codex goal contracts. Use when starting, resuming, delegating, or reviewing `/goal` work.
---

# Using Codex Goals

Use this skill when the user starts, refines, delegates, resumes, or reviews a
Codex `/goal`. Treat a goal as a durable completion contract, not a prompt prefix
or a snapshot of the current plan.

## Mental Model

A goal names the finished state and the evidence that will prove it. It does not
name the currently preferred route. The route may change whenever evidence
changes; the finished state changes only through an explicit amendment by the
named authority, normally the user.

Codex goals are active state in one context, not portable markdown. A controller
can send a goal-shaped contract to a child, but the child has active goal state
only after it applies that contract with goal tools in its own context.

Goals persist a thread-bound objective and inject continuation behavior on later
turns. The agent still uses the normal planning and tool loop, but the stopping
rules change:

1. Preserve the user-requested outcome and required final-state assertions unless
   the named authority explicitly amends them.
2. Treat a discovered obstacle, prerequisite, repair, phase, command, review,
   handoff, wait, or next action as mutable execution state, not as a replacement
   for the objective.
3. Keep the goal active while any required assertion remains unverified,
   including while work is under review, waiting on CI, or waiting on external
   state.
4. Mark complete only after current evidence proves every required assertion.
5. Treat blocked as a severe claim, not a resting state. Mark blocked only when
   the same blocking condition has held for at least three consecutive goal
   turns and no meaningful local progress remains possible.

A tidy blocker report, a partial result, a stalled review, or a handoff that
explains failure does not end a goal. Convert it into repair, reroute, review,
recovery, or a named external decision until the completion predicate is truly
satisfied or the same blocker has repeated across at least three goal turns.

An explicit user pause or stop is a control decision, not evidence that the goal
objective was achieved. Stop only owned work, preserve evidence, neutralize
monitors or heartbeats that would restart the work, and write a resume packet.
Do not mark complete unless the user explicitly accepts the paused state as the
endpoint. Do not mark blocked only because execution is paused; blocked still
requires the repeated-blocker standard.

## Contract Layers

For nontrivial or stateful work, keep three logical layers distinct:

- **Outcome contract, stable:** the finished state, required assertions, evidence
  standard, constraints, scope, exclusions, and amendment authority.
- **Acceptance ledger, status-mutable:** stable assertion text plus current
  status and evidence for each assertion.
- **Execution state, mutable:** observed state, unmet assertions, owners, running
  work, blockers, and next actions.

These layers may share one short live document when that is the clearest control
surface. Label them explicitly and name one writer. Simple goals do not need an
extra file; the separation still applies in the active goal and plan.

Use two tests before activating or revising a goal:

- **Outcome stability:** if every currently known obstacle disappeared, would the
  contract still describe what finished work looks like?
- **Evidence closure:** can another agent decide whether every required assertion
  is true from named evidence?

A sequential phrase such as `then`, `after`, or `next` usually describes a route.
It belongs in execution state unless it names an observable resulting state or
artifact. Finishing a route step triggers a fresh comparison with the parent
outcome; it does not make that route the new finish line.

If the original outcome is ambiguous, contradictory, or impossible as written,
request an amendment. Do not infer a new outcome from the latest problem.

## Goal State Boundary

Goal state is local to the context that activates it. Delegated `/goal` text sent
to another thread or subagent is plain text until the child applies it in that
context.

A child that needs active goal state calls `create_goal` for its own slice. The
child receives the parent outcome as read-only context and a slice outcome tied
to named parent assertions. Parent completion authority stays with the
controller. A child completion is evidence for the parent goal, not completion
of the parent goal.

## Activation Rule

When the user invokes this skill for real work and goal tools are available,
default to creating or continuing a goal in the current context. Skip goal
creation when goal tools are unavailable, the user is reviewing this skill,
drafting a reusable template, explicitly says not to create a goal, or is asking
a narrow question that should not persist.

## Goal Brief

When drafting or clarifying a goal, shape it as a concrete contract with a
finished state, required final-state assertions, verification evidence, scope
boundary, waiting rule, blocker rule, and any subagent slices. Prefer named files,
repos, PRs, commands, checks, artifacts, and review signals over broad intent.

For long or stateful work, name authoritative inputs in precedence order and say
how to re-anchor after interruption, compaction, or handoff. Point to one short
live state surface for changing owners, holds, runtime state, assertion status,
and next actions. Keep those details out of the durable outcome text.

Write blocker rules as pressure rules. They should force the agent to say what
failed, what was tried, what evidence changed, what local move remains, and what
external decision, if any, truly cannot be made from the workspace.

For ready-to-copy controller, worker, monitor, live-state, and subagent templates,
read [goal-contracts.md](references/goal-contracts.md).

## Running A Goal

1. Inspect the active goal before creating a duplicate when goal tools are
   available.
2. Identify the stable outcome and required assertions. Restate them before work
   if they are missing or ambiguous.
3. Re-open authoritative inputs and the live state surface, then identify which
   required assertions remain unmet.
4. Choose the next action as a route for closing that gap. Treat planning as setup
   and recorded evidence as progress.
5. Record evidence against the assertion it supports: command output, tests,
   diffs, PR state, rendered artifacts, runtime behavior, or direct source
   inspection.
6. After each material result or worker return, update observed state, assertion
   status, and the plan. Recompute the gap to the parent outcome; do not rewrite
   the outcome to match the work just completed.
7. Before marking complete, audit every required assertion against current
   evidence. Weak, partial, indirect, stale, or missing evidence means keep
   working.
8. If the user pauses or stops a live goal, stop owned execution, disable or
   delete restart automation when available, preserve resume state, and report
   exact live evidence before ending the turn.
9. If goal tools are unavailable in the current context, keep using the same
   goal-shaped contract in plain text and describe it as a contract rather than
   active goal state.

## Subagent Handoffs

Pass each child the parent outcome as read-only context, the parent assertion IDs
its slice advances, a slice postcondition, an integration target, scope, and
required evidence. The child may adapt its local route but may not rewrite the
parent outcome or assertion text. The child must apply active goal state itself;
the controller retains parent completion authority, integrates evidence,
recomputes unmet assertions, and decides the next route. Use fresh subagents for
independent slices.

For copyable slice, activation, and fan-out templates, read
[goal-contracts.md](references/goal-contracts.md).

## Related Skills

- Use `subagent-driven-development` when a goal already has independent
  implementation slices and needs controller-led subagent execution.
- Use `action-items-to-prs` when a goal should become one or more PR-scoped
  changes.
- Use `git-branch-resolver` when a goal depends on branch, worktree, or PR
  inventory before implementation.
