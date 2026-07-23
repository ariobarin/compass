# Large Workspace Git Audit

Audit a large nested workspace by resolving repository identity once, then
enumerating registered worktrees from Git. This route exists because recursively
running status against every `.git` entry is slow, misses linked worktrees when
`.git` is a file, and repeats repository-level remote work.

The terminal result is a read-only preservation inventory that distinguishes
represented work from local changes at risk. It does not authorize cleanup.

## Establish The Boundary

Name the search roots, known canonical repositories, expected worktree areas,
remote hosts, and snapshot time. Read workspace guidance before interpreting
generated artifacts, vendored repositories, archives, or scratch.

Use known canonical repository roots when they exist. When discovery is needed,
find likely repository roots first and resolve each with:

```powershell
git -C <candidate> rev-parse --show-toplevel
git -C <candidate> rev-parse --git-common-dir
```

Treat `.git` files and `.git` directories as discovery hints, not independent
repositories. Deduplicate by resolved common Git directory before collecting
state.

## Enumerate Registered Worktrees

For each common repository, run:

```powershell
git -C <canonical-repo> worktree list --porcelain
```

Deduplicate the returned worktree paths. This inventory owns registered linked
worktrees, including paths outside the initial search root. Do not infer that a
detached worktree is disposable.

Collect worktree state with bounded parallelism:

```powershell
git -C <worktree> status --porcelain=v2 --branch
git -C <worktree> rev-parse HEAD
git -C <worktree> branch --show-current
```

Collect repository-level remotes, branches, and stashes once per common
repository. Avoid repeated network queries for every worktree.

## Join Representation Evidence

Use `git-branch-resolver` to interpret branch and PR state. Join local branches
to current remote refs and pull requests only after the local inventory is
deduplicated.

Query exact unresolved repository and branch pairs. Confirm remote existence
with `git ls-remote --heads` when local tracking refs may be stale. Fetching,
pruning, closing, deleting, moving, or removing remains outside a read-only
audit unless separately authorized.

Classify each meaningful state as:

- clean and represented by a current remote or pull request;
- dirty but represented by an active pull request;
- local commits without verified remote representation;
- meaningful uncommitted or staged work without verified representation;
- detached worktree with meaningful changes;
- gone or superseded branch with retained evidence;
- generated, vendored, archived, or recreatable residue;
- unresolved and requiring owner review.

Separate source changes from caches, browser profiles, results, dependency
trees, and generated artifacts before lowering risk. A suspicious branch name,
detached head, or missing merge base is not proof that work is disposable.

## Keep The Audit Scalable

- Resolve common repositories before worktrees.
- Run one worktree enumeration per common repository.
- Bound parallel status checks and preserve deterministic output ordering.
- Cache repository-level remote and pull-request results.
- Query remote or host metadata only for unresolved candidates.
- Record timeouts and incomplete coverage instead of silently shrinking scope.

Do not recurse through every nested `.git` path and run a full status from each.
That route duplicates registered worktrees, misses file-based links, and scales
with filesystem noise rather than repository state.

## Return A Preservation Inventory

Report:

- search roots and snapshot time;
- common repository and registered worktree counts;
- dirty, detached, local-only, and unresolved counts;
- exact paths, branches, and head SHAs for preservation risks;
- verified remote or pull-request representation;
- incomplete checks and timeouts;
- recommended preservation action for each unresolved item.

Recommend commit and push, patch or bundle export, archive, owner decision, or
explicit disposable classification. Keep deletion and cleanup behind separate
authority.
