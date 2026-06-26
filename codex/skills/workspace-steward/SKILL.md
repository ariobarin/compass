---
name: workspace-steward
description: Set up and maintain umbrella workspaces with child repos, worktrees, artifacts, scripts, configs, tmp space, docs, and cleanup rules.
---

# Workspace Steward

Use this skill as a stewardship frame, not as a cleanup reflex. The goal is to
make a workspace easier to enter, operate, preserve, and review without hiding
active work or destroying evidence.

An umbrella workspace is different from a monorepo. The root coordinates
multiple child repos and shared operating surfaces; it should not pretend all
source belongs under one `src/` tree.

## Core Model

Keep each top-level bucket owned by one lifecycle:

- canonical child repos: active repos people work in directly;
- `docs/`: maps, principles, decisions, current operating docs, and dated
  records;
- `experiments/`: exploratory code or notes that have not become a repo,
  artifact, or archived reference;
- `configs/`: reusable non-secret defaults;
- `scripts/`: reusable operator tooling with documented inputs and effects;
- `artifacts/`: generated evidence, reports, logs, exports, and manifests;
- `worktrees/`: non-canonical Git worktrees grouped by state;
- `tmp/`: disposable scratch space for local intermediate files;
- `archived/`: inactive reference checkouts and obsolete tooling.

Use this generic starting shape when creating or explaining an umbrella
workspace:

```text
workspace/
  README.md
  AGENTS.md
  repo-a/
  repo-b/
  repo-c/
  docs/
  experiments/
  configs/
  scripts/
  artifacts/
  worktrees/
  tmp/
  archived/
```

Root child repos should be named as repos, not generic projects. If the main
unit of work is a repo, keep it visible at the root until there is a tested
migration plan for every script, shortcut, automation, and doc path that names
it.

## Setup Pass

When shaping a new or messy workspace:

1. Read local guidance first: root `AGENTS.md`, root `README.md`, then any
   existing docs index.
2. Inventory root entries and classify each as canonical repo, worktree,
   artifact, reusable tool, config, experiment, archive, scratch, or unknown.
3. Draft the target layout before moving files. Prefer a small map over a large
   procedure.
4. Create local README files only where they reduce root-doc pressure.
5. Add ignore rules for `tmp/`, caches, logs, credentials, browser state, and
   generated runtime state.
6. Move or delete only after preservation evidence exists.

Do not classify by folder name alone. For Git directories, use Git metadata:

```powershell
git rev-parse --git-common-dir
git worktree list --porcelain
git status --short --branch
```

## Maintenance Pass

Maintain the workspace by asking what a cold reader needs to do next:

- Can they find the canonical repo without reading history?
- Can they tell whether a worktree is active, waiting, review-only, preserved,
  or disposable?
- Can they find generated evidence without mixing it with source?
- Can they tell which scripts are current and which are historical?
- Can they see whether configs are reusable defaults or one-run state?
- Can they safely ignore `tmp/`?

Prefer small reviewable changes. One ownership README for one unclear area is
usually better than a broad cleanup PR that moves unrelated things.

## Bucket Rules

Keep child repos at the root when they are canonical active work. Do not move
them under `src/` unless the workspace is actually one repo with internal source
packages.

Use `worktrees/` for Git checkouts that are not canonical. Group them by state,
for example:

```text
worktrees/
  prs/
    in-progress/
    waiting-for-merge/
    review/
  preserved/
  delete-candidates/
```

Move registered worktrees with `git worktree move`. Remove them with
`git worktree remove` only after merge, preservation, or explicit disposable
evidence.

Use `artifacts/` for generated evidence that may matter later. Add a nearby
manifest or notes with source, owner, date range, retention, secret-scan status,
and regeneration instructions. Put suspect raw outputs under quarantine rather
than in the general archive.

Use `tmp/` for scratch files that can be recreated or discarded. Do not put
unique research, benchmark evidence, dirty patches, handoff notes, or reusable
tools there. If a scratch file becomes useful, promote it to `artifacts/`,
`docs/`, `scripts/`, or a repo branch.

Use `experiments/` for exploratory work that is still being understood. When an
experiment becomes durable, promote it to a repo, a documented artifact, a
script, or an archived reference. Avoid duplicating abandoned-experiment buckets
in both `experiments/` and `archived/`.

Use `scripts/` only for reusable tools. One-off launchers belong beside their
artifact outputs or under `archived/` with context.

Use `configs/` for reusable non-secret defaults. One-run configs belong with
the run artifact. Secrets and machine-only trust state stay local and ignored.

## Cleanup Boundaries

Default to preservation-first cleanup:

- inspect dirty state before moving anything;
- export or commit useful work before deleting;
- keep old benchmark or run evidence unless an owner approves deletion;
- delete remote branches only on owned remotes and only after PR and branch
  checks;
- treat foreign remotes, uncertain branches, and stale automations as report
  targets, not mutation targets.

Cleanup is done when the workspace is easier to operate, not when the root is
as small as possible. "Keep forever" means preserve in the right place, not keep
at the root.

## Common Failure Modes

- Duplicating active repos into role-named root worktrees instead of selecting
  variants by runtime flags or config.
- Treating logs and run outputs as clutter instead of evidence.
- Putting long dated inventories into root guidance files.
- Leaving reusable scripts undocumented.
- Letting `tmp/` become a hidden source of truth.
- Moving Git worktrees by hand and breaking registration.
- Opening one broad cleanup PR instead of scoped ownership changes.
