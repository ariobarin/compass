# PR Host Fallbacks

Use this reference when PR work depends on repo context, remote selection, or
GitHub access that may be blocked or incomplete.

## Outside A Repo

- If the shell is not in a repository, do not guess.
- Ask for the target `owner/repo` or a local repo path before PR inspection.
- Restate the target repo before acting when nearby context names multiple repos.

## Multi-Remote Forks

- Inspect `git remote -v` before opening, refreshing, or retargeting a PR.
- If both `origin` and `upstream` exist and `origin` is the user's fork,
  prefer `origin` unless the user explicitly asked for `upstream`.
- State the intended base repo and base branch before changing PR state when
  the remote layout is ambiguous.

## Local Fallback When GitHub Access Fails

- If `gh`, a connector, or repo permissions cannot read the requested PR, fetch
  the PR ref locally and review it in a temporary worktree.
- Prefer a temp worktree under the project parent or another writable sibling
  path, not an unrelated global temp directory that may have different access
  or cleanup rules.
- Preserve the requested branch identity when replaying or refreshing PR work.
- Re-run local verification before pushing a refreshed branch.

Example:

```powershell
git fetch origin pull/<pr-number>/head:pr-<pr-number>-review
git worktree add ..\pr-<pr-number>-review pr-<pr-number>-review
```

- Remove the temporary review worktree only after any useful notes, commits, or
  preservation branches have been kept.
