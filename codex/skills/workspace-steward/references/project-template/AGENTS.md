# Agent Guidance for <Project> Workspace

This root is an umbrella workspace, not a single product repo. Identify the
actual git repo before any branch, commit, push, or status work:

```sh
git rev-parse --show-toplevel
git status --short --branch
git remote -v
```

Operating rules:

- Canonical repo checkouts live at the root by name. A `<repo>-main` checkout
  stays on the default branch and stays clean of implementation edits.
- PR work goes in `worktrees/prs/<slug>`, started from the child repo's
  `origin/main`, not a dirty local main.
- `docs/` is durable documentation. `local-docs/` is controller operating state
  for this workspace.
- `artifacts/` holds generated evidence with a provenance note. `tmp/` is
  deletable scratch and is gitignored.
- Keep secrets, credentials, browser state, and machine-only caches ignored and
  local.

Read the root `README.md` for the full layout before moving files or adding
conventions.
