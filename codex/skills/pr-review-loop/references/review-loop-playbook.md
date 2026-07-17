# PR Review Loop Playbook

Use this reference when current-head review needs a confined patch, observable
behavior proof, structured waiting, or a decision about stale PR identity.

## Current-Head Discipline

Evidence belongs to a head SHA.

- Reread the SHA after every push, rebase, force-push, or retarget.
- Refresh checks and reviewers whose proof targets an older head.
- Name the tested build, ref, or artifact for behavior validation.
- Inspect inline comments independently from top-level comments and review
  bodies.
- Treat approval, test output, and runtime proof as stale when their target
  identity changed materially.

## Confined Source-Aware Review

Use `scripts/build-review-bundle.py` when a fresh reviewer should see the full
selected patch without parent conversation or arbitrary checkout files.

The bundle contains:

- complete binary-capable patch;
- base and head SHAs;
- changed paths and hashes;
- optional task file;
- explicitly selected context datasets.

It accepts only a clean committed range and rejects escaping paths, symlinks,
secret-like content, existing output directories, empty patches, and oversized
bundles. A truncated diff is not an equivalent review surface.

## Proportionate Review Selection

Choose gates from the claim being made:

- Every PR loop: one independent current-head reviewer.
- Repository or user policy: every additional named reviewer.
- Specialized risk: the relevant specialist reviewer.
- Material observable behavior not fully proven by ordinary tests: fresh
  source-blind `behavior-validator` result.
- Narrow documentation, metadata, formatting, or deterministic generated output:
  the independent review and exact mechanical check may be sufficient.

Record why a gate applies. Neither habitual over-review nor convenient
under-review is evidence.

## Source-Blind Behavior Validation

Capture the observable contract before implementation detail can redefine
success. Build an isolated workspace through `behavior-validator` and launch a
fresh non-forked validator.

Provide only:

- contract and approved fixtures;
- exact target identity and access;
- approved credential route;
- observable evidence surfaces.

Implementation source, diffs, tests, history, review summaries, and source-aware
bundles remain outside the validator. Contamination requires a fresh workspace
and fresh run.

## Review Waiting

Review acknowledgement is not the terminal state. Wait on one observable
condition:

- requested review submitted;
- actionable comment added;
- check reaches a terminal result;
- head SHA changes and invalidates the wait.

Put polling inside one bounded command. On timeout, refresh live state once and
choose an authorized alternate reviewer, a changed wait, or a pending-gate
report.

## Stale PR Decision

Preserve the named PR when the user wants its branch identity and history.

Rebuild from the current default branch when the user wants current intent and
the old branch can no longer express that truthfully. Inspect the old branch as
source material, reapply only still-relevant intent, and open a replacement PR
under explicit authority.

## Output Evidence

Return:

- PR and branch identity;
- current head SHA;
- preserved or rebuilt decision;
- checks and their target;
- reviewer gates and their target SHA;
- behavior proof and target identity;
- unresolved findings;
- current public-mutation boundary.
