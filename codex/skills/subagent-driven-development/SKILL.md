---
name: subagent-driven-development
description: Execute approved implementation plans with fresh subagents and staged reviews in the same session. Use when a plan exists and tasks are mostly independent.
---

# Subagent-Driven Development

Use this skill when the plan already exists, the tasks are mostly independent,
and keeping the work in the current session is cheaper than spinning up a
separate long-lived thread for each step.

## When To Use

Use this skill when all of these are true:

- there is a real implementation plan or item ledger;
- tasks can be executed one at a time without constant shared reasoning;
- each task can be described with local context and concrete checks;
- the controller can stay focused on sequencing, review, and integration.

Do not use this skill when:

- the work is still exploratory or the plan is not real yet;
- tasks are tightly coupled and need continuous shared context;
- branch or worktree triage should happen first;
- the user asked only for brainstorming, review, or a one-shot manual change.

## Controller Responsibilities

1. Read the plan once and restate the task boundaries in your own words.
2. Gather the smallest code, docs, logs, and repo context each subagent needs.
3. Track task state explicitly in the session plan or task list. Do not rely on
   memory alone.
4. Use a fresh implementer subagent per task. Do not reuse implementation
   context across unrelated tasks.
5. Run review in two stages after each implementation handoff:
   - spec compliance first;
   - code quality second.
6. Send fixes back through the implementer path until both reviews are clear.
7. Commit, push, or open PRs only when the user asked for publishing or the
   repo workflow clearly requires it.

## Prompt Templates

Use the bundled prompt templates instead of hand-rolling dispatch text:

- [implementer-prompt.md](implementer-prompt.md): implementer task handoff.
- [spec-reviewer-prompt.md](spec-reviewer-prompt.md): spec compliance review.
- [code-quality-reviewer-prompt.md](code-quality-reviewer-prompt.md): code
  quality review after spec compliance passes.

## Task Dispatch Pattern

For each task:

1. Dispatch the implementer with
   [implementer-prompt.md](implementer-prompt.md), plus the full task text,
   repo path, scope boundaries, nearby files, validation target, and known
   pitfalls.
2. Require questions before coding when requirements or context are unclear.
3. Require one concrete status on return:
   - `DONE`
   - `DONE_WITH_CONCERNS`
   - `NEEDS_CONTEXT`
   - `BLOCKED`
4. If the task touches shared code paths, confirm the implementer ran the
   narrowest useful checks before review.
5. Dispatch spec review before code quality review. Do not reverse the order.

## Status Handling

- `DONE`: proceed to spec compliance review.
- `DONE_WITH_CONCERNS`: read the concerns first. Resolve correctness or scope
  concerns before review.
- `NEEDS_CONTEXT`: provide the missing context and re-dispatch.
- `BLOCKED`: treat this as a repairable state, not a terminal result. Ask the
  worker what failed, what was tried, what the next smallest action is, and
  whether a fresh worker should take over. Add context, pick a stronger model,
  split the task, repair local setup through the worker, reroute ownership, or
  use `orchestration-controller` for broader coordination. Escalate beyond the
  worker only after the repair path has been tried and the remaining dependency
  is concrete.

Do not ignore a blocked signal or solve the task for the worker. Restore agency,
then route execution back to the owner.

## Review Loop

Spec compliance review answers one question: did the implementation match the
requested task, with nothing missing and nothing extra?

Use [spec-reviewer-prompt.md](spec-reviewer-prompt.md) for that review so the
same standard is applied each time.

Code quality review happens only after spec compliance passes. It should focus
on correctness risks, tests, maintainability, file growth, and fit with local
patterns.

Use [code-quality-reviewer-prompt.md](code-quality-reviewer-prompt.md) for the
quality pass so the reviewer sees the requested task, diff context, and review
focus explicitly.

If either review finds issues:

1. send the issue list back through the implementer path;
2. re-run the same review that found the issue;
3. continue until the issue list is clear.

## Model Selection

- Use a fast model for mechanical tasks with clear scope and 1-2 files.
- Use a standard model for multi-file integration and debugging.
- Use the most capable model for design-heavy tasks, broad codebase reasoning,
  or review.

## Red Flags

Never:

- start implementation on the default branch without explicit consent;
- skip either review stage;
- move to the next task while review issues are still open;
- dispatch multiple implementer subagents in parallel against the same checkout;
- make the subagent discover the plan file on its own when you can paste the
  relevant task text;
- let a self-review replace independent review.

## Useful Pairings

- Pair with `using-codex-goals` when the user frames the work as a durable
  `/goal` or when subagent slices need explicit completion evidence.
- Pair with `git-branch-resolver` when branch or worktree setup is part of the
  job.
- Pair with `action-items-to-prs` when the plan comes from a report, audit, or
  issue list that should become PR-scoped work.

## Output

Report the plan used, task order, subagent status per task, review findings,
checks run, and whether the branch is ready for the next task, ready for PR
work, or needs a named repair action.
