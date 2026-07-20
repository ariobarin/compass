# Benchmark Protocol Reference

Use this reference when setting up, launching, monitoring, or reporting an A/B
benchmark.

## Core Principle

There is one independent variable: the capability under test. Everything else
must be identical between treatment and control:

- Agent build.
- Model endpoint and decoding params.
- Grader and grader params.
- Browser/runtime.
- Task set, order, seed, concurrency, timeout, and step cap.
- Site state and reset policy.
- Auth policy.
- Input guards.

Control should be the same build with the capability off, not a historical
baseline.

## Preflight

1. Confirm no competing heavy jobs, scheduled tasks, stale runners, shared
   browser profiles, shared accounts, or provider quota conflicts.
2. Partition tasks by site, group, mutating flag, read-only flag, auth
   requirements, single-site versus multi-site, and capability coverage.
3. Reset state to a known baseline while preserving expensive caches, indexes,
   and volumes.
4. Run content-aware health gates, not only port checks.
5. Probe auth after reset for each protected service.
6. Smoke one representative task per group.

Smoke must prove:

- Runtime starts.
- Capability is present in the environment.
- Capability surfaces into the agent action surface.
- Agent can invoke it through the real action path.
- Invocation executes.
- Agent perceives the result.
- Preconditions such as auth work.
- Grader returns a verdict.
- With the toggle off, the capability is absent.

## Run Rules

- Same timeout and step cap across arms.
- Same task order and concurrency across arms.
- Version manifest records agent commit, harness commit, service images, browser
  version, model id, decoding params, grader settings, and task revision.
- Give each materially distinct agent, harness, task, scorer, tool-surface,
  environment, and repair identity an evidence epoch or an explicit
  compatibility ruling.
- Reset between arms for mutating tasks.
- Record capability telemetry per task: available, invoked, successful, failed,
  names, args, and return logs.
- Retain prompts, step records, screenshots, per-call usage, and raw results.

## Validity Rules

- Count only rows with terminal artifacts and grader verdicts.
- Separate task failure from infrastructure failure.
- Report invalid, unpaired, unscored, rerun, and rescore rows separately.
- Assign every candidate attempt to an evidence epoch, declare the compatible
  epoch cohort, then select one accepted attempt per cohort, arm, and task
  through a documented deterministic rule before computing comparison sets.
- Headline deltas use the paired valid intersection.
- Token, step, and duration comparisons should include all valid rows and the
  shared-success subset.
- Exploratory one-pass runs are acceptable for signal. Final claims require
  repeated runs and spread.

## Required Outputs

Per task:

- Condition, run id, task id, site, group, mutating flag, auth scope.
- Status, success, raw score, score provenance.
- Artifact path, terminal reason, final URL, steps, wall time.
- Return code, timeout flag, max-step flag.
- Error class and message.

Usage:

- Prompt, completion, cached, and total tokens.
- Model calls, grader calls, endpoint, model id, retry count, request status.

Capability:

- Available flag.
- Availability count.
- Invocation count.
- Success and failure count.
- Tool names, args, returns, and surfacing evidence.

Comparison:

- Paired valid set.
- Unpaired rows.
- Invalid rows.
- Shared-success efficiency.
- Score-source mix.
- Failure-mode summary.
- Reproduction manifest.

## Accepted Confounds To State

- Environment-version skew.
- Historical baseline use.
- Capability coverage gaps.
- Tool-fit gaps.
- Capability exposure gaps.
- State residue.
- Score-source mix.
- Unpaired valid sets.
- Shared session drift.
- Concurrent-run contamination.
- Provider or infrastructure noise.
