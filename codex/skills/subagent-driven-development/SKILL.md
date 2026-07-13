---
name: subagent-driven-development
description: Execute a real implementation plan through independent worker slices with shared-checkout safety and staged review.
---

# Subagent-Driven Development

Use this skill when a real implementation plan exists and its tasks are
independent enough to hand off with local context and concrete checks. Do not use
it for exploration, tightly coupled work, branch triage, ordinary review, or a
one-shot manual change.

## Posture

This is a disciplined implementation pipeline, not permission to maximize
fan-out. Delegate only when a fresh execution owner gains clarity or reduces the
controller's working set. The controller holds the plan above execution. It is
accountable for task boundaries, sequence, review, and integration, but should be
reluctant to prove its value by editing the worker's slice.

The implementer owns the assigned artifact and carries ordinary setup,
debugging, testing, and recovery inside that boundary. Ordinary continuation is
implicit. A worker keeps the slice until it completes or reaches a real
exception; it does not return merely to ask whether it should keep working.
Completion and exception reports are evidence for routing, not self-verifying
runtime state.

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

Require one return record only when the slice is complete or a real exception
prevents further safe useful work. The return kind describes why control is
being returned; it is not a repeated progress status:

- `completed`: the artifact exists, focused checks ran, and self-review is done.
  Proceed to independent spec review; do not accept the claim as proof.
- `needs_input`: an exact fact, decision, permission, or context item blocks all
  remaining safe work. Supply it or route it to the correct owner.
- `waiting_external`: a named process or event remains and no useful parallel
  work is available. Assign a bounded monitor rather than spending model turns
  waiting.
- `failed`: local recovery is exhausted or a safety boundary prevents further
  execution. Diagnose the failed action, evidence, current state, smallest
  reversible move, and next owner.

Keep residual concerns in a separate field. Do not encode concern severity as a
different completion state. A negative search or test result belongs in evidence
and may still support completion, replanning, or a more precise input request.

A progress update, timeout, or quiet child is not an automatic pause or takeover
signal. Collect partial evidence, account for shared-checkout ownership, and
restore a concrete next move. If the host forces a checkpoint, preserve the
objective and evidence and requeue the same owner unless the route changes.

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
