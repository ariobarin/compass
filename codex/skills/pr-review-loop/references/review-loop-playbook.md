# PR Review Loop Playbook

Use this reference when PR work needs explicit branch identity, review gates,
current-head re-review, or stale-PR rebuild handling.

## Standing Review Gates

`neutral-critic` is mandatory for every PR review loop. For any `ariobarin/*`
repository, a second independent reviewer is also mandatory. These are
readiness gates, not nice-to-have checks.

Do not mark a PR ready or merge it while a required review gate is missing,
stale, failed, or still waiting on actionable findings. A local test run can
support the case for readiness, but it never replaces reviewer approval.

## Named PR Loop

When the user names a specific PR or branch:

1. Inspect the live PR first with `gh pr view` or equivalent, and inspect inline
   review comments separately.
2. Record base branch, head branch, head SHA, review state, inline findings,
   and checks.
3. Keep the exact PR identity unless the user explicitly asks for a rebuild,
   retarget, or replacement branch.
4. Re-run the same live checks after each material push.

Useful fields:

- `headRefName`
- `headRefOid`
- `baseRefName`
- `reviewDecision`
- `mergeStateStatus`
- `statusCheckRollup`
- inline review comments, such as GitHub pull review comments

## Current-Head Discipline

Review conclusions are tied to a head SHA, not just a PR number.

- After a push, force-push, rebase, or retarget, re-read the head SHA.
- Re-request the second reviewer or other required review on the new head when
  the old review may be stale.
- Do not call a PR ready based on feedback that clearly targeted an older head.

## Stale PR Rebuild

Use rebuild posture when the user wants current-main work rather than the old
PR identity.

- Inspect the old PR branch for source material, not as something to merge
  wholesale.
- Start a fresh branch or worktree from current `origin/main`.
- Reapply only the still-relevant intent.
- Open a new PR when the rebuilt work is no longer truthfully the same old PR.

Preserve exact PR identity only when the user asked to keep iterating that PR.

## Dual Review Gates

When both a second reviewer and `neutral-critic` apply:

- treat both as blocking gates;
- route actionable findings back through the implementation path;
- after fixes, re-run the narrow checks and re-request review on the new head;
- if one reviewer is silent and an alternate route is authorized, use that
  route explicitly and report which gate remains unsatisfied.

## Merge Boundary

- If the user merges, stop at review-ready state and say exactly what remains:
  PR number, head SHA, check state, and review state.
- Merge only when the user or repo workflow explicitly authorized it.
- For an explicit merge-closeout request, archive the task only after GitHub
  confirms the merge. If a required gate fails or remains pending, leave the PR
  open and comment with the blocking evidence or actionable finding.
- If a stack is involved, name the merge order instead of assuming a reviewer
  can infer it.

## Output

Report:

- repo and PR number;
- base branch, head branch, and current head SHA;
- whether PR identity was preserved or rebuilt;
- checks run and their result;
- review gates requested, satisfied, or still pending;
- whether the task stopped at merge boundary or completed with an authorized
  merge.
