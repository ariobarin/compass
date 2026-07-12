# PR Review Loop Playbook

Use this reference when PR work needs explicit branch identity, review gates,
current-head re-review, source-aware bundle isolation, source-blind behavior
proof, or stale-PR rebuild handling.

## Standing Review Gates

`neutral-critic` is mandatory for every PR review loop. For any `ariobarin/*`
repository, a second independent reviewer is also mandatory. These are
readiness gates, not nice-to-have checks.

Do not mark a PR ready or merge it while a required review gate is missing,
stale, failed, or still waiting on actionable findings. A local test run can
support the case for readiness, but it never replaces reviewer approval.

When a PR changes observable behavior, add a separate `behavior-validator` gate.
A source-aware reviewer judges the implementation and patch. A source-blind
validator judges the running product, command, API, or artifact against a
written behavior contract. Neither gate substitutes for the other.

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
- Behavior evidence must identify the tested build, ref, or artifact. A passing
  result for an older build does not clear the current head.

## Confined Source-Aware Review

Use the bundled `scripts/build-review-bundle.py` when a fresh reviewer should
see the complete selected patch without inheriting the current conversation or
arbitrary checkout files.

The bundle contains:

- the complete binary-capable Git patch for the selected base and head;
- base and head SHAs plus changed paths and hashes in `manifest.json`;
- an optional repo-relative task file;
- only explicitly selected repo-relative datasets.

The helper deliberately refuses:

- dirty worktrees, because uncommitted material would be omitted;
- empty or oversized patches;
- known secret and credential paths or secret-like content;
- symlinked, absolute, or escaping context paths;
- existing output directories that could contain stale evidence.

Treat a bundle failure as an evidence-boundary failure. Redact or divide the
change and build complete bundles for the resulting claims. Do not paste a
truncated diff and call it equivalent.

## Source-Blind Behavior Validation

Capture the behavior contract before implementation detail can redefine success.
Give the validator only:

- the behavior contract;
- exact target identity and launch or connection instructions;
- allowed fixtures and credentials through approved secret handling;
- user-visible or operator-visible evidence.

Do not provide source, diffs, tests, Git history, review summaries, or a review
bundle. If those become visible, the run is contaminated and a fresh validator
must rerun it. Require clause-level pass, fail, blocked, or out-of-scope status,
plus anti-cheat probes that distinguish real behavior from static success text.

Skip this gate only when the PR makes no user-visible or operator-visible
behavior claim, such as a prose-only maintainer note or an internal refactor
whose observable contract is intentionally unchanged.

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
- finish `neutral-critic`, resolve its findings, and get a green current-head
  result before requesting the second review, unless the user explicitly
  requires parallel reviews;
- when the second-review request receives an `eyes` reaction, treat it as
  acknowledged, wait one bounded five-minute interval, then refresh reviews
  and comments once instead of polling during the interval;
- route actionable findings back through the implementation path;
- after fixes, re-run the narrow checks and re-request review on the new head;
- if one reviewer is silent and an alternate route is authorized, use that
  route explicitly and report which gate remains unsatisfied.

## Merge Boundary

- If the user merges, stop at review-ready state and say exactly what remains:
  PR number, head SHA, check state, review state, and behavior gate state.
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
- source-aware review gates requested, satisfied, or still pending;
- behavior contract and clause totals when observable behavior changed;
- whether the task stopped at merge boundary or completed with an authorized
  merge.
