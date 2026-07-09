# Benchmark Run Learnings

Status: repo-local candidate notes. Do not install this file as runtime
agent behavior without a separate promotion pass.

Source: reviewed benchmark operations evidence summarized in this document and
the companion evidence extract.

Scope: lessons from the A3 Qwen3.5 9B five-arm WebArena benchmark thread.
The thread started as launch preparation, then became a multi-day live
benchmark operation with monitors, repairs, status-led restarts, and a hard
pause. The exact A3 labels, task ids, artifact roots, and local ports belong to
the benchmark repo and run records. The Compass-worthy material is the
operating discipline that kept the run evidence reviewable.

## What Is Worth Keeping

The thread shows that a benchmark run is a live system, not a command. The most
useful behavior was not any one launcher. It was the repeated loop:

1. Read the controlling status ledger first.
2. Verify live state from processes, Docker, endpoints, task attempts, logs,
   and terminal artifacts.
3. Classify fresh rows before changing counts.
4. Convert invalid rows into repair work or explicit exclusions.
5. Stop only the owned poisoned slice.
6. Write the status ledger with the decision already acted upon.

That loop is already close to the `benchmark-run-operator` stance, but the
thread makes several failure modes concrete enough to consider for future
Compass updates.

## Thread Phases

### Launch Framing

The first useful artifact was a launch-gate draft for a five-arm A3 9B run.
It forced the work to name the agent, model, task set, arms, independent
variable, smoke gates, monitor contract, and launch packet before a full run.
That phase matters because it separates an expensive benchmark from an eager
script launch.

The important Compass lesson is not the A3-specific arm list. The reusable
lesson is that expensive benchmark work needs an up-front contract with a
kill switch. Smoke is not a demo. Smoke is the evidence gate that decides
whether the full spend is allowed.

### Full Authority And Goal Activation

The user later gave full authority and explicitly said there were no real
blockers. The useful response was to create or continue active goal state,
read the run contract, and start acting on the smallest valid next move. Full
authority did not remove the obligation to verify. It removed the excuse to
wait for vague permission.

For Compass, this strengthens the link between `using-codex-goals` and
benchmark operation: a long benchmark needs a durable completion predicate,
but the controller still has to keep local action pressure on any repairable
row.

### Count Correction

The run initially had optimistic or stale count sections. Later scans found
completed rows with exact missing-tool poison, timeout rows without markers,
and duplicate or nested summary shapes. The useful move was to tighten the
strict denominator, mark poisoned artifacts, and accept the lower count.

This phase is the strongest evidence for future artifact-validation guidance.
The truthful answer may be numerically worse after deeper validation. That is
still progress because it makes the final claim defensible.

### Repair Operation

Most of the thread was repair work. Repairs were useful when they were small,
owned, labeled, and attributable. Bad repairs were marked at the root or task
path, then excluded from aggregation. Good repairs reused known launcher
patterns and verified child command lines before being treated as live.

The durable lesson is that repair work needs provenance as much as the original
run. A replacement row without a clear label, root, launcher, and count rule is
just another ambiguity.

### Throughput And Deadline Truth

The benchmark kept missing the user's desired time horizon. The operator
eventually answered with exact valid-row pace and required-row pace instead of
optimistic language. It also held below the maximum lane count when model
latency was the bottleneck.

This should inform status output guidance. A status packet should not say a run
is "on track" or "moving" when simple rate math proves the requested completion
time is impossible. It should state the rate gap and the action already taken.

### Pause And Resume

The thread ended with an explicit pause, forced-stop artifacts, monitor cleanup,
and then a later discussion about the decisions that mattered. This exposed a
gap in durable goal semantics: pausing execution is not the same as completing
the benchmark objective, but monitors must not restart work after a user pause.

This phase should not be promoted as "mark paused work complete." It should be
promoted as a design problem: installed goal guidance needs a clear pause
pattern that preserves resume state, disables automation, and avoids false
completion claims.

## Durable Patterns

### Status Ledger First

The run became manageable only when `RUN_STATUS.md` was treated as the control
surface. Each continuation read it before touching workers, then compared it
against live evidence. The useful ledger entries named exact counts, active
roots, PIDs, Docker shape, endpoint health, dominant errors, and the next
action already taken.

The thread also exposed a ledger hazard: mixed append and prepend behavior made
the newest status easy to misread. A future workflow should require one clear
ordering rule, an unmistakable top timestamp, and a short latest-state block.

### Strict Row Accounting

Raw `summary_info.json` counts were not enough. The useful count rule was:

- terminal summary exists;
- no `DO_NOT_COUNT` ancestor;
- no known infra poison in the related task log;
- no wrong route, missing tool, timeout, stack trace, bad parameter, or forced
  pause artifact;
- de-duplicated by arm and task, not raw file count.

Clean zero-reward max-step rows were counted as valid task failures. Missing,
timeout, unscored, nonterminal, wrong-port, bad-tool, and poisoned rows stayed
out of headline counts.

The thread also showed that count code should explain its unit. A raw file
count, task-attempt count, copied-summary count, and paired valid arm-task
count can all be different. The operator should name which one is being used
before reporting a headline.

### Invalid Rows Are Work

The strongest correction in the thread was to stop treating invalid rows as a
status caveat. Invalid rows became a repair queue. The operator marked poisoned
or timeout rows with `DO_NOT_COUNT`, launched the smallest clean replacement
slice when safe, rescored or reclassified when appropriate, and kept healthy
lanes running.

This is a durable habit for benchmark guidance: a neat blocker report is not a
result. If unaffected comparable work can continue safely, continue it. If a
slice is bad, quarantine that slice and make the next local move.

Invalid rows in this thread fell into separate evidence categories: timeouts
before terminal summary, infrastructure poison after terminal artifacts, forced
stops from user pause, launch failure before task execution, protocol-unsafe
rerun or rescore cases, and replacement work that was still live. Keep those as
evidence categories unless a target skill adopts final names.

### Owned Process Boundaries

Good interventions were narrow. The operator stopped child pairs for poisoned
tasks, left healthy parent lanes alone when possible, and stopped a bulk parent
only after repeated poisoned refills proved the lane itself was no longer a
clean spend path.

This is worth preserving because it prevents two opposite failures: killing the
whole run for one bad task, and letting one poisoned task consume model time
after it is no longer countable.

### Launcher And Port Provenance

Several failed repair attempts came from assuming a checkout, wrapper, or port
offset was still valid. The safer pattern was to copy the latest working launch
record, inspect active parent command lines, verify derived ports before
launch, and check that any same-origin proxy had a live upstream. Arbitrary
offsets and stale wrappers produced uncountable roots.

Future guidance should push agents to read active launch records and proven
repair scripts before inventing flags.

The failure pattern was concrete:

- a working parent came from an older wrapper environment;
- the current checkout no longer exposed the same flags;
- a same-origin proxy offset could listen while its upstream service was dead;
- a derived port could exceed the valid port range;
- reusing a bad historical label made provenance harder to audit.

These are stack-operation lessons, not benchmark-result lessons. They belong in
references or workflow notes, not top-level global defaults.

### Docker Hygiene

The run needed precise Docker cleanup, not broad cleanup. Useful cleanup
removed only unused `test-*` networks, completed owned stacks, or stale
single-task containers. It did not recreate old fleets, reset healthy shared
stacks, or remove containers just because they were noisy in a listing.

The important distinction is ownership plus attachment state: an unused network
with zero containers is cleanup. A stack with active workers is run state.

The thread's best Docker decisions all had a narrow proof:

- container count before and after;
- matching Compose project or label;
- zero attached containers for network cleanup;
- no active benchmark process on the offset;
- completed or marked root before stack removal.

### Throughput Honesty

The thread repeatedly recalculated ETA from strict valid rows per hour and said
when a deadline was impossible. This avoided treating a target time as a
promise after the live rate made it mathematically impossible.

The lane-cap decisions were also useful. The operator did not automatically
fill all five lanes when the bottleneck was model response latency. Concurrency
was tied to terminal-row throughput and invalid-row risk, not just available
slots.

The status packet pattern should include both numbers:

- current clean pace, such as valid rows per hour over a named window;
- required clean pace to meet the requested deadline.

When the required pace is far beyond the observed pace, the operator should say
so and keep working on the next valid local action.

### Pause Authority

The explicit user pause overrode heartbeat instructions. The operator stopped
owned runner trees, verified no owned workers remained, preserved artifacts,
deleted or neutralized stale monitors, and classified forced-stop rows as
nonterminal and uncountable.

This exposed a goal-design question for Compass: a user pause is not proof that
the benchmark objective is complete, but active heartbeats must not keep
restarting work after the pause. The installed goal guidance should eventually
make that distinction explicit.

The better pause contract is:

1. Stop only owned workers.
2. Verify no owned worker remains.
3. Preserve logs and artifact roots.
4. Mark interruption artifacts out of strict counts.
5. Disable or delete stale monitors that would violate the pause.
6. Write a resume packet with roots, PIDs stopped, counts, and uncounted rows.
7. Do not claim the original benchmark objective is complete unless the user
   explicitly accepts the paused state as the endpoint.

## Failure Modes To Preserve

These are the failure modes that were concrete enough to carry forward:

- `stale-ledger`: a status file had historical sections that looked current.
- `raw-count-drift`: raw terminal summaries overstated strict valid rows.
- `poison-after-terminal`: a terminal row existed but related logs contained
  infrastructure poison.
- `unmarked-timeout`: a task timed out without a terminal summary or marker.
- `bad-offset-repair`: a repair offset looked free but lacked a live upstream.
- `wrapper-drift`: current checkout flags did not match the active parent
  wrapper.
- `heartbeat-after-pause`: automation tried to resume after an explicit pause.
- `slot-overfill`: available lanes hid a model-latency bottleneck.

Each failure mode should be fixed in the narrowest surface. Some belong in
benchmark references. Some belong in goal guidance. Some should remain only in
this local evidence packet unless they recur.

## Promoted Compass Changes

This PR promotes the narrow installed guidance that survived review:

- `codex/skills/benchmark-run-operator`: tighten ledger control, strict row
  gates, invalid rows as recovery work, launcher provenance, Docker cleanup,
  and throughput honesty.
- `codex/skills/using-codex-goals`: clarify explicit user pause semantics for
  long active goals. The agent should stop monitors and record resume state
  without implying the original result objective was achieved.

Remaining candidates should stay evidence-backed and narrower than this local
packet:

- `workflows/agent-failures.md`: consider recording a failure pattern for raw
  summary counts that ignored log poison and for arbitrary repair offsets that
  lacked live upstream services.
- `local-docs/maintenance-learnings.md`: if this becomes common outside
  benchmark work, add a repo-local maintenance note about promoting thread
  lessons through evidence maps rather than copying whole transcripts.

## Promotion Bar

Promote a lesson from this file only when it meets all of these checks:

- It names a repeated failure mode, not just a successful tactic.
- It applies beyond the A3 run.
- It can be stated without local task ids, PIDs, ports, tunnels, or artifact
  roots.
- It belongs in a narrower installed skill or reference, not in global
  `codex/AGENTS.md`.
- It can be verified by existing Compass checks or a small added check.

## Do Not Promote Blindly

Keep A3-specific task ids, local artifact roots, PID values, ports, and tunnel
paths out of installed Compass behavior. They are evidence for this thread, not
portable guidance.

Do not turn every successful behavior into a global rule. Promote only the
parts that prevent repeated failure modes: strict count gates, ledger clarity,
owned-slice repair, pause authority, launch provenance, and throughput honesty.
