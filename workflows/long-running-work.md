# Long-Running Work

Use this workflow when an objective must survive compaction, interruption,
multiple delegated assignments, or a replacement principal context.

The purpose is continuity. Preserve one coherent intention in principal-authored
control documents, then let temporary contexts and delegates advance it without
becoming alternate authors of the objective.

## The Principal Authors Control

The user-facing principal, or the user directly, authors and reviews:

- the stable goal;
- anchor precedence;
- the current plan;
- the work catalog and ledger shape;
- assignment packets;
- checkpoints;
- amendments and completion judgment.

Delegates own their assigned artifacts and investigations. They return evidence
through the named return channel. The principal verifies that evidence and
updates control state.

A delegate never needs write access to the control documents merely to report
progress.

## Minimal Control Packet

Use only the documents the objective needs. A substantial multi-context task
usually has:

```text
local-docs/control/
  goal.md
  catalog.md
  checkpoint.md
  assignments/
    <assignment>.md
```

Templates for goals, plans, catalogs, assignments, decisions, and checkpoints live
under [templates/](templates/). Keep stable meaning in `goal.md`, current state
in `catalog.md`, and the smallest complete resume packet in `checkpoint.md`.

The local JSON orchestration ledger is an optional mechanical index and recovery
guard. It remains principal-written and points at the Markdown control packet.
It does not replace the goal or checkpoint.

## Review Before Dispatch

A delegation packet should be reviewable before launch. The principal reviews
every assignment. Give the user an opportunity to review material goals, plans,
slice boundaries, and irreversible authority unless the user already granted
that operating authority or explicitly waived review.

A reviewed assignment names:

- the slice outcome;
- parent goal and assertion identifiers;
- authoritative anchors;
- exact scope and allowed actions;
- production mutation authority;
- evidence required;
- return channel;
- return conditions.

The assignment carries enough context to act and no narrative history that does
not change the work.

## Checkpoint Before Context Loss

Write a checkpoint before compaction, restart, or deliberate handoff. Record:

- goal revision and authoritative anchors;
- current observed state;
- accepted evidence and its locators;
- remaining assertions or decisions;
- active delegates, processes, and worktrees;
- unresolved risks;
- the next proof-producing action;
- the first verification a successor must perform.

The successor reopens anchors in precedence order and checks current observable
state before trusting the checkpoint.

## Fresh-Context Resume Test

A fresh agent with no conversation history should be able to:

1. identify the authoritative goal;
2. locate the current repository, worktree, branch, and artifacts;
3. distinguish accepted evidence from claims;
4. identify active delegated work and its return channel;
5. name the remaining gap;
6. take the next correct action without reconstructing private chat history.

Repair the control packet when this test fails.

## Completion And Archive

Completion reconciles current evidence against the complete goal. A finished
assignment, command, review, wait, or phase is progress until every required
assertion is verified.

After completion:

- write a final checkpoint or completion packet;
- preserve durable evidence in `artifacts/` or the project repository;
- archive control documents that retain future value;
- remove stale monitor state and disposable scratch;
- leave the stable goal and amendments auditable.
