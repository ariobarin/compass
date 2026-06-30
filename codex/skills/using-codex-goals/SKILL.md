---
name: using-codex-goals
description: Draft and run durable Codex goal contracts. Use when starting, resuming, delegating, or reviewing `/goal` work.
---

# Using Codex Goals

Use this skill when the user starts, refines, delegates, resumes, or reviews a
Codex `/goal`. Treat a goal as a durable work contract, not a prompt prefix.

## Mental Model

Codex goals are active state in one context, not portable markdown. A controller
can send a goal-shaped contract to a child, but the child has active goal state
only after it applies that contract with goal tools in its own context.

Goals persist a thread-bound objective and inject continuation behavior on later
turns. The agent still uses the normal planning and tool loop, but the stopping
rules change:

1. Preserve the original objective unless the user explicitly replaces it.
2. Treat later user turns as amendments, constraints, or status checks by
   default.
3. Keep the goal active while work is incomplete, under review, waiting on CI,
   or waiting on external state.
4. Mark complete only after evidence proves the completion predicate.
5. Treat blocked as a severe claim, not a resting state. Mark blocked only when
   the same blocking condition has held for at least three consecutive goal
   turns and no meaningful local progress remains possible.

A tidy blocker report, a partial run, a stalled review, or a handoff that
explains failure does not end a goal. Convert it into repair, reroute, review,
recovery, or a named external decision until the completion predicate is truly
satisfied or the same blocker has repeated across at least three goal turns.

When the user asked for results, a blocker report is not completion. It is an
unfinished signal to investigate. Do not mark complete because the report is
neat, because the failure is well explained, because evidence is partial or
stale, or because one row or worker became invalid. Keep the goal open and drive
the next result-producing move unless the user explicitly accepts an incomplete
endpoint.

## Goal State Boundary

Goal state is local to the context that activates it. Delegated `/goal` text
sent to another thread or subagent is plain text until the child applies it in
that context.

A child that needs active goal state calls `create_goal` for its own slice.
Parent completion authority stays with the controller. A child completion is
evidence for the parent goal, not completion of the parent goal.

## Activation Rule

When the user invokes this skill for real work and goal tools are available,
default to creating or continuing a goal in the current context. Skip goal
creation when goal tools are unavailable, the user is reviewing this skill,
drafting a reusable template, explicitly says not to create a goal, or is asking
a narrow question that should not persist.

## Goal Brief

When drafting or clarifying a goal, shape it as a concrete contract with a
finish line, scope boundary, verification evidence, waiting rule, blocker rule,
and any subagent slices. Prefer named files, repos, PRs, commands, checks,
artifacts, and review signals over broad intent.

Write blocker rules as pressure rules. They should force the agent to say what
failed, what was tried, what evidence changed, what local move remains, and what
external decision, if any, truly cannot be made from the workspace.

For ready-to-copy controller, worker, monitor, and subagent templates, read
[goal-contracts.md](references/goal-contracts.md).

## Running A Goal

1. Inspect the active goal before creating a duplicate when goal tools are
   available.
2. Restate the completion predicate if it is missing or ambiguous.
3. Maintain a concise plan for multi-step work. Treat planning as setup and
   recorded evidence as progress.
4. Record evidence as work completes: command output, tests, diffs, PR state,
   rendered artifacts, runtime behavior, or direct source inspection.
5. On interruption or continuation, resume from the durable objective and the
   latest authoritative state, not only from prior chat memory.
6. Before marking complete, audit every explicit requirement against current
   evidence. Weak, partial, indirect, stale, or missing evidence means keep
   working.
7. If goal tools are unavailable in the current context, keep using the same
   goal-shaped contract in plain text and describe it as a contract rather than
   active goal state.

## Subagent Handoffs

Pass a narrowed goal-shaped contract instead of the whole parent goal. Delegated
messages to other threads and spawned subagents treat `/goal` text as plain
text until the child applies it. If the child needs active goal state, ask that
child to apply the goal to itself by calling `create_goal` for its own slice.

Use fresh subagents for independent slices. The controller keeps ownership of
the parent goal, integrates outputs, verifies final evidence, and decides when
the parent can be completed.

Before dispatching a subagent, write the slice as a mini goal with its own done
condition and evidence requirement. Keep parent completion authority with the
controller. The subagent should return status and evidence; the controller
should decide whether to continue, re-dispatch, review, or complete the parent
goal.

## Related Skills

- Use `subagent-driven-development` when a goal already has independent
  implementation slices and needs controller-led subagent execution.
- Use `action-items-to-prs` when a goal should become one or more PR-scoped
  changes.
- Use `git-branch-resolver` when a goal depends on branch, worktree, or PR
  inventory before implementation.
