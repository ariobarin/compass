---
name: git-branch-resolver
description: Audit and safely resolve Git branches, worktrees, remotes, and PRs. Use for read-only audits, requested PR refreshes, preservation, and explicit cleanup.
---

# git-branch-resolver

Use this skill to audit or refresh Git branch state without losing active work.

Choose a mode before mutating anything:

- `audit/report`: inventory branches, worktrees, remotes, and PRs; classify
  their state; recommend next actions; do not change branches, worktrees,
  commits, or PR state.
- `refresh requested PR`: keep work on the exact branch or PR the user named,
  refresh it against the current base, reverify, and preserve branch identity.
- `cleanup on request`: after inventory and preservation, delete or retarget
  clearly redundant state the user explicitly asked to clean up.

Default to `audit/report` or `refresh requested PR`. In those modes, do not
delete branches, remove worktrees, retarget PRs, or close PRs. Move to cleanup
only when the user explicitly asks for those cleanup actions.

When the user names a specific branch or PR, keep work on that exact branch.
Do not redirect the work to a different PR or replacement branch unless the
user asks for that outcome.

For explicit cleanup work, the target end state is:

- remaining local branches are `main` or `master`, active PR branches, or
  clearly useful local work;
- remaining worktrees are clean and tied to useful active branches;
- remaining remote branches back open PRs, active external work, or the default
  branch;
- merged, duplicate, backup, preservation, closed-draft, and superseded
  branches are removed;
- valuable recent work is represented by a commit, pushed branch, or open PR;
- old branch intent is either proven upstream or recreated cleanly on the
  current default branch.

## Start with repo guidance

Read local guidance before changing branch state:

1. nearest `AGENTS.md` or repo-owned guidance file;
2. `README.md` or equivalent project overview;
3. any branch or PR workflow notes.

Preserve local rules from those files, especially commit message, PR body, and
line-ending requirements.

## Required References

Read [pr-host-fallbacks.md](references/pr-host-fallbacks.md) when PR work
depends on repo context, GitHub access, or multi-remote fork handling.

## Inventory first

If the prompt or repo rules require read-only inspection, or the user has not
opted into refreshing remote refs, collect current local state first and skip
fetch or prune:

```powershell
git status --short --branch
git worktree list --porcelain
git branch -vv --no-color
git branch -r --no-color
git remote -v
```

When the user explicitly opts into refreshing remote refs for `audit/report`,
cleanup, or PR refresh work, run:

```powershell
git fetch --all --prune
```

Treat that as a ref refresh, not read-only inspection, because it updates local
remote-tracking refs.

If the current shell is not inside the target repo, stop and ask for the
target `owner/repo` or local repo path before doing PR inspection or cleanup.

When `audit/report` skips fetch or prune, label branch classifications as based
on current local refs and call out that stale remote-tracking refs may affect
recommendations.

If GitHub is the host and `gh` is authenticated, infer `owner/repo` from
`git remote get-url origin`, then gather PRs:

```powershell
gh pr list --repo <owner/repo> --state all --json number,title,headRefName,headRefOid,baseRefName,state,isDraft,mergedAt,updatedAt,url --limit 200
```

For dirty or unusual worktrees:

```powershell
git -C <path> status --short --branch
git -C <path> log --oneline --decorate -8
git -C <path> diff --stat
```

If Git reports dubious ownership, use a one-shot safe directory value instead
of changing global config:

```powershell
git -c safe.directory=<absolute-path> -C <absolute-path> status --short --branch
```

## Classify each branch

Classify every local and remote branch before changing it:

- `active-pr`: backs an open PR and the head matches or should be updated.
- `needs-pr`: useful recent work exists but no open PR covers it.
- `stacked-pr`: branch is a base or head for another open PR.
- `already-merged`: PR is merged or the patch is already in the default branch.
- `superseded`: replaced by a later branch or PR with the same intent.
- `backup-only`: preserved prior state, and the represented work exists
  elsewhere.
- `stale-but-valuable`: old intent is still useful but should be recreated on
  current default branch.
- `delete-candidate`: no unique useful work remains.

Useful checks:

```powershell
git log --oneline --decorate --left-right --cherry-pick origin/<default>...<branch>
git diff --stat origin/<default>...<branch>
git branch --merged origin/<default> --no-color
git branch --no-merged origin/<default> --no-color
gh pr view <number> --repo <owner/repo> --json number,title,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,url
```

## Resolve safely

For a requested PR refresh:

- use a dedicated worktree when the main checkout is busy or dirty;
- fetch and re-read both the branch and default-branch state before editing;
- if upstream moved mid-task, replay or rebase the requested branch onto the new
  base, then reverify before pushing;
- preserve branch identity unless the user explicitly asked for branch surgery.

Preserve first:

- commit dirty useful work on the branch where it belongs;
- push branches that can fast-forward;
- if a remote branch has diverged and should not be overwritten, push a
  separate preservation branch first;
- if a nested repo or submodule cannot push to its own remote, preserve its diff
  using the parent repo's patch convention and avoid pushing inaccessible
  submodule pointers.

Update active PR branches carefully:

- rebase recent PR branches onto the current default branch when they are not
  intentionally stacked;
- for stacked PRs, update the base first, then check whether the head branch
  still has a meaningful delta;
- if the delta is already represented by the base or default branch, mark it as
  redundant in the audit and close or delete it only when the user asked for
  cleanup;
- when retargeting was explicitly requested, retarget PR bases to the default
  branch only after confirming old base branches have merged or been removed.

Handle conflicts conservatively:

- keep current default-branch behavior when a branch commit is stale wording,
  old guidance migration, or broad formatting from an old context;
- keep branch changes when they are the substantive still-new feature, fix, or
  proposal;
- skip stale preservation or guidance commits when newer work already carries
  that intent;
- run `git diff --check` after conflict resolution.

Delete only after explicit cleanup approval and evidence:

- confirm the user asked for cleanup or approved the specific cleanup action;
- prove the branch intent exists in `origin/<default>` or an open PR before
  deleting local branches, worktrees, or backup refs;
- if the upstream state is uncertain, preserve first and ask before deleting;
- delete local branches only after approval and after confirming work is merged,
  superseded, closed as redundant, or preserved elsewhere;
- delete remote branches only after approval and after confirming no open PR
  depends on them;
- remove clean stale worktrees with `git worktree remove <path>` only after
  approval;
- never remove dirty worktrees until dirty state is committed, pushed, or
  explicitly documented as disposable.

## Verification gates

Before reporting completion, re-read current state. If the user explicitly
opted into refreshing remote refs, run:

```powershell
git fetch --all --prune
git branch -vv --no-color
git branch -r --no-color
git worktree list --porcelain
```

If the task stayed read-only, skip fetch or prune and run the remaining local
state commands only.

If a PR host is available, verify open PRs:

```powershell
gh pr list --repo <owner/repo> --state open --json number,title,headRefName,headRefOid,baseRefName,state,isDraft,mergeStateStatus,url --limit 100
```

Check every remaining worktree is clean:

```powershell
$paths = @("<repo-path>")
foreach ($p in $paths) {
  "PATH`t$p"
  git -c safe.directory=$p -C $p status --short --branch
}
```

Run repo-specific validation when touched files require it, for example
line-ending guards for shell scripts or branch policy checks.

Completion requires evidence that remaining branches and worktrees are useful,
clean, and represented by open PRs, active remote work, or the current default
branch.

## Output

Report:

- operating mode used;
- requested branch or PR, if any, and whether branch identity was preserved;
- preserved or refreshed branches, worktrees, and exact commit SHAs;
- PRs opened, refreshed, rebased, retargeted, closed, or left active;
- the base repo and base branch used for any PR refresh or review;
- any branches intentionally left because they back open PRs or active external
  work;
- deleted local branches, worktrees, or remote branches, only when cleanup was
  requested or explicitly approved;
- verification commands and their result.
- next recommended action when the task stopped at audit or report mode.
