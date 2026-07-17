# <Project> Workspace

Umbrella workspace for <project>. This root coordinates child repositories,
production worktrees, disposable experiments, control documents, evidence, and
archives. It may be its own small Git repository, but it is not automatically a
monorepo. Canonical child checkouts stay visible at the root by name.

## Operating Model

One user-facing principal preserves the objective across contexts. The user or
principal authors goals, plans, catalogs, assignments, and checkpoints under
`local-docs/`. Delegates execute reviewed assignments and return artifacts plus
evidence. A fresh principal context resumes from those anchors rather than from
conversation memory.

Use absolute timestamps with time zones in mutable control documents and
evidence notes. `Last verified at` matters more than a vague modification date.

## Layout

- `<repo>-main/`: clean default-branch checkout for reading, syncing, and
  creating worktrees.
- `<repo>/`: canonical checkout when the project needs one distinct from the
  clean-main checkout.
- `worktrees/prs/`: production-bound branch and PR work.
- `worktrees/spikes/`: disposable integration spikes that require the real
  repository but are not production-bound.
- `experiments/`: tiny isolated programs that answer one uncertainty and never
  become production code.
- `local-docs/`: principal-authored goals, plans, catalogs, assignments,
  checkpoints, and decisions.
- `docs/`: durable project and workspace documentation.
- `artifacts/`: generated evidence, reports, exports, logs, and manifests.
- `tmp/`: recreatable scratch.
- `archived/`: inactive material preserved with dated context.
- `glossary.md`: terms whose distinctions change behavior.

Each lifecycle area has its own README. Read it before creating or promoting
material there.

## Adopt This Template

1. Copy the template contents into a new workspace root.
2. Replace `<Project>` and other placeholders with real names.
3. Initialize the root repository when it will own these control documents.
4. Add concrete child checkout names to `.gitignore` before cloning.
5. Clone each child as a clean `<repo>-main` checkout.
6. Record repository identities and default branches in the root documentation.
7. Create production work in `worktrees/prs/<slug>` from the intended current
   remote base, usually `origin/main`.
8. Keep experiments and spikes visibly disposable.
9. Review `AGENTS.md`, `CLAUDE.md`, and `glossary.md` for project-specific truth.

## Fresh Worktree Convention

```sh
git -C <repo>-main fetch origin
git -C <repo>-main status --short --branch
git -C <repo>-main worktree add -b <branch> <workspace>/worktrees/prs/<slug> origin/main
```

Use the project-declared default branch when it differs. Move registered
worktrees with `git worktree move`. Remove them with `git worktree remove` only
after merge, preservation, or explicit disposable evidence.

## Continuity Test

A fresh principal context should be able to open the current goal, plan,
catalog, checkpoint, and named repository state, then answer:

- What finished state remains authoritative?
- What phase is authorized?
- Which assignments are active?
- What evidence is current?
- What remains unresolved?
- What action can produce the next useful proof?

When it cannot, repair the control documents before adding more work.
