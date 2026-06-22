---
name: subagent-driven-development
description: Execute approved implementation plans with fresh subagents and staged reviews in the same session. Use when a plan exists and tasks are mostly independent.
---

# Subagent-Driven Development

Use this skill when the plan already exists, the tasks are mostly independent,
and keeping the work in the current session is cheaper than spinning up a
separate long-lived thread for each step.

This is a controller skill for implementation fan-out. The controller keeps the
plan, sequencing, review gates, and integration judgment. Implementer subagents
own execution. The controller should make workers effective, not become a
worker.

Keep pressure on worker status claims. `DONE` and `BLOCKED` are not endpoints
until the controller checks the evidence. A blocked worker is usually a worker
that lost the next move, not a task that has become impossible.

## When To Use

Use this skill when all of these are true:

- there is a real implementation plan or item ledger;
- tasks can be executed one at a time without constant shared reasoning;
- each task can be described with local context and concrete checks;
- the controller can stay focused on sequencing, review, and integration.

Use another workflow when:

- the work is still exploratory or the plan is not real yet;
- tasks are tightly coupled and need continuous shared context;
- branch or worktree triage should happen first;
- the user asked only for brainstorming, review, or a one-shot manual change.

## Controller Role

Hold the plan one level above execution:

- restate task boundaries before dispatch;
- give each implementer only the context needed for its slice, including exact
  repo, file, log, and artifact paths when they matter;
- track task state explicitly instead of relying on memory;
- use fresh implementers for unrelated tasks;
- run spec compliance review before code quality review;
- send fixes back through the implementer path until review is clear;
- keep execution with the worker path when a worker needs repair, narrowing,
  rerouting, or a fresh owner;
- keep the parent moving on independent read-only prep or controller work while
  a child is slow, timed out, or waiting on external state;
- publish only when the user asked for it or the repo workflow requires it.

## Prompt Templates

Use the prompt templates in this skill instead of hand-rolling dispatch text:

- [implementer-prompt.md](implementer-prompt.md): implementer task handoff.
- [spec-reviewer-prompt.md](spec-reviewer-prompt.md): spec compliance review.
- [code-quality-reviewer-prompt.md](code-quality-reviewer-prompt.md): code
  quality review after spec compliance passes.

## Task Dispatch Pattern

For each task:

1. Dispatch the implementer with
   [implementer-prompt.md](implementer-prompt.md), plus the full task text,
   absolute repo path, exact files or artifacts to inspect, scope boundaries,
   nearby files, validation target, and known pitfalls.
2. Require questions before coding when requirements or context are unclear.
3. Require one concrete status on return:
   - `DONE`
   - `DONE_WITH_CONCERNS`
   - `NEEDS_CONTEXT`
   - `BLOCKED`
4. If the task touches shared code paths, confirm the implementer ran the
   narrowest useful checks before review.
5. Dispatch spec review before code quality review.

## Worker Signals

- `DONE`: proceed to spec compliance review.
- `DONE_WITH_CONCERNS`: read the concerns first. Resolve correctness or scope
  concerns before review.
- `NEEDS_CONTEXT`: provide the missing context and re-dispatch.
- `BLOCKED`: do not accept the word. Break it open. Ask what failed, what was
  tried, what that proved, what local reversible move remains, and whether a
  fresh worker should take over. Add context or reroute ownership, but keep
  execution with the worker path. Use `orchestration-controller` when oversight
  itself needs to stay stepped back.

Do not solve the task for the worker. Restore agency, then route execution back
to the owner.

## Wait Discipline

- If a child times out or stalls, collect partial findings and ask what failed,
  what was tried, and what the smallest next action is. Decide whether to add
  context, narrow the slice, interrupt, close, or dispatch a fresh worker.
- While a still-active child may touch the shared checkout, keep parent work to
  independent prep, prompt shaping, review planning, or read-only verification.
  Edit shared files only after closing, interrupting, or otherwise accounting
  for that child.
- Do not block the parent on a long-running reviewer when independent prep,
  read-only verification, or unrelated follow-up remains. Hold the reviewed
  diff at its current gate until that reviewer returns.
- Passive waiting is not neutral. If the parent can still move without corrupting
  the shared checkout, move it.
- When the job stops being same-session implementation sequencing and becomes
  mostly routing, monitoring, review fallback, or completion-gate enforcement,
  create a controller-owned status plan with named owners and evidence gates.
  Use `orchestration-controller` when oversight needs to stay stepped back.

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
- Pair with `orchestration-controller` when the parent task is mostly routing,
  monitoring, review fallback, or completion-gate enforcement instead of
  implementation sequencing.

## Output

Report the plan used, task order, subagent status per task, review findings,
checks run, and whether the branch is ready for the next task, ready for PR
work, or needs a named repair action.
