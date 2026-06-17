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

When drafting or clarifying a goal, shape it into this contract:

```text
/goal <objective>

Done means:
Scope:
Do not touch:
Evidence required:
If waiting:
If blocked:
Subagents:
```

Keep each field concrete. Prefer named files, repos, PRs, commands, checks,
artifacts, and review signals over broad intent.

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

For subagents, pass a narrowed slice instead of the whole parent goal:

```text
Parent goal:
Slice:
Allowed files or systems:
Forbidden scope:
Inputs to inspect:
Expected output:
Evidence required:
Done condition for this slice:
Return one status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED.
```

Use fresh subagents for independent slices. The controller keeps ownership of
the parent goal, integrates outputs, verifies final evidence, and decides when
the parent can be completed.

## Good Completion Predicates

Good predicates name the finish line and the proof:

- All named PRs are open, green, reviewed, and linked in the final report.
- Each listed repo has a current diff audit, a matching `MODIFICATIONS.md`, and
  verification that unrelated changes were not touched.
- The report exists at the requested path, covers each named comparison axis,
  and has been checked for formatting or repo-specific style constraints.

Avoid predicates like "make progress", "clean it up", or "look into it" unless
the user explicitly wants exploration only.

## Related Skills

- Use `subagent-driven-development` when a goal already has independent
  implementation slices and needs controller-led subagent execution.
- Use `action-items-to-prs` when a goal should become one or more PR-scoped
  changes.
- Use `git-branch-resolver` when a goal depends on branch, worktree, or PR
  inventory before implementation.
