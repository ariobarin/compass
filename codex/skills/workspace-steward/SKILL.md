---
name: workspace-steward
description: Organize and audit local multi-repo workspaces with clean main checkouts, PR worktrees, experiments, local docs, artifacts, tmp space, and evidence rules.
---

# Workspace Steward

Use this skill to make a workspace easier to enter, operate, and review while
preserving active work and evidence. The first move is to make the requested
change earn its place.

An umbrella workspace coordinates multiple child repos and local operating
surfaces. It is not automatically a monorepo, and its root might not be the repo
that a command should operate on.

## Decision Filter

Run this filter in order before changing layout, moving files, adding scripts,
or automating cleanup:

1. Challenge the requirement. State the current confusion, repeated cost, or
   safety risk the change is meant to fix.
2. Remove what does not earn maintenance. Delete proposed buckets, docs, scripts,
   or conventions that do not solve that stated problem.
3. Simplify what remains. Prefer fewer paths, clearer names, and existing Git
   or shell behavior over new process.
4. Speed up only after the shape is right. Add aliases, scripts, templates, or
   manifests only when they shorten a proven workflow.
5. Automate last. Automate only stable, repeated operations with clear inputs,
   outputs, rollback, and preservation boundaries.

If a proposed folder, move, script, or automation fails an earlier filter, stop
and report the smaller change that survived.

## Operating Model

Question the target layout before moving anything. Ask what problem the change
solves, who will use it next, and whether a smaller note, ignore rule, or
worktree convention would solve it.

Keep top-level areas tied to one lifecycle:

- canonical repo checkouts stay visible at the root;
- clean main checkouts, usually `<repo>-main`, stay on the default branch for
  reading, syncing, and creating worktrees;
- `worktrees/prs/` holds branch or PR work that is intended to be pushed;
- `experiments/` holds exploratory work that is not yet a repo, artifact, or
  PR;
- `local-docs/` holds controller notes, plans, and handoffs;
- `docs/` holds durable project or workspace documentation;
- `artifacts/` holds generated evidence, reports, exports, logs, and manifests;
- `tmp/` holds scratch files that can be recreated or deleted;
- `archived/` holds inactive reference material.

Use names that reveal repo identity. Do not move active repos under generic
buckets such as `src/` unless the workspace is actually one repository with
internal packages and every path dependency has a migration plan.

## Before Editing

1. Read root `AGENTS.md`, root `README.md`, and the nearest docs index.
2. Identify the actual Git repo before branch, commit, push, or status work:

```powershell
git rev-parse --show-toplevel
git status --short --branch
git remote -v
```

3. Classify uncertain directories by evidence, not name:

```powershell
git rev-parse --git-common-dir
git worktree list --porcelain
git status --short --branch
```

4. Inspect dirty state and preserve useful work before moving or deleting files.
5. Draft the smallest target layout that solves the specific confusion.

## Worktree Rules

Keep the clean main checkout clean. Use it for reading, syncing, and creating
worktrees, not ordinary implementation edits.

Start PR worktrees from `origin/main` by default, not from a dirty local main
checkout:

```powershell
git -C <repo-main> fetch origin
git -C <repo-main> status --short --branch
git -C <repo-main> worktree add -b <branch-name> <umbrella>\worktrees\prs\<slug> origin/main
```

If local project guidance names a different default branch, use that branch
explicitly and explain the deviation.

Treat `worktrees/prs/` as pushed-work territory. If the work is exploratory or
local-only, use `experiments/`, `artifacts/`, or `local-docs/` instead.

Move registered worktrees with `git worktree move`. Remove them with
`git worktree remove` only after merge, preservation, or explicit disposable
evidence.

Before cleanup, inspect registration:

```powershell
git -C <repo-main> worktree list --porcelain
git -C <repo-main> worktree prune --dry-run --verbose
```

Treat stale or prunable entries as report targets first. Run `git worktree
prune` only after confirming the path is gone and no work needs preservation.

## Evidence Rules

Do not let `tmp/` become a hidden source of truth. Promote useful scratch work
to the right durable surface:

- reproducible evidence or reports: `artifacts/`;
- reusable tooling: `scripts/`;
- project or workspace docs: `docs/`;
- controller notes or handoffs: `local-docs/`;
- branch-bound code changes: a repo branch or PR.

When preserving generated evidence, add nearby notes with source, owner, date
range, retention, secret-scan status, and regeneration instructions when those
details are not obvious.

Keep secrets, credentials, browser state, local trust state, and machine-only
runtime caches ignored and local.

## Maintenance Pass

When auditing an existing workspace, answer these questions in the final report
or the changed README:

- Where is the canonical repo?
- Which checkout is clean main?
- Which worktrees are active PR work?
- Which artifacts are evidence, and how were they produced?
- Which notes are local controller state instead of product docs?
- Which files are safe to delete because they are recreatable scratch?

Prefer one small ownership README or ignore rule over a broad cleanup. Cleanup
is done when the workspace is easier to operate, not when the root has the
fewest folders.
