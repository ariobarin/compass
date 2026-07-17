# Codex Guidance for <Project> Workspace

This root coordinates several repositories and local operating surfaces. Identify
the actual Git repository before branch, commit, push, or status work.

```sh
git rev-parse --show-toplevel
git status --short --branch
git remote -v
```

## Direction

Preserve one coherent objective across finite contexts. The user or user-facing
principal authors goals, plans, catalogs, assignments, and checkpoints under
`local-docs/`. Delegated workers execute reviewed assignments and return
artifacts plus evidence. They do not invent independent control state.

Lead with the desired state and evidence. Use prohibitions for crisp safety,
authority, and lifecycle boundaries.

## Workspace Boundaries

- Keep `<repo>-main` checkouts on the declared default branch and free of
  implementation edits.
- Put production-bound work in `worktrees/prs/<slug>` from the intended current
  remote base.
- Put real-repository integration spikes in `worktrees/spikes/`.
- Put isolated one-question disposable programs in `experiments/`.
- Let findings graduate from experiments. Reimplement production behavior in a
  real worktree.
- Keep durable product truth in `docs/` and principal operating state in
  `local-docs/`.
- Keep generated evidence in `artifacts/` with provenance and timestamps.
- Treat `tmp/` as deletable.
- Preserve secrets, credentials, browser state, sessions, and machine caches
  outside tracked files.

Read the root README and the lifecycle README nearest the work before moving,
promoting, or deleting material.
