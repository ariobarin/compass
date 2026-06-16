---
name: benchmark-infra-reviewer
description: Skeptical review of benchmark-management and publication diffs before PR. Use for docs, runbooks, telemetry, summarizers, launch controls, and target notes.
---

# benchmark-infra-reviewer

Use this skill to review benchmark-management diffs before publication or PR.
Default to read-only review. Do not launch benchmarks, smokes, resets, or
other commands that create result rows unless the user explicitly asks.

## Required References

Read [review-checklist.md](references/review-checklist.md) before giving a
final verdict.

## Review Loop

1. Read the nearest `AGENTS.md`, repo overview, and any benchmark docs that the
   diff touches.
2. Inspect the working tree, including untracked benchmark docs or report
   artifacts that the PR is expected to include.
3. Bucket the change: target docs, runbook or README text, publication-summary
   code, runner defaults, usage telemetry, or tests.
4. Check time-sensitive claims. Counts, limits, evidence status, and benchmark
   scope should be dated or tied to a verified snapshot in the same run.
5. Check publication semantics. Operational duration, token, or cost
   projections should scale from attempted rows or another explicitly named
   operational denominator. Valid-only projections should stay nested and
   labeled as scoreable or valid subsets.
6. Check launch and parser controls. Standardized flags such as `--max-steps`
   and timeout parsing should preserve the repo's intended semantics, including
   any deliberate zero-timeout behavior.
7. Check validation and scope. Tests should cover the changed semantics, and
   the diff should stay scoped to the benchmark-management items under review.

## Output

Return findings first, ordered by severity, with concrete file and line
references when possible. If the diff is good enough to proceed, say so
explicitly and list only residual risks, unchecked areas, or tests you could
not verify.
