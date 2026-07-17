# PR Review Loop Playbook

Use this reference for current-head review, confined reviewer context,
source-blind behavior proof, and stale PR decisions.

## Current-Head Discipline

Review evidence belongs to a head SHA.

- Re-read the SHA after push, force-push, rebase, or retarget.
- Refresh checks and reviewers when their evidence targets an older head.
- Identify the tested build, ref, or artifact for behavior validation.
- Do not call a PR ready from stale approval or stale runtime proof.

## Confined Source-Aware Review

Use `scripts/build-review-bundle.py` when a fresh reviewer should see the full
selected patch without the current conversation or arbitrary checkout files.

The bundle includes:

- the complete binary-capable patch;
- base and head SHAs;
- changed paths and hashes;
- an optional task file;
- only explicitly selected datasets.

It rejects dirty worktrees, empty or oversized patches, secret-like content,
escaping paths, symlinks, and existing output directories. A truncated diff is
not an equivalent fallback.

## Source-Blind Behavior Validation

Capture the observable contract before implementation detail can redefine
success. Build the isolated workspace through `behavior-validator`, then launch
a fresh non-forked validator agent.

Give the validator only:

- contract and approved fixtures;
- exact target identity and access instructions;
- approved credentials;
- observable evidence surfaces.

Do not provide source, diffs, tests, history, review summaries, or a review
bundle. Contamination requires a fresh workspace and fresh run.

Skip this gate only when there is no user-visible or operator-visible behavior
claim.

## Review Waiting

Review acknowledgement is not approval. Wait on the actual review state with one
bounded condition:

- requested review submitted;
- actionable comment added;
- check reaches terminal state;
- head SHA changes and invalidates the wait.

Derive the timeout from a repository SLA, stated reviewer window, user deadline,
or explicit operational limit. Put polling inside one command. On timeout,
refresh the live PR once and choose an authorized alternate route or report the
pending gate. Never use a fixed interval as proof that a reviewer had enough
time.

## Stale PR Rebuild

Rebuild when the user wants current-main intent rather than preservation of the
old PR identity.

- Inspect the old branch for source material.
- Start from current default branch.
- Reapply only still-relevant intent.
- Open a new PR when the result is no longer truthfully the same branch history.

Preserve the named PR when the user asked to keep iterating it.

## Gate Order

Unless the user requires parallel review:

1. run narrow checks;
2. complete `neutral-critic`;
3. resolve findings and verify the new head;
4. request the second reviewer;
5. run source-blind behavior validation when required;
6. report readiness at the merge boundary.

A pending gate stays pending. An authorized alternate route must be named.

## Output

Report:

- repository and PR;
- base, head branch, and current SHA;
- preserved or rebuilt identity;
- checks and their result;
- reviewer gates and head SHA each targeted;
- behavior contract result;
- unresolved findings;
- merge authority and current boundary.
