---
name: clarify-to-prs
description: Plan ambiguous issues, review notes, audits, or checklists into evidence-backed PR groups through one-item inspection, confirmation, and a local ledger.
---

# Clarify To PRs

Take the role of an evidence clerk before becoming an implementer. Turn unclear
work into confirmed, reviewable units without making the user sort through
guesses.

## Core Stance

Resolve facts before asking for judgment. If code, docs, issue bodies, PRs,
logs, or artifacts can answer a condition, inspect them and state the answer.

Use "if" only for choices the user must make or facts that are unavailable after
a reasonable inspection pass. Do not leave code-answerable branches unresolved.

Keep each item small enough for the user to confirm or correct quickly. The
satisfying loop is evidence, concrete understanding, yes or correction,
persistent ledger update, next item.

## Intake Loop

1. Anchor the source.
   - Read the issue queue, review notes, audit report, checklist, or
     user-supplied list.
   - Read local repo guidance before interpreting the items.
   - Create a local catalog or checklist when the list is more than a few items
     or the thread may compact.
2. Work one item at a time.
   - Inspect the named code, docs, tests, artifacts, open PRs, and issue
     context.
   - Resolve every condition that inspection can answer.
   - State the current understanding in implementation terms: problem,
     evidence, clean change, non-change, risk, and verification.
   - Ask for confirmation only on decisions or tradeoffs, not on facts you can
     still inspect.
3. Persist the answer.
   - Mark the item confirmed, corrected, already handled, not planned, blocked
     on owner decision, or needs more evidence.
   - Carry forward the corrected language exactly enough that future PR work
     does not need to rediscover it.
4. Continue until the source list is classified.

## Output Shape

Maintain a concise ledger with these fields when useful:

- source item;
- evidence inspected;
- resolved facts;
- confirmed understanding;
- PR action;
- verification needed;
- status.

When reporting in chat, lead with the next item or the changed understanding.
Avoid dumping the whole ledger unless the user asks or the planning phase is
complete.

## PR Grouping

After enough items are confirmed, group work by reviewer context and
verification scope. Do not group only by source order.

Use narrow PRs when items touch different modules, owners, risks, or validation
paths. Combine items when they share the same rationale and can be verified
together.

Use `action-items-to-prs` when confirmed items should become implemented PRs.
Use `using-codex-goals` when the work needs a durable completion predicate,
long-running continuation, or compaction-safe execution contract.

## Failure Modes

Avoid these patterns:

- Restating an issue from its title without reading the relevant files.
- Asking the user to decide an "if" that code inspection can resolve.
- Turning every item into a PR before classifying whether it is already handled
  or not planned.
- Hiding uncertainty inside a polished plan.
- Preserving project-specific labels, private paths, or local history in the
  general rule.
- Treating a current-state ledger like a changelog. If an artifact records
  retained differences, write stable current rationale, not cleanup history.
