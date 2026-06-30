---
name: benchmark-run-operator
description: Run and monitor WebMCP or browser-agent benchmarks. Use for setup, launch gates, monitoring, recovery, and report rebuilds.
---

# benchmark-run-operator

Use this skill when a benchmark run is a live system to operate, not just a
script to start. The run is not trustworthy until the stack, timeout, workers,
artifacts, and comparison set have been verified.

The primary priority is producing the requested result set. Validity rules keep
you from making false claims about results; they are not a reason to stop while
runnable, comparable work is still available. An incident report is incomplete
if safe result-producing work remains.

Front-load the operating doctrine. Any benchmark handoff, runner prompt,
monitor prompt, or status packet must put the non-negotiables in the first
screen: desired result, runner owner, strict contract, active stop conditions,
and current next action. Do not bury this behind history, logs, or caveats. If
only the first 10 lines are read, the agent should still know what result to
produce, who owns execution, and what failure mode to refuse.

Invalid rows can poison headline claims, but they do not poison continued
collection. Treat them as a recovery queue: classify them, preserve evidence,
rerun or rescore what can be recovered, and keep healthy slices moving whenever
continuing will not corrupt comparability or shared state. Do not freeze a
healthy arm, site, worker, or stack just because one row is invalid.

Recoverable invalid rows are work, not caveats. Investigate them until each one is
countable, intentionally rerun, cleanly rescored, or proven nonrecoverable under
the benchmark protocol. Use safe idle capacity. Do not let safe isolated
workers, single-site stacks, or disjoint task slices sit idle while one invalid
row is being diagnosed, unless you have a recorded protocol reason that
parallel work would poison the comparison.

A blocker claim needs evidence. Exhaust the local moves first:
continue unaffected slices, isolate the failing slice, rerun only affected task
ids, rescore terminal artifacts, switch to a clearly linked recovery label, or
write a provenance map that lets original and recovery rows aggregate cleanly.
Only then call for a user decision.

For long runs, split controller and runner ownership. The parent orchestrator
should create or route to a runner thread or worker that owns the shell process,
live logs, local recovery, and artifact preservation. The parent stays above the
run: it defines the contract, checks evidence, reroutes failures, keeps monitors
alive, and tests blocker claims. Do not let the orchestrator sit inside the
long-running execution loop and then mistake local loop state for judgment.

For a new agent family or fresh integration, treat the work as onboarding first
and run operation second. Read the upstream repo and nearest local launcher
before inventing local glue.

## Required References

Read the references that match the task:

- [benchmark-protocol.md](references/benchmark-protocol.md): comparison design,
  A/B validity, smoke gates, success metrics, and accepted confounds.
- [stack-operations.md](references/stack-operations.md): stack ownership,
  labels, ports, timeouts, OpAgent/WebOperator patterns, OSM resource pressure,
  and monitoring commands.
- [artifact-validation.md](references/artifact-validation.md): result-row
  validity, error taxonomy, missing-task recovery, final aggregation, and report
  outputs.
- [report-rebuild.md](references/report-rebuild.md): rebuilding report roots,
  preserving local style, shared-success comparisons, and final count checks.

## Operating Loop

1. Read the protocol and nearest prior launcher before changing or launching
   anything.
2. If this is a new agent family or fresh integration, read the upstream repo,
   local setup docs, and current benchmark notes before deciding where the
   benchmark glue should live.
3. Declare run ownership: label, arms, ports, result roots, workers, task set,
   model settings, timeout, cleanup boundary, and whether the stack is isolated
   or shared.
4. For any long or expensive run, assign a runner owner before launch. Use a
   separate durable thread when the run may outlive the current turn, needs its
   own heartbeat, or benefits from user-visible continuity. Use a subagent only
   for bounded same-session slices. The controller keeps parent completion
   authority.
5. Prefer a sibling checkout or dedicated worktree for a new agent stack, and
   do not mix new experiments into existing agent worktrees unless the user
   explicitly asked for a shared setup.
6. Run content-aware health checks and a smoke task before spending a long run.
   Prefer a cheap smoke or reduced-task pass before an expensive full launch
   unless the user explicitly wants the direct long run.
7. Monitor worker state, result-root growth, exact error clusters, and scheduler
   state while it runs.
8. If invalid rows are accumulating, pause only the affected label, slice, site,
   or stack, then immediately debug why the rows are invalid. Keep healthy
   comparable work moving.
9. Treat missing, invalid, or unscored rows as a recovery queue until they are
   classified as countable, recoverable, or protocol-unsafe to retry.
10. Count results only after terminal artifacts exist and final aggregation has
   been rebuilt. Until then, keep producing artifacts rather than polishing
   explanations for why the run stopped.
11. If the user needs a refreshed report or comparison CSVs, rebuild them from
   the canonical final artifacts instead of mixing raw rerun directories and
   ad hoc counts.

## Output

Report the run label, arms, stack shape, ports, labels, timeout, stack health,
active workers, result-root status, dominant error clusters, whether a monitor
or heartbeat is attached, and the next action. For completed runs, include the
valid paired comparison set, invalid or missing rows, and the commands or
artifacts used as evidence. For new-agent bring-up, also report the checkout or
worktree path, ownership boundary, chosen ports, smoke evidence, and what
remains isolated from existing stacks. When a final report was rebuilt, include
the canonical inputs, refreshed report root, and exact count checks used to
verify it.
