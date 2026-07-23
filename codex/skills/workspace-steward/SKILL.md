---
name: workspace-steward
description: Organize and audit agentic multi-repo workspaces, worktrees, control docs, experiments, evidence, scratch, and archives.
---

# Workspace Steward

Create a workspace that makes parallel agent work easy to enter, isolate,
resume, review, and retire. This skill exists because repositories, worktrees,
control documents, experiments, artifacts, and scratch acquire different
lifecycles, and a flat directory turns those differences into hidden risk.

The requested organization must earn its maintenance. Preserve active work and
make the smallest layout change that removes real confusion, repeated cost, or
safety risk.

## Apply The Reduction Filter

Before moving files or adding process:

1. Name the current confusion, repeated cost, or preservation risk.
2. Remove proposed buckets, docs, scripts, or automation that do not solve it.
3. Simplify names and paths around existing Git and shell behavior.
4. Accelerate a proven workflow only after its shape is clear.
5. Automate stable repeated operations with explicit inputs, outputs, rollback,
   and preservation boundaries.

A smaller note, ignore rule, catalog, or worktree convention may solve the
problem better than a new hierarchy.

## Separate Lifecycles

An umbrella workspace coordinates child repositories and local operating state.
It is not automatically a monorepo.

Use visible, purpose-named areas when they match the work:

- canonical repositories and clean default-branch checkouts at the root;
- `worktrees/prs/` for branch work intended to become reviewed repository
  changes;
- `worktrees/spikes/` for disposable integration questions against the real
  repository;
- `experiments/` for tiny disposable mechanism tests;
- `local-docs/` for principal-authored goals, plans, catalogs, assignments,
  checkpoints, and handoffs;
- `docs/` for durable project or workspace documentation;
- `artifacts/` for generated evidence, reports, exports, logs, and manifests;
- `tmp/` for recreatable scratch;
- `archived/` for inactive material retained as reference.

Use names that reveal repository and workstream identity. Generic buckets such
as `src/` weaken an umbrella workspace unless the root is truly one repository.

## Worktrees Are Real Work

Keep a clean default-branch checkout for reading, syncing, and creating
worktrees. Start production-bound work from the intended current remote base,
usually `origin/main`, after fetching and verifying state.

Use `git-branch-resolver` whenever branch identity, divergence, registration,
cleanup, or PR state needs interpretation.

Move registered worktrees with Git. Remove them after merge, preservation, or
explicit disposable evidence. A dirty worktree remains active work until its
contents are understood and preserved.

For a preservation audit across many nested repositories and worktrees, read
[large-workspace-git-audit.md](references/large-workspace-git-audit.md).

## Experiments Are Disposable Learning

A micro-experiment answers one uncertainty with tiny code that will never be
copied into production. Keep it independent of the project when the mechanism
can be isolated. Record the finding, then implement deliberately in a real
worktree.

Use `run-a-micro-experiment` for that contract. Use a disposable integration
spike worktree when the uncertainty requires the real repository.

## Preserve Principal Control State

Long-running goals, plans, catalogs, assignments, and checkpoints are authored
by the user-facing principal or the user. Delegated workers return evidence and
artifacts through named channels rather than maintaining independent control
files.

Keep current state compact. Timestamp operational documents with the fields that
answer freshness questions, such as:

- created at;
- updated at;
- last verified at;
- next check at;
- applies to commit or runtime identity;
- archived at.

Use absolute ISO 8601 timestamps with time zones. Source code and ordinary code
comments do not need historical timestamps.

## Promote Useful State

Scratch must not become a hidden source of truth. Promote useful material to the
surface that owns its lifecycle:

- reproducible evidence to `artifacts/`;
- reusable tooling to a reviewed script or repository;
- durable project guidance to `docs/`;
- principal control state to `local-docs/`;
- production-bound edits to a branch and PR.

Generated evidence should record source, owner, observed time, secret-scan state,
and regeneration instructions when those facts are not obvious.

## Copyable Workspace

For a new umbrella workspace, use `references/project-template/` only when the
reduction filter leaves the full structure as the smallest useful shape. Read
its root README, glossary, runtime guidance, and lifecycle READMEs before
copying it.

## Audit Result

A workspace audit should make these answers immediate:

- Where is each canonical repository?
- Which checkout is clean default branch?
- Which worktrees are active production work?
- Which experiments are disposable and what question did each answer?
- Which control documents are current and when were they last verified?
- Which artifacts are accepted evidence and how were they produced?
- Which paths are safe to delete because they are recreatable scratch?
- Which inactive material should be archived or removed?

Cleanup is complete when the workspace is easier to operate and resume, not when
it has the fewest visible folders.
