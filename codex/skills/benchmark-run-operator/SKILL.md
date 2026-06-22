---
name: benchmark-run-operator
description: Run and monitor WebMCP or browser-agent benchmarks. Use for setup, launch gates, monitoring, recovery, and report rebuilds.
---

# benchmark-run-operator

Use this skill when a benchmark run is a live system to operate, not just a
script to start. The run is not trustworthy until the stack, timeout, workers,
artifacts, and comparison set have been verified.

Invalid rows are not harmless progress. They are contamination until classified.
When they accumulate, preserve evidence, stop only the labeled failing slice,
repair what can be repaired, and keep healthy slices moving only when the
comparison remains valid.

For a new agent family or fresh integration, treat the work as onboarding first
and run operation second. Read the upstream repo and nearest local launcher
before inventing local glue.

## Required References

Read the references that match the task:

- [benchmark-protocol.md](references/benchmark-protocol.md): comparison design,
  A/B validity, smoke gates, success metrics, and accepted confounds.
- [stack-operations.md](references/stack-operations.md): stack ownership,
  labels, ports, timeouts, OpAgent/WebOperator patterns, OSM pressure, and
  monitoring commands.
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
4. Prefer a sibling checkout or dedicated worktree for a new agent stack, and
   do not mix new experiments into existing agent worktrees unless the user
   explicitly asked for a shared setup.
5. Run content-aware health checks and a smoke task before spending a long run.
   Prefer a cheap smoke or reduced-task pass before an expensive full launch
   unless the user explicitly wants the direct long run.
6. Monitor worker state, result-root growth, exact error clusters, and scheduler
   state while it runs.
7. Pause only the labeled stack if invalid rows are accumulating.
8. Count results only after terminal artifacts exist and final aggregation has
   been rebuilt.
9. If the user needs a refreshed report or comparison CSVs, rebuild them from
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
