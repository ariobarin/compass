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
- No ancestor directory, sibling marker, task log, or launcher log marks the row
  as excluded from strict counts.
- Related task logs have been checked for missing-tool, wrong-route, timeout,
  traceback, bad-parameter, connection, auth, or forced-stop evidence.
- The row belongs to the intended run label and arm.
- The row is de-duplicated by the intended unit, usually arm plus task id, not by
  raw file count.

For WebOperator-style result directories, do not count a task until
`summary_info.json` exists.

A clean zero-reward or max-step terminal row can be a valid task failure. A row
with infrastructure poison is invalid recovery work even when a terminal
summary exists.

## Accepted Attempt Selection

Inventory candidate attempts from every attributable original, rerun, rescore,
and manual-classification root. Assign every candidate to an evidence epoch
before selection, then declare the compatible epoch cohort for the comparison.
Select at most one accepted attempt per cohort, arm, and task through a rule
fixed before inspecting the desired outcome. Never collapse attempts across
incompatible epochs.

The benchmark contract owns the rule. A recovery run may use earliest valid by
recorded start time, an explicit generation order, or another deterministic
precedence that matches the harness. Do not let a later success replace an
earlier valid failure merely because it improves the result.

Preserve an excluded-attempt ledger with the candidate and parent-attempt
identities, epoch and cohort, selection reason, validity classification,
provenance, and artifact locator. Invalid or superseded attempts remain
operational evidence and token overhead when the report contract calls for
them, but they do not become accepted task rows.

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
- Missing tool or wrong route.
- Bad parameter.
- Forced stop after user pause.
- Launch failure before task execution.

Filter progress-only lines before sampling logs.

Keep invalid categories descriptive until a target report adopts final names.
The important split is whether the row is a valid task failure, recoverable
infrastructure failure, failed launch, forced interruption, unscored terminal
artifact, or protocol-unsafe rerun candidate.

## Missing-Task Recovery

When top-up or missing-task recovery is needed:

1. Compute missing ids from expected task set minus valid terminal artifacts.
2. Run one missing task or a small controlled batch.
3. Capture child stdout and stderr.
4. Clean stale wrappers, parents, and child processes between probes.
5. Mark rows by provenance: original, rerun, rescore, or manual classification.
6. Re-run final aggregation after recovery.

Missing or recoverable invalid rows are not presentation caveats until they have
been prosecuted. Recover them with controlled reruns, rescoring, or
classification until each remaining gap has a concrete nonrecoverable reason.
Assume the row is fixable until the artifact, scorer, stack, or protocol
evidence proves otherwise.

Do not let invalid or missing rows become a tidy excuse for stopping. They are a
worklist. If the user asked for results, the default response is to keep
producing terminal artifacts for every unaffected comparable task while the bad
rows are investigated. A blocker report is not a result set.

Timeouts, provider refusals, missing summaries, and scorer errors are result
artifacts or recovery candidates first. Treat them as benchmark-ending only
after affected-task reruns, rescoring, provenance separation, or safe parallel
collection have been tried or proven protocol-unsafe.

Avoid overlapping bulk wrappers. They make state and attribution unclear.

## Final Aggregation

Before reporting:

- Re-run the canonical aggregation script or notebook.
- If the user needs refreshed report artifacts or comparison CSVs, also read
  `report-rebuild.md`.
- Assign candidate epochs, declare a compatible cohort, and apply the documented
  accepted-attempt selector before computing result sets.
- Verify denominators after recovery.
- Build paired valid intersections.
- Separate invalid, unpaired, unscored, rerun, and rescore rows.
- Rebuild final CSVs and summaries from the current artifacts.
- Spot-check that top-line numbers match source rows.
- Name the denominator unit before reporting a headline. Raw file count, copied
  summary count, task-attempt count, valid task count, and paired arm-task count
  can all differ.

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
