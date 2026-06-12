# Artifact Validation Reference

Use this reference before declaring a benchmark run complete or publishing
comparison results.

## Valid Result Criteria

A task result is countable only when:

- The result directory or row exists.
- The expected terminal summary artifact exists.
- The grader or exact checker returned a verdict.
- The runner did not crash.
- There is no stale-runner marker.
- There is no known infra marker making the row invalid.
- The row belongs to the intended run label and arm.

For WebOperator-style result directories, do not count a task until
`summary_info.json` exists.

## Error Taxonomy

Maintain an error taxonomy during long runs instead of waiting for final
aggregation.

Group by exact strings such as:

- `KeyError: 'text'`.
- `Unsupported function call`.
- `No valid function call found`.
- `Locator.fill: Timeout 10000ms exceeded`.
- `Page.goto: net::ERR_CONNECTION_REFUSED`.
- `ERR_EMPTY_RESPONSE`.
- Login timeout.
- Max steps.
- Task timeout.
- Grader failure.

Filter progress-only lines before sampling logs.

## Missing-Task Recovery

When top-up or missing-task recovery is needed:

1. Compute missing ids from expected task set minus valid terminal artifacts.
2. Run one missing task or a small controlled batch.
3. Capture child stdout and stderr.
4. Clean stale wrappers, parents, and child processes between probes.
5. Mark rows by provenance: original, rerun, rescore, or manual classification.
6. Re-run final aggregation after recovery.

Avoid overlapping bulk wrappers. They make state and attribution unclear.

## Final Aggregation

Before reporting:

- Re-run the canonical aggregation script or notebook.
- If the user needs refreshed report artifacts or comparison CSVs, also read
  `report-rebuild.md`.
- Verify denominators after recovery.
- Build paired valid intersections.
- Separate invalid, unpaired, unscored, rerun, and rescore rows.
- Rebuild final CSVs and summaries from the current artifacts.
- Spot-check that top-line numbers match source rows.

## Report Shape

Include:

- Run label and arms.
- Result roots.
- Task counts by valid, invalid, unscored, and missing.
- Paired valid set size.
- Pass rate by arm.
- Paired delta.
- Token, step, and duration totals.
- Shared-success efficiency.
- Dominant failure clusters.
- Score-source mix.
- Commands or artifacts used to verify completion.

If a live CLI resume path is broken, saved local session artifacts and result
directories can be the durable source, but say that the answer is artifact based.
