---
name: git-branch-resolver
description: Inspect or resolve Git branches, worktrees, remotes, and PRs with depth proportional to the requested action.
---

# Git Branch Resolver

Use this skill to inspect or change branch state without losing active work.

## Choose Scope First

- **Named PR or branch:** inspect the exact branch, its worktree, base and head
  relationship, remote tracking state, and named PR. Widen only when evidence
  shows a stack, conflict, shared worktree, or cleanup dependency.
- **Audit or cleanup:** inventory all local branches, worktrees, remotes, and PRs
  before recommending or performing deletion.
- **Requested refresh:** preserve the named branch and PR identity while bringing
  it current and re-verifying it.

Do not perform a full repository branch census for a targeted named-PR question
unless the target cannot be understood safely without it.

## Read Repo Guidance

Before mutation, read the nearest `AGENTS.md`, project overview, and branch or PR
workflow. Preserve commit, PR body, line-ending, and review rules.

## Targeted Inspection

For a named branch or PR, gather only what establishes its state:

```powershell
git status --short --branch
git worktree list --porcelain
git branch -vv --no-color <branch>
git log --oneline --decorate --left-right --cherry-pick origin/<base>...<branch>
git diff --stat origin/<base>...<branch>
gh pr view <number> --json number,title,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,url
```

Read unusual or dirty worktree state before changing anything.

## Full Audit

For cleanup or broad audit, collect:

```powershell
git status --short --branch
git worktree list --porcelain
git branch -vv --no-color
git branch -r --no-color
git remote -v
gh pr list --state all --json number,title,headRefName,headRefOid,baseRefName,state,isDraft,mergedAt,updatedAt,url --limit 200
```

Classify branches as active PR, useful local work, stacked, merged, superseded,
backup-only, stale-but-valuable, or delete candidate.

Read-only audits do not fetch or prune unless the user asks to refresh refs.
Mutation work must refresh refs first and stop if that refresh fails.

## Preserve Before Mutation

- Keep work on the exact named branch or PR.
- Commit or otherwise preserve dirty useful work before rebase, deletion, or
  worktree removal.
- Use a dedicated worktree when the main checkout is busy or dirty.
- Preserve remote divergence before any overwrite.
- Resolve conflicts by retaining current default behavior for stale guidance and
  branch behavior for the still-new substantive change.
- Run `git diff --check` after conflict resolution.

## Destructive Boundary

Deletion, PR closure, retargeting, and worktree removal require explicit cleanup
authority. Before deleting, prove the work is merged, represented by an open PR,
superseded, or preserved elsewhere. Never remove a dirty worktree.

## Verification

Re-read current state after mutation. For refresh or cleanup, verify branches,
remote refs, worktrees, named PR state, and repo-specific checks. For targeted
read-only work, report the evidence inspected and do not imply a global audit.

## Output

Report operating scope, branch or PR identity, evidence inspected, preservation
actions, mutations, exact commit SHAs, verification, intentionally retained
state, and the next recommended action.
