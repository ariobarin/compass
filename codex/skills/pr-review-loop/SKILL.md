---
name: pr-review-loop
description: Iterate a named PR through review, fixes, re-review, behavior proof, merge gates, and explicit closeout.
---

# PR Review Loop

Use this skill when the center of gravity is a pull request, not just a branch
or a code change. The job is to keep PR identity, review gates, current-head
state, observable behavior proof, and merge authority explicit from first
inspection through final ready state.

Review gates are mandatory. Run `neutral-critic` for every PR review loop. For
any `ariobarin/*` repository, also request a second independent reviewer (such
as `@codex` when available, or another fresh `neutral-critic` pass). Do not
treat either gate as optional, advisory, or covered by local checks.

Source-aware review and source-blind behavior validation are separate gates.
Source-aware reviewers inspect the patch and relevant implementation. When a PR
changes user-visible or operator-visible behavior, `behavior-validator` must
exercise the real surface from a written contract without seeing source, diffs,
tests, implementation notes, or review output.

This skill covers two common postures:

- iterate on the exact PR or branch the user named;
- rebuild a stale PR from source material when the user wants current-main work
  rather than preserving the old PR identity.

## Required Reference

Read [review-loop-playbook.md](references/review-loop-playbook.md) for named-PR,
stale-rebuild, re-review, source-aware bundle, behavior-validation, and
merge-boundary patterns.

## Loop

1. Inspect the live PR state first: repo, base, head branch, head SHA, checks,
   review status, top-level comments, and inline review comments.
2. Decide the posture before editing: preserve the named PR, rebuild from stale
   source material on current main, or stay read-only.
3. For user-visible or operator-visible behavior, write the behavior contract
   from the request before implementation details can bias the expected result.
4. Patch only the scope needed for the current PR claim or the approved rebuild.
5. Run the narrowest checks that cover the changed implementation.
6. Run `neutral-critic` for every PR loop. Resolve its findings and get a green
   current-head result before requesting the second reviewer for an
   `ariobarin/*` PR, unless the user explicitly requires parallel reviews.
7. Request the second independent review. If the request receives an `eyes`
   reaction, wait one bounded five-minute interval before checking once.
8. When behavior changed, launch a fresh `behavior-validator` with only the
   contract, target access, allowed fixtures, and redacted observable evidence.
   Resolve failures and rerun affected clauses plus nearby regression probes.
9. After any material push, re-read the head SHA and re-request review on that
   new head before calling the PR ready or merging.
10. Merge only when the user or repo workflow explicitly authorized it.
11. For an explicit closeout request, archive the task after a confirmed merge.
    If the PR cannot merge, leave it open and comment with the blocking evidence.

## Confined Source-Aware Bundles

When a fresh source-aware reviewer should not inherit the current chat or full
checkout, run `scripts/build-review-bundle.py` from this skill directory. The
helper creates a new private directory outside the repository containing only a
complete Git patch, a manifest, and explicitly named repo-relative context.

```text
python <skill-dir>/scripts/build-review-bundle.py \
  --root <repo> \
  --base origin/<base> \
  --head <head> \
  --output <new-temp-directory> \
  --task-file <repo-relative-task-file> \
  --dataset <repo-relative-context-file>
```

The helper fails when the working tree is dirty, the selected diff is empty or
too large, a changed or context path looks sensitive, content looks secret-like,
context escapes the repository, or the output already exists. Do not bypass a
failure with a partial patch. Redact or split the review while preserving the
complete claim.

A source-aware bundle is still implementation material. Never give it to
`behavior-validator` or count its verdict as source-blind behavior proof.

## Rules

- If the user names a specific PR or branch, do not quietly redirect to a new
  PR unless they ask for a rebuild or branch surgery.
- If the user wants current-main work and the old PR is stale, treat the old PR
  as source material only and rebuild cleanly on current main.
- `neutral-critic` is required for every PR review loop. Do not claim
  readiness or merge without a green current-head result unless the user
  explicitly removes that gate.
- In any `ariobarin/*` repo, a second independent reviewer is required in
  addition to `neutral-critic`. Do not leave that gate conditional, vague, or
  treated as polish.
- Do not spend the second review on a head that has not cleared
  `neutral-critic`. After an `eyes` acknowledgement, let one bounded five-minute
  wait own the clock instead of repeatedly polling GitHub.
- Local checks do not satisfy review gates. They prove the implementation path;
  they do not replace reviewer approval or user-surface validation.
- A clean source-aware review does not prove changed behavior. When the PR makes
  a user-visible claim, require clause-level evidence from `behavior-validator`.
- Top-level review text does not clear inline findings. Inspect inline review
  comments separately before claiming readiness or merge safety.
- If review is silent, use an authorized alternate review route rather than
  waiting passively. Name the missing gate and why the alternate route is
  allowed.
- If the user performs merges, stop at merge boundary with the exact next merge
  action.
- If the user requested closeout and authorized merging, archive the task only
  after GitHub confirms the merge. Otherwise, leave the PR open and comment
  with the unsatisfied gate or actionable finding.
- If a base branch moved, re-check whether downstream PRs still have a real
  delta before keeping them alive.

## Related Skills

- Use `behavior-validator` for source-blind proof of observable behavior.
- Use `git-branch-resolver` when branch, worktree, or PR inventory is still
  unclear.
- Use `action-items-to-prs` when review findings or audit items should become
  one or more scoped PR changes.
- Use `orchestration-controller` when the work is mostly review routing,
  monitoring, or completion-gate enforcement.
