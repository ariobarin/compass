---
name: subagent-driven-development
description: Execute an approved implementation plan through bounded worker-owned slices, safe checkouts, and independent evidence gates.
---

# Subagent-Driven Development

Use fresh implementers when an approved implementation plan contains slices that
can be owned and verified independently. This skill exists to reduce context and
increase focus without losing integration, scope, or review discipline.

It is an implementation pipeline, not an alternate controller. The user-facing
principal keeps the parent goal, plan, control documents, assignment authorship,
and final completion judgment.

## Delegate Only A Coherent Slice

A slice is ready when it has:

- one observable postcondition;
- the parent assertion IDs it advances;
- an integration target;
- authoritative anchors;
- exact scope and preservation boundaries;
- production and public mutation authority;
- a concrete evidence target;
- limited collision with other active work;
- a named return channel.

The principal prepares and reviews the assignment before launch. Material slice
boundaries remain available for user review unless existing authority or an
explicit waiver covers them.

Keep coupled changes with one owner. A fresh worker is useful when it gains a
cleaner context, not merely because another agent slot exists.

## Preserve Checkout Ownership

One editing owner operates in one checkout at a time. Use a dedicated worktree
for production-bound work when parallel activity or a dirty main checkout would
create collisions.

The principal stays read-only against worker-owned files until the worker
returns or the assignment is explicitly held, cancelled, or reassigned.

When the user or principal explicitly holds, cancels, or revokes the assignment,
the worker stops further mutation, preserves its current artifact and evidence,
and returns `held` or `cancelled` with preservation evidence without completing
extra scope. The principal verifies that the worker is inactive before taking
over or assigning a new editor.

## Worker Ownership

The implementer owns ordinary setup, repository reading, debugging, focused
tests, and local recovery inside the assignment. It continues while safe,
authorized work remains and returns only when:

- the slice postcondition is verified;
- one exact decision or permission blocks all useful work;
- a named external event remains with no useful parallel work;
- recovery is exhausted or a safety boundary stops execution.

The worker returns artifacts and evidence. It does not edit the parent goal,
catalog, ledger, checkpoint, or assignment after dispatch.

Use [implementer-prompt.md](implementer-prompt.md) for the assignment handoff.

## Independent Evidence Gates

After implementation, test two different claims:

1. **Specification:** the accepted artifact matches the assigned slice and adds
   no unauthorized scope.
2. **Quality:** the accepted slice is correct, robust, tested, maintainable,
   integrated, and no larger than its ownership boundary requires.

Use separate reviewers for substantial or risky slices. A narrow low-risk slice
may use one combined independent review when the approved assignment says so.
Implementer self-review supports these gates and does not replace them.

Route findings back to the implementation owner or a fresh explicitly assigned
repair worker. Re-run the failed evidence gate after material changes.

Use [spec-reviewer-prompt.md](spec-reviewer-prompt.md) and
[code-quality-reviewer-prompt.md](code-quality-reviewer-prompt.md).

## Return To The Principal

The pipeline returns:

- slice postcondition;
- artifact and exact changed files;
- checks and results;
- independent review results;
- evidence mapped to parent assertions;
- integration status;
- remaining concerns or repair owner.

The principal reconciles this evidence against the complete parent goal.
Completing the planned slice list is not sufficient while a required parent
assertion remains unverified.
