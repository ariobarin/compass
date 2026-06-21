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
5. Mark blocked only when the same blocker repeats across the required goal
   turns and no meaningful progress remains possible.

## Product Grounding

OpenAI's Codex docs describe `/goal` as the slash command that sets a
persistent goal for Codex, and subagents as delegated agents that Codex starts
for specific tasks. This skill treats cross-thread goal activation as an
explicit action in the child context rather than a text transfer from the
parent.

Codex product mechanics can change. Use this contract unless current tooling
shows a different boundary:

- delegated `/goal` text sent to another thread or subagent is plain text until
  the child applies it;
- a child that needs active goal state applies it by calling `create_goal` for
  itself;
- parent completion stays with the controller, even when a child completes its
  slice;
- spawned subagents may create their own goals when goal tools are available,
  but nested subagent spawning is not an assumed capability.

Treat these as operating assumptions to verify, not as permanent platform
guarantees.

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
   evidence. Weak, indirect, stale, or missing evidence means keep working.
7. If goal tools are unavailable in the current context, keep using the same
   goal-shaped contract in plain text and describe it as a contract rather than
   active goal state.

## Subagent Handoffs

Pass a narrowed goal-shaped contract instead of the whole parent goal. In
observed Codex behavior, delegated messages to other threads and spawned
subagents treated `/goal` text as plain text. If the child needs active goal
state, ask that child to apply the goal to itself by calling `create_goal` for
its own slice.

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
