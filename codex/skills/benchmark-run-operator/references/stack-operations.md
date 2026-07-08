# Stack Operations Reference

Use this reference for local benchmark stack setup, launch, monitoring, and
pause or recovery.

## Ownership Contract

Every serious run needs explicit ownership:

- Run label.
- Arms: treatment and control.
- Stack shape: isolated or shared.
- Agent repos and commits.
- Compose overlays or stack maps.
- Host port ranges.
- Result roots.
- Worker count.
- Auth directories.
- Browser profile policy.
- Timeout and step cap.
- Cleanup boundary.

Do not reuse another agent's stack unless the user explicitly asks. New stacks
need non-overlapping ports and labels so other agents can avoid touching them.
For a new agent family, prefer a sibling checkout or dedicated worktree and
explicitly document what existing stacks or repos must remain untouched.

## Protocol-First Setup

Before editing or launching:

1. Read the benchmark protocol.
2. Read the nearest launcher or overlay for the same agent family.
3. Read local setup docs and stack procedures.
4. Identify whether the stack is baked-image, bind-mounted, Compose-managed, or
   direct process-managed.
5. Identify what needs rebuild versus restart.

## Known Local Patterns

For WebMCP and WebOperator-style runs:

- Mirror an existing proven overlay before inventing a new one.
- Prefer an active parent command line, launch record, or known-good repair
  script over assumptions from the current checkout name.
- Use a dedicated compose file or stack map.
- Use a dedicated result root and log root.
- Use unique host ports.
- Keep a live `RUN_ERRORS.md` or equivalent scratchpad for dominant failures.
- Prefer a cheap smoke or reduced-task pass before committing to a long full
  run unless the user explicitly wants the full run first.

For OpAgent-style runs:

- Prefer Compose-managed isolated stacks.
- Use stack configs with labels for arm, worker, and site.
- Run `preflight_stack.py` or the harness-equivalent preflight check against
  stack JSON before launch.
- Use `phase_progress.py` or equivalent for progress, row status, max-step rows,
  worker activity, and errors.
- Tune `TaskTimeoutS` deliberately. Slow DGX or remote generation can make the
  default invalid.
- Record timeout in launcher metadata or phase state.

For OSM-heavy stacked services:

- Bike and foot routing services may need memory-pressure mitigation.
- A proven mitigation is `osrm-routed --algorithm mld --mmap --threads 1`.
- Verify map, Nominatim, OSRM, tile server, and Rails health with content-aware
  checks.

## Launch Readiness Checklist

- No competing heavy scheduled tasks or stale worker processes.
- Ports are free and documented.
- Labels are visible in container or task metadata.
- Stack health checks pass.
- Auth probes pass.
- Tool or capability exposure smoke passes.
- Agent and grader model settings are pinned.
- Timeout and step cap are equal across arms.
- Result roots are empty or intentionally resumed.
- Launcher metadata records run label, arms, task set, timeout, model, and stack.
- Derived ports are inside the valid range and every proxy or same-origin
  listener has a live upstream service.
- Child command lines match the intended launcher, label, task slice, and result
  root before rows are treated as countable.

## Monitoring

Report:

- Run label.
- Arms and active phase.
- Stack shape: isolated or shared.
- Ports and stack labels.
- Worker count and active worker processes.
- Result-directory count and growth rate.
- Current valid, invalid, timeout, and max-step counts.
- Dominant exact error strings.
- Whether a heartbeat, wakeup, or other monitor is attached.
- Whether rows are still being produced.
- Observed strict valid-row pace over a named window when deadline pressure
  matters.
- Required strict valid-row pace for any user-stated deadline.

Do not infer completion from one scheduler code. Check scheduled task state,
active workers, child processes, and result-root growth.

Treat idle safe capacity as a diagnostic signal. Step back and identify whether
the idle capacity is safe, owned, comparable, and useful. If independent
single-site tasks, isolated stacks, or disjoint task slices can run without
state collision, name the owner, label the evidence path, and choose whether to
use them.

When one slice fails, step back and classify what is poisoned and what is still
comparable. Stop only the poisoned slice. Keep unrelated arms, sites, workers,
or recovery labels moving only when their evidence remains comparable and
attributable.

If a poisoned child keeps refilling from the same parent, stop the child first
and preserve evidence. Stop the parent only when repeated refills prove the lane
itself is no longer a clean spend path.

## Pause And Cleanup

Pause only the owned run unless the user asks for broader cleanup:

- Disable or stop only scheduled tasks with the run label.
- Stop only containers with the run label.
- Confirm unrelated WebOperator, WebMCP, or benchmark stacks remain untouched.
- Confirm no benchmark Python or browser workers for that run remain.
- Preserve result roots and logs for triage.
- Remove only owned, unused stack residue. For Docker networks, verify zero
  attached containers before removal.
- Record container, process, and result-root evidence before and after cleanup
  when cleanup changes benchmark state.

If infra degradation is producing invalid rows, pause the smallest poisoned
slice before it corrupts provenance or comparability, then diagnose and repair
the cause. Continue healthy comparable work only when continuing will not
corrupt evidence, damage shared state, violate an explicit user stop, or spend
uncontrolled resources. Assume the invalid rows are fixable until protocol
evidence proves otherwise.
