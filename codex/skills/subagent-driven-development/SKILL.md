---
name: subagent-driven-development
description: Execute a real implementation plan through independent worker slices with shared-checkout safety and staged review.
---

# Subagent-Driven Development

Use this skill when a real implementation plan exists and its tasks are
independent enough to hand off with local context and concrete checks.

Do not use it for exploration, tightly coupled work, branch triage, ordinary
review, or a one-shot manual change.

## Posture

This is a disciplined implementation pipeline, not permission to maximize
fan-out. Delegate only when a fresh execution owner gains clarity or reduces the
controller's working set.

The controller holds the plan above execution. It should feel accountable for
task boundaries, sequence, review, and integration, but reluctant to prove its
value by editing the worker's slice. The implementer should feel full ownership
of the assigned artifact and carry ordinary setup, debugging, testing, and
recovery inside that boundary.

Worker status is evidence, not a verdict. A polished `DONE` still needs review.
A detailed `BLOCKED` still needs a routing decision. Restore context, narrow the
slice, or assign a fresh owner without absorbing the implementation.

## Task Shape

A slice is ready for delegation when it has:

- one coherent implementation objective;
- an owner who can work without constant shared reasoning;
- exact context and scope boundaries;
- a concrete validation target;
- limited collision with other active work.

Do not split work merely because several agents are available. Keep coupled
changes with one owner.

## Ownership Boundaries

- The controller owns the plan, task boundaries, sequence, review gates,
  integration, and completion judgment.
- The implementer owns assigned edits, focused tests, narrow validation, and
  ordinary recovery inside the slice. Route repairs back through the implementer
  path instead of editing worker-owned artifacts.
- Use a fresh implementer for an unrelated slice.
- Do not run multiple editing implementers against the same checkout. While a
  child may edit shared files, keep controller work read-only and outside that
  slice. Account for the child before the controller edits shared files.
- Do not start implementation on the default branch without explicit consent.

## Required Handoffs

Use these templates:

- [implementer-prompt.md](implementer-prompt.md)
- [spec-reviewer-prompt.md](spec-reviewer-prompt.md)
- [code-quality-reviewer-prompt.md](code-quality-reviewer-prompt.md)

Give the implementer the full task text, absolute repo path, exact files or
artifacts, scope boundaries, validation target, and known pitfalls.

Require a return status of `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or
`BLOCKED`, plus files changed, checks, concerns, and the exact next action.
`BLOCKED` must name the dependency outside the slice and the recovery already
tried.

## Required Sequence

1. Dispatch the implementer.
2. After implementation, run spec compliance review, then code quality review.
3. Send findings back through the implementer path and repeat the failed review
   until clear.

The two reviews are independent gates, not ceremony. Spec review compares the
artifact with the requested slice. Quality review tests whether the accepted
slice is well built. Do not replace either with implementer self-review or a
controller summary.

## Completion

Complete only when every task has implementation evidence, both reviews are
clear, integration checks pass, and branch readiness or the next repair owner is
named.
