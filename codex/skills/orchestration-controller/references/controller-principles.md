# Controller Principles

Use this reference when the controller needs more detail than the router.

## Stance

A controller protects judgment by staying outside execution. Workers are close
to commands, edits, logs, and local failures. The controller remains close enough
to understand evidence but far enough away to keep the parent result, ownership,
and stop conditions visible.

Do not answer worker friction with slogans or takeover. Strong direction names an
owner, executable action, and proof. A controller message should change the
route, context, evidence standard, or decision point. Otherwise it is noise.

## Control Contract

Front-load every assignment or handoff with:

1. desired result;
2. current owner;
3. next action;
4. stop condition;
5. evidence and history.

Long-running work needs an execution owner for the process, output, logs, and
immediate retries. The controller owns the run contract, evidence checks,
reroutes, and completion decision.

## Read Worker Signals

Status words compress a worker's view. They do not decide the controller's next
move.

- `CONTINUE`: the owner keeps executing the named action.
- `DONE`: verify evidence against the parent objective.
- `DONE_WITH_CONCERNS`: decide whether the concern is accepted risk or another
  owner action.
- `NEEDS_CONTEXT`: find context or route to a better owner before escalating.
- `BLOCKED`: diagnose before accepting a stop.
- `WAITING_ON_REVIEW`: obtain independent judgment.
- `NO_RESULTS`: inspect what changed and whether to restore motion, monitor, or
  reroute.

For `BLOCKED`, require the exact failed action, evidence, local recovery tried,
current system state, smallest reversible next move, and the external decision
that truly prevents progress. Choose continue, reroute, pause, or user
escalation from that evidence.

A useful unblock exchange is short:

```text
What exactly failed?
What did that attempt prove?
What state exists now?
What is the smallest reversible move?
Who owns that move?
```

The worker performs the diagnosis and execution. The controller chooses the
route.

## Detect Thrash

Thrash is motion that no longer improves judgment. It includes repeated attempts
without new evidence, widening scope, log dumps without a next action, routine
debugging escalated to the user, or a worker nearing context saturation.

Reset the route with:

```text
Objective:
Current evidence:
Attempts that changed state:
Next smallest reversible action:
Fresh owner needed:
```

A fresh owner receives that packet and owns execution. The controller does not
absorb the task.

## Monitoring And Review

Use a controller heartbeat only when each wake requires judgment such as
inspecting evidence, rerouting, requesting review, or choosing recovery. Put
mechanical waits inside one bounded command through `monitor-to-completion`.

Monitoring should create perspective, not constant presence. When work is moving
under a clear owner and evidence gate, step back. When the next event is purely
mechanical, do not spend model turns watching it.

Use independent review or checks to test worker claims. Review is a source of
judgment, not another status ritual. Route findings back to the implementation
owner.

## Controller Handoff

A handoff should preserve control state, not narrate every attempt.

```text
Objective:
Current owner:
Current state:
Running now:
Evidence matched:
Signals needing judgment:
Reroutes or questions sent:
Next decision point:
Remaining dependency:
```

## Goal Activation

When a child needs active goal state, tell it to apply and confirm the slice
goal in its own context. Delegated goal text alone is not active state. Parent
completion authority remains with the controller.
