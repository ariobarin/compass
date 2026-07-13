---
name: benchmark-run-operator
description: Run and monitor WebMCP or browser-agent benchmarks. Use for setup, launch gates, monitoring, recovery, and report rebuilds.
---

# benchmark-run-operator

Use this skill when a benchmark run is a live system to operate, not just a
script to start. The run is not trustworthy until the stack, timeout, workers,
artifacts, and comparison set have been verified.

The priority is producing the requested result set with valid provenance.
Validity rules keep reports honest and guide whether the next route should be
continue, pause, repair, rerun, rescore, reroute, or ask for authority. A status
packet is not a substitute for that route decision.

Treat the run ledger as a control surface. Before touching processes, stacks,
counts, or reports, read the latest authoritative status file or handoff and
compare it against live evidence. After acting, update the ledger with the
current strict counts, owned workers, poisoned slices, artifact roots, and next
action. If old sections can be mistaken for current state, fix the latest-state
shape before launching more work.

Account for authorized production capacity at every controller checkpoint.
Classify each stack or lane as counted work, immediate staging, deliberate
reserve, blocked with named evidence and owner, or justified idle. Unexplained
safe idle capacity is a controller defect. Fill conflict-free capacity with
attributable work, including independent single-site tasks or disjoint repair
slices, without crossing a user hold, provenance, isolation, comparability,
ownership, or spend boundary.

Front-load the operating doctrine. Any benchmark handoff, runner prompt,
monitor prompt, or status packet must put the non-negotiables in the first
screen: desired result, runner owner, strict contract, active stop conditions,
and current next action. Do not bury this behind history, logs, or caveats. If
only the first 10 lines are read, the agent should still know what result to
produce, who owns execution, and what risk to diagnose.

Invalid rows are poisonous to headline claims. Treat them as a diagnostic
signal and recovery queue: classify them, preserve evidence, identify the
poisoned label, rerun or rescore what can be recovered, and decide whether
healthy slices can continue without corrupting comparability or shared state.

Recoverable invalid rows are work, not caveats. Work them until each one is
countable, intentionally rerun, cleanly rescored, or proven nonrecoverable under
the benchmark protocol. Idle safe capacity is a signal to inspect. Use safe
isolated workers, single-site stacks, or disjoint task slices only when they
have clear ownership, comparable provenance, and no state collision with the
diagnosis underway.

Treat an alleged blocker as a diagnosis request. Step back and name the failed
action, current state, owner, evidence, local recovery tried, smallest
reversible move, and any external decision that truly prevents progress.
Continue unaffected slices, isolate the failing slice, rerun affected task ids,
rescore terminal artifacts, switch to a clearly linked recovery label, or write
a provenance map only after that route is safe and attributable.

Treat launch-hold packets as hard no-launch states. If the user asks for a
`READY_TO_LAUNCH_*_HOLD` packet or names an equivalent hold state, stop at the
packet. Do not launch full arms, canaries, Docker stack changes, or injectors
unless the user reopens launch authority. The packet should name the gate
checklist, stop conditions, monitor cadence, status-path pattern, owned roots,
and exact action that would release the hold.

Report pace truthfully. When the user names a deadline or asks whether the run
is on track, compute strict valid-row pace over a named window and the required
pace to meet the target. Do not call a run healthy just because rows are still
arriving. If the rate math is impossible, say so and keep driving the next
valid local action.

For long runs, split controller and runner ownership. The parent orchestrator
should create or route to a runner thread or worker that owns the shell process,
live logs, local recovery, and artifact preservation. The parent stays above the
run: it defines the contract, checks evidence, reroutes failures, keeps monitors
alive, and diagnoses blocker claims. Do not let the orchestrator sit inside the
long-running execution loop and then mistake local fatigue for judgment.

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
2. Read the latest run ledger or handoff and verify it against live processes,
   stack state, result roots, and terminal artifacts before changing anything.
3. If this is a new agent family or fresh integration, read the upstream repo,
   local setup docs, and current benchmark notes before deciding where the
   benchmark glue should live.
4. Declare run ownership: label, arms, ports, result roots, workers, task set,
   model settings, timeout, cleanup boundary, and whether the stack is isolated
   or shared.
5. For any long or expensive run, assign a runner owner before launch. Use a
   separate durable thread when the run may outlive the current turn, needs its
   own heartbeat, or benefits from user-visible continuity. Use a subagent only
   for bounded same-session slices. The controller keeps parent completion
   authority.
6. Prefer a sibling checkout or dedicated worktree for a new agent stack, and
   do not mix new experiments into existing agent worktrees unless the user
   explicitly asked for a shared setup.
7. Run content-aware health checks and a smoke task before spending a long run.
   Prefer a cheap smoke or reduced-task pass before an expensive full launch
   unless the user explicitly wants the direct long run.
8. Monitor worker state, result-root growth, exact error clusters, and scheduler
   state while it runs.
9. If invalid rows are accumulating, pause only the poisoned label, slice, site,
   or stack, then debug why the rows are invalid. Continue healthy comparable
   work only when provenance remains clean.
10. Treat missing, invalid, or unscored rows as a recovery queue until they are
   classified as countable, recoverable, or protocol-unsafe to retry.
11. Count results only after terminal artifacts exist and final aggregation has
   been rebuilt. Until then, keep producing artifacts rather than polishing
   explanations for why the run stopped.
12. If the user needs a refreshed report or comparison CSVs, rebuild them from
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
