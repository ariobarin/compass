# worktrees

Real child-repository checkouts attached to branches.

- `prs/<slug>/`: production-bound work intended for review and possible merge.
- `spikes/<slug>/`: disposable integration questions against the real project.

Create each worktree from the intended current remote base after fetching and
checking the clean-main checkout. Keep one coherent scope per branch. Preserve
useful dirty work before rebase, move, or removal.

A spike remains disposable. Reimplement accepted findings in a fresh PR
worktree. Move registered worktrees with `git worktree move` and remove them with
`git worktree remove` only after merge, preservation, or explicit disposal.
