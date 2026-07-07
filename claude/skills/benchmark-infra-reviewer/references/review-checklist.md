# Benchmark Infra Review Checklist

Use this checklist to review benchmark-management diffs consistently without
re-running the whole benchmark.

## Scope And Evidence

- Read the actual diff plus any untracked benchmark docs the user says will be
  staged with the PR.
- Treat user-provided validation output as evidence to cross-check, not as a
  substitute for reading the touched files.
- Keep the review read-only unless the user explicitly asks for edits or live
  reruns.

## Target Docs And Time-Sensitive Claims

- Benchmark target docs should name the target set, the exact denominator, and
  the verification date or snapshot.
- Runbooks and README examples should match the code's real defaults and
  accepted flag values.
- Modification ledgers should describe benchmark-affecting changes without
  stale "current" claims or unverified freshness language.

## Projection And Telemetry Semantics

- Top-level publication projections for wall time, usage, cost, or completion
  should use attempted task rows or another explicitly operational denominator.
- Valid-only or scoreable-only projections should stay in a separately labeled
  nested object, not replace the operational projection.
- Usage-efficiency claims should require real usage artifacts plus schema
  completeness checks, not guessed totals from partial rows.
- If a repo intentionally treats timeout `0` as "no timeout", parser changes
  must preserve that behavior.

## Validation And Diff Scope

- Tests should cover the changed parser, projection, telemetry, or report
  semantics.
- Doc-only claims that depend on code behavior should still be checked against
  the implementation.
- Flag unrelated churn, stale generated outputs, or speculative cleanup that is
  not required for the benchmark-management goal.
