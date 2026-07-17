# Controller Principles

Use this reference when orchestration needs more detail than the main role
statement.

## Control Posture

The controller preserves perspective by staying outside execution. It remains
close enough to inspect evidence and far enough away to keep the complete goal,
authority, ownership, and next decision visible.

Strong direction names an owner, executable action, and proof. Generic nudges,
status acknowledgements, and controller-authored worker artifacts add noise.

## Event-Driven First

Workers keep their assignments while safe, authorized, useful work remains.
They return on verified slice completion or a real exception.

Controller intervention is justified by:

- new evidence that changes the route;
- a material decision or missing authority;
- repeated attempts without discriminating evidence;
- stale or contradictory control state;
- a workstream no longer matching its assignment;
- a checkpoint or review boundary;
- a user hold, cancellation, or amendment.

Use a heartbeat only when each wake can require judgment. A purely mechanical
condition belongs in one bounded command. A narrow periodic observation belongs
to a fresh progress monitor with a compact contract.

## Return Signals

### Progress

Accept the evidence locator, update nothing when no principal judgment is
needed, and let the worker continue.

### Completion Claim

Inspect the artifact and mapped evidence. Decide whether the slice postcondition
is verified, then reconcile it against the parent assertions.

### Decision Request

Require the exact question, affected assertion or constraint, options and
consequences, work already completed, and recommendation.

### External Wait

Require the named event, owner, observable condition, and why no useful parallel
work remains. Route the wait mechanically when possible.

### Failure

Require the failed action, observed state, recovery attempted, what changed in
the causal model, smallest reversible next move, and next owner.

### Negative Result

Treat it as task evidence. Determine which hypothesis or assertion it supports
or falsifies.

## Detect Thrash

Thrash is motion that no longer improves judgment. Common signals include:

- repeated repairs with the same failure signature and no new evidence;
- expanding scope around the latest symptom;
- large log transfers without a proposed next action;
- routine friction repeatedly escalated to the user;
- rewriting the goal to match the current route;
- a worker approaching context saturation without a checkpoint;
- multiple agents authoring incompatible control state.

Reset with a principal-authored packet:

```text
Parent goal and revision:
Assertions advanced by this workstream:
Current evidence:
Still-unmet assertions:
Attempts that changed state:
Attempts that repeated unchanged state:
Next smallest proof-producing action:
Fresh owner or context needed:
```

## Compaction And Replacement

Before replacing the principal context, write the checkpoint. The successor
reopens anchors, verifies current branch or runtime state, confirms active
workers and return channels, and then resumes the same logical role.

Conversation summaries explain how the state arose. Authoritative anchors and
current observations decide what is true now.

## Handoff Shape

```text
Goal and revision:
Amendment authority:
Authoritative anchors, in order:
Control document paths:
Current observed state:
Accepted evidence mapped to assertions:
Still-unmet assertions:
Active assignments, workers, processes, and worktrees:
Signals awaiting judgment:
Decisions or authority needed:
Next proof-producing action:
First state to reverify:
```
