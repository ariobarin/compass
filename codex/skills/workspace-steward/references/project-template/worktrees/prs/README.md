# PR Worktrees

Use this area for real repository changes intended for review and possible merge.
Each worktree has one branch, one coherent purpose, one editing owner, and a
clear base.

Before creating a worktree:

- fetch the remote through the clean-main checkout;
- identify the project-declared default or target base;
- confirm the branch name and destination are unused;
- record the assignment, scope, evidence target, and public mutation authority.

Create from current remote state, usually:

```sh
git -C <repo>-main worktree add -b <branch> <workspace>/worktrees/prs/<slug> origin/main
```

Keep experiments, integration spikes, private control documents, and unrelated
user changes outside the PR branch. Preserve useful dirty work before rebase,
move, or removal. Remove the worktree through Git after merge, preservation, or
an explicit decision that the branch is disposable.
