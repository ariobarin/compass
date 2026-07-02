# <Project> Workspace

Umbrella workspace for <project>. This root coordinates several child repos and
local operating surfaces. It is usually its own git repo, but it is not a
monorepo: canonical repo checkouts stay visible at the root by name.

## Layout

- `<repo>/` and `<repo>-main/` - canonical repo checkouts live at the root,
  revealed by name, never tucked under `src/` or a generic bucket. A `<repo>-main`
  checkout stays on the default branch for reading, syncing, and spawning
  worktrees; keep it clean of implementation edits.
- `worktrees/prs/` - branch and PR work that is meant to be pushed. Start each
  from the child repo's `origin/main`, not a dirty local main.
- `experiments/` - exploratory work that is not yet a repo, artifact, or PR.
  Promote it out when it earns a place.
- `local-docs/` - controller notes, plans, and handoffs: state about operating
  this workspace.
- `docs/` - durable project and workspace documentation.
- `artifacts/` - generated evidence: reports, exports, logs, manifests.
- `tmp/` - scratch files that can be recreated or deleted.
- `archived/` - inactive reference material, preserved as-is.

Each directory above has its own README with the rules that keep it honest.

## Adopt this template

1. Copy the contents of this directory into your new project root.
2. If the root is not yet a git repo, `git init` it. The shipped `.gitignore`
   keeps `tmp/` and child-repo worktrees out, and ignores secrets and caches.
3. Clone each child repo as a clean `<repo>-main` on the default branch, used
   only for reading, syncing, and creating worktrees.
4. Start PR work in `worktrees/prs/<slug>` from the child repo's `origin/main`.
5. Replace this heading and the bracketed placeholders with the project name and
   real repo identities.

## Worktree convention

Keep the clean main checkout clean. Create PR worktrees from the child repo:

```sh
git -C <repo>-main fetch origin
git -C <repo>-main worktree add -b <branch> <root>/worktrees/prs/<slug> origin/main
```

If local project guidance names a different default branch, use it explicitly
and note why. Move worktrees with `git worktree move`, and remove them with
`git worktree remove` only after merge, preservation, or explicit disposable
evidence.

## Operating notes

Read this README and `AGENTS.md` before changing layout. Treat `tmp/` as
deletable: promote useful scratch to `artifacts/`, `scripts/`, `docs/`, or
`local-docs/`. Add `scripts/` or `manifests/` only when a repeated operation
earns the maintenance.
