# Multi-Thread PR Coordination

Use this workflow when one repository objective benefits from parallel Codex
contexts, worktrees, or agents while the public review surface remains coherent.

The principal owns the objective, assignments, integration map, and public PR
authority. Workers own reviewed slices and return artifacts plus evidence.

## Establish The Control Packet

Before dispatch, the principal authors a compact goal and catalog that name:

- the finished state and evidence required;
- current base branch and authoritative repository state;
- active worktrees and their exact scope;
- reviewed worker assignments;
- dependencies and collision boundaries;
- the public PR budget;
- the return channel;
- public mutation authority.

Keep private operational state under `.local/` or another ignored project
surface. Keep worker worktrees outside the principal checkout.

## Prepare Reviewed Assignments

Each assignment states:

- one bounded outcome;
- relevant goal assertion identifiers;
- authoritative anchors;
- exact worktree and branch;
- allowed edits and actions;
- integration target;
- checks and evidence required;
- whether a PR may be opened;
- return conditions and channel.

The principal reviews the assignment before launch. Give the user an opportunity
to review material slice boundaries and public authority unless prior authority
or an explicit waiver covers the dispatch.

Workers report through the assignment return shape. They do not invent separate
tracking systems or rewrite the principal catalog.

## Preserve Worktree Independence

Use one editing owner per worktree. Start production-bound branches from the
intended current base, usually `origin/main`, after refreshing refs. Preserve
unrelated user work and keep experiments outside PR worktrees.

Parallelize slices only when their files, state, and integration order remain
clear. Keep coupled changes with one owner.

## Keep Public Review Focused

Set a visible PR budget, usually no more than three active PRs for one workstream.
A worker opens a PR only when the assignment grants that action and the change is:

- independently reviewable;
- scoped to one purpose;
- free of private tracking notes;
- based on the intended branch;
- accompanied by current verification or an explicit evidence gap.

The principal classifies each public change as a behavior fix, guard, durable
documentation change, eval or fixture update, or a narrowly justified
preservation branch. Mixed audit notes and speculative fixes remain local.

## Reconcile Returns

After a worker returns:

1. inspect the artifact and current branch state;
2. map evidence to the parent goal;
3. update the principal catalog and checkpoint;
4. identify integration dependencies and stale assignments;
5. prepare repair, review, or the next dispatch;
6. recompute the active PR budget.

A worker completion claim advances the objective only after the principal checks
the returned evidence.

## Consolidate With Authority

Inspect current-workstream PRs at meaningful decision points. Close duplicates,
refresh branches, retarget, or rewrite public state only within granted
authority. Treat unrelated PRs as context and preserve their owner boundaries.

Keep local tracking local when it contains scratch findings, temporary matrices,
ports, machine paths, logs, screenshots, seeded values, or notes useful only to
the current operator. Promote material upstream only when it becomes durable
project guidance or reviewable product work.
