---
name: pr-review-loop
description: Drive a named PR through current-head checks, independent review, behavior validation, fixes, and merge gates.
---

# PR Review Loop

Use this skill when a pull request must move through evidence and review without
losing branch identity or current-head discipline.

Read [review-loop-playbook.md](references/review-loop-playbook.md) for review
bundles, source-blind validation, stale-head handling, and merge boundaries.

## Start With The Named PR

Record:

- repository, PR number, base branch, head branch, and head SHA;
- current checks, review decision, inline findings, and merge state;
- whether the user asked to preserve this PR or rebuild from current main.

Keep the exact branch and PR unless the user explicitly asks for replacement,
retargeting, or cleanup.

## Required Gates

- `neutral-critic` reviews every PR loop.
- Any `ariobarin/*` repository also requires a second independent reviewer.
- Observable behavior changes require a separate source-blind
  `behavior-validator` result.
- All conclusions are tied to the current head SHA.

A local test supports readiness but does not replace an independent gate.

## Iteration

1. Inspect the current PR and inline comments.
2. Run the narrow checks that prove the changed surfaces.
3. Request or perform source-aware review on the current head.
4. Route actionable findings to the implementation owner.
5. Re-run checks after each material push.
6. Re-read the head SHA and refresh stale review gates.
7. Run source-blind behavior validation for observable changes.
8. Stop at the authorized merge boundary.

Use `scripts/build-review-bundle.py` when a fresh reviewer should receive the
complete selected patch without arbitrary checkout context.

## Waiting For Review

After review acknowledgement, use `monitor-to-completion` to wait on the actual
review, comment, or check state. Choose a bounded timeout from the repository
review expectation, user deadline, or explicit service window. Do not use a
fixed clock sleep or repeated model polling.

On timeout, re-read the head SHA, checks, reviews, and comments once. Then
reroute to an authorized alternate reviewer, report the pending gate, or choose
a new evidence-based wait. Do not treat timeout as approval.

## Completion

Report the current head SHA, checks, review gates, behavior gate, unresolved
findings, and merge authority. Merge only when explicitly authorized. If a
required gate is pending, leave the PR open and name the exact gate.
