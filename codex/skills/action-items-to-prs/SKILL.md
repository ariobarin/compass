---
name: action-items-to-prs
description: Turn a report, audit, checklist, issue list, or review into a confirmed action tracker and coherent PR groups.
---

# Action Items To PRs

Turn one source artifact into reviewable repository work without losing what the
source actually asked for. This skill exists because a broad list is easy to
fragment, duplicate, reinterpret, or declare complete from PR motion alone.

The terminal result is a principal-reviewed action tracker plus PR groups whose
scope and evidence map back to that tracker.

## Anchor To The Source

Read repository guidance, the complete action source, and current open PRs that
may already cover the same work. Build a compact proposed tracker before editing.
For each item record:

- source locator or concise quote;
- requested behavior or decision;
- likely ownership surface;
- evidence that would prove it handled;
- status: todo, already handled, skipped by decision, needs repair, needs owner
  decision, or done.

Resolve locally answerable questions from repository evidence. Present a
proposed interpretation for ambiguous items and ask only when a different answer
would materially change scope, ownership, risk, or PR grouping.

The principal authors and approves the tracker. Implementers return evidence for
it rather than maintaining independent copies.

## Form Coherent PR Groups

Choose boundaries around one purpose, reviewer context, risk profile, and
verification surface.

- Reuse an existing compatible PR when it truthfully owns the same intent.
- Create a new PR when the group has a distinct purpose, owner, risk, or review
  surface.
- Keep unrelated groups separate even when they share a source document.
- Mark non-actionable and already-handled items in the tracker instead of creating
  ceremonial PRs.

A PR group should state which tracked items it advances and what evidence will
close them.

## Execute Through Existing Ownership

Implementation follows the repository's branch and PR workflow. Use
`pr-review-loop` when a named PR needs current-head checks, independent review,
behavior proof, or merge-boundary handling. Use `using-goals` when the source is
a durable multi-context objective rather than a finite PR list.

Keep user changes outside the group untouched. Stage explicit paths when the
worktree contains unrelated edits.

## Reconcile Evidence

After each material result:

1. map current evidence to the exact tracked items;
2. update their status;
3. recompute the unresolved set;
4. adjust PR grouping only when new evidence changes ownership or scope.

A created PR is not evidence that its items are complete.

## Output

Report the source artifact, approved tracker, PR groups created or reused, item
status, evidence locators, unresolved decisions, and the next proof-producing
action.
