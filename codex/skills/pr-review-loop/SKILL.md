---
name: pr-review-loop
description: Iterate on a named PR through review, fixes, re-review, and merge gates. Use when the user names a PR, asks to address review comments, or wants dual review.
---

# PR Review Loop

Use this skill when the center of gravity is a pull request, not just a branch
or a code change. The job is to keep PR identity, review gates, current-head
state, and merge authority explicit from first inspection through final ready
state.

This skill covers two common postures:

- iterate on the exact PR or branch the user named;
- rebuild a stale PR from source material when the user wants current-main work
  rather than preserving the old PR identity.

## Required Reference

Read [review-loop-playbook.md](references/review-loop-playbook.md) for named-PR,
stale-rebuild, re-review, and merge-boundary patterns.

## Loop

1. Inspect the live PR state first: repo, base, head branch, head SHA, checks,
   review status, and open comments.
2. Decide the posture before editing: preserve the named PR, rebuild from stale
   source material on current main, or stay read-only.
3. Patch only the scope needed for the current PR claim or the approved rebuild.
4. Run the narrowest checks that cover the changed behavior.
5. Request or run the required review paths.
6. After any material push, re-read the head SHA and re-request review on that
   new head before calling the PR ready.
7. Merge only when the user or repo workflow explicitly authorized it.

## Rules

- If the user names a specific PR or branch, do not quietly redirect to a new
  PR unless they ask for a rebuild or branch surgery.
- If the user wants current-main work and the old PR is stale, treat the old PR
  as source material only and rebuild cleanly on current main.
- If `@codex` and `neutral-critic` are both required, do not claim readiness
  until both current-head reviews are green or the remaining blocker is
  explicit.
- If review is silent, use the approved fallback path rather than waiting
  passively.
- If the user performs merges, stop at merge boundary with the exact next merge
  action.
- If a base branch moved, re-check whether downstream PRs still have a real
  delta before keeping them alive.

## Related Skills

- Use `git-branch-resolver` when branch, worktree, or PR inventory is still
  unclear.
- Use `action-items-to-prs` when review findings or audit items should become
  one or more scoped PR changes.
- Use `orchestration-controller` when the work is mostly review routing,
  monitoring, or completion-gate enforcement.
