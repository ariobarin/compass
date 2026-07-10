---
name: pr-review-loop
description: Iterate a named PR through review, fixes, re-review, merge gates, and explicit closeout. Use for named PRs, review feedback, dual review, or merge closeout.
---

# PR Review Loop

Use this skill when the center of gravity is a pull request, not just a branch
or a code change. The job is to keep PR identity, review gates, current-head
state, and merge authority explicit from first inspection through final ready
state.

Review gates are mandatory. Run `neutral-critic` for every PR review loop. For
any `ariobarin/*` repository, also request a second independent reviewer (such
as `@codex` when available, or another fresh `neutral-critic` pass). Do not
treat either gate as optional, advisory, or covered by local checks.

This skill covers two common postures:

- iterate on the exact PR or branch the user named;
- rebuild a stale PR from source material when the user wants current-main work
  rather than preserving the old PR identity.

## Required Reference

Read [review-loop-playbook.md](references/review-loop-playbook.md) for named-PR,
stale-rebuild, re-review, and merge-boundary patterns.

## Loop

1. Inspect the live PR state first: repo, base, head branch, head SHA, checks,
   review status, top-level comments, and inline review comments.
2. Decide the posture before editing: preserve the named PR, rebuild from stale
   source material on current main, or stay read-only.
3. Patch only the scope needed for the current PR claim or the approved rebuild.
4. Run the narrowest checks that cover the changed behavior.
5. Run `neutral-critic` for every PR loop, and request a second independent
   reviewer for every `ariobarin/*` PR. Add any repo-specific gates on top of
   these.
6. After any material push, re-read the head SHA and re-request review on that
   new head before calling the PR ready or merging.
7. Merge only when the user or repo workflow explicitly authorized it.
8. For an explicit closeout request, archive the task after a confirmed merge.
   If the PR cannot merge, leave it open and comment with the blocking evidence.

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
- Local checks do not satisfy review gates. They prove the code path; they do
  not replace reviewer approval.
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

- Use `git-branch-resolver` when branch, worktree, or PR inventory is still
  unclear.
- Use `action-items-to-prs` when review findings or audit items should become
  one or more scoped PR changes.
- Use `orchestration-controller` when the work is mostly review routing,
  monitoring, or completion-gate enforcement.
