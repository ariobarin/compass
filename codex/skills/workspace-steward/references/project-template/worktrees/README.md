# worktrees

Branch and PR work for the child repos, kept out of the clean main checkouts.

- `prs/<slug>/` - worktrees for branches or PRs that are meant to be pushed.
- Create them from the child repo's `origin/main`, not a dirty local main.
- Exploratory or local-only work does not belong here; use `../experiments/`,
  `../artifacts/`, or `../local-docs/` instead.

The contents of `prs/` are gitignored in the root repo because each entry is a
git worktree linked to its child repo, not files this root should track.

Move worktrees with `git worktree move`, and remove them with `git worktree
remove` only after merge, preservation, or explicit disposable evidence.
