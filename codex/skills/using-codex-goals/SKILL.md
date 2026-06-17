---
name: using-codex-goals
description: Draft and run durable Codex goals with explicit completion, evidence, continuation, and subagent handoff rules.
---

# Using Codex Goals

Use this skill when the user starts, refines, delegates, resumes, or reviews a
Codex `/goal`. Treat a goal as a durable work contract, not a prompt prefix.

## Mental Model

Codex goals persist a thread-bound objective and inject continuation behavior on
later turns. The agent still uses the normal planning and tool loop, but the
stopping rules change:

1. Preserve the original objective unless the user explicitly replaces it.
2. Treat later user turns as amendments, constraints, or status checks by
   default.
3. Keep the goal active while work is incomplete, under review, waiting on CI,
   or waiting on external state.
4. Mark complete only after evidence proves the completion predicate.
5. Mark blocked only when the same blocker repeats across the required goal
   turns and no meaningful progress remains possible.

## Goal Brief

When drafting or clarifying a goal, shape it as a concrete contract with a
finish line, scope boundary, verification evidence, waiting rule, blocker rule,
and any subagent slices. Prefer named files, repos, PRs, commands, checks,
artifacts, and review signals over broad intent.

For ready-to-copy goal and subagent templates, read
[goal-contracts.md](references/goal-contracts.md).

## Running A Goal

1. Inspect the active goal before creating a duplicate when goal tools are
   available.
2. Restate the completion predicate if it is missing or ambiguous.
3. Maintain a concise plan for multi-step work, but do not treat planning as
   progress by itself.
4. Record evidence as work completes: command output, tests, diffs, PR state,
   rendered artifacts, runtime behavior, or direct source inspection.
5. On interruption or continuation, resume from the durable objective and the
   latest authoritative state, not only from prior chat memory.
6. Before marking complete, audit every explicit requirement against current
   evidence. Weak, indirect, stale, or missing evidence means keep working.

## Subagent Handoffs

Do not assume active Codex goal state can be assigned to another thread or
subagent. Goal tools operate on the current thread, and delegated messages may
deliver `/goal` as text rather than as a slash command. Pass a narrowed
goal-shaped contract instead of the whole parent goal.

Use fresh subagents for independent slices. The controller keeps ownership of
the parent goal, integrates outputs, verifies final evidence, and decides when
the parent can be completed.

Before dispatching a subagent, write the slice as a mini goal with its own done
condition and evidence requirement. Tell the subagent not to mark or claim the
parent goal complete. The subagent should return status and evidence; the
controller should decide whether to continue, re-dispatch, review, or complete
the parent goal.

## Related Skills

- Use `subagent-driven-development` when a goal already has independent
  implementation slices and needs controller-led subagent execution.
- Use `action-items-to-prs` when a goal should become one or more PR-scoped
  changes.
- Use `git-branch-resolver` when a goal depends on branch, worktree, or PR
  inventory before implementation.
