# Log And Artifact Triage

Use this reference to decide whether a run produced valid evidence.

## Evidence To Gather

- Task definition and eval definition.
- Browser logs, tool logs, and runner logs.
- Step records or action records.
- Tool catalog and invocation records.
- Tool return value.
- Final URL and screenshot if present.
- Result directory contents.
- Terminal summary artifact.
- Grader verdict and raw score.
- Worker process state and scheduler state for active runs.

## Error Grouping

Group by exact error strings after filtering progress-only lines. Normalize task
sorting so `task_100` does not appear before `task_2`.

Common clusters:

- `KeyError: 'text'`: action-shape or parser drift.
- `Unsupported function call`: executor/tool-call mismatch.
- `No valid function call found`: model or parser did not produce a valid action.
- `Locator.fill: Timeout 10000ms exceeded`: UI locator, auth, or page-state
  mismatch.
- `Page.goto: net::ERR_CONNECTION_REFUSED`: stack or port failure.
- `ERR_EMPTY_RESPONSE`: unhealthy service or restart.
- Login timeouts: stale auth, cookie-domain mismatch, or wrong stack port.
- Progress-only lines such as evaluator progress bars: noise, not failure class.

## Valid Row Rules

A row is valid only when:

- The runner produced a terminal artifact.
- The grader returned a verdict or exact checker result.
- There is no uncaught crash, stale-runner marker, missing-summary gap, or known
  infra marker.
- The result directory has the expected summary file for that harness, such as
  `summary_info.json`.

Do not count partial directories, missing summaries, or silent exits as valid
task attempts.

## Active Run Checks

Do not treat a quiet terminal or scheduler result code as completion proof.
Check:

- Scheduled task state.
- Active worker processes.
- Browser or runner child processes.
- Result-directory growth.
- Worker logs.
- Error-rate trend.
- Stack health and content checks.

If invalid rows are accumulating, pause the smallest poisoned labeled slice
before it corrupts provenance or comparability, then immediately debug why the
rows are invalid. Do not stop unrelated healthy work just to make the situation
feel clean. Keep collecting terminal artifacts wherever the task set, stack
state, scorer configuration, and provenance remain comparable. Assume invalid
rows are fixable until protocol evidence proves otherwise.

Monitor errors are alarms, not verdicts. They demand classification and a next
productive action. They do not, by themselves, justify giving up on the requested
result set.

## Missing-Task Recovery

When recovering missing rows:

- Run one task or a very small controlled batch.
- Capture child stdout and stderr.
- Clean stale parent and child processes between probes.
- Count a task only after the terminal summary artifact exists.
- Rebuild final aggregates after recovery.
- Record which rows are original, rerun, rescore, or manually classified.

Recovery should overshoot toward motion. If several independent single-site
rows are missing and safe stacks exist, run disjoint slices in tandem with clear
labels and provenance instead of serializing everything behind one bad row.

## Output Pattern

For each cluster:

- Task ids.
- Site or tool family.
- Exact error.
- Bucket: tool, eval, agent, infra, or long-run drift.
- Evidence path or artifact description.
- Recommended owner.
- Whether to continue, pause, rerun, rescore, or patch.
