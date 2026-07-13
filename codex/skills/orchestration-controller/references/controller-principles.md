# Controller Principles

Use this reference when the controller needs more detail than the router.

## Stance

A controller protects judgment by staying outside execution. Workers are close
to commands, edits, logs, and local failures. The controller remains close enough
to understand evidence but far enough away to keep the parent result, ownership,
and stop conditions visible.

Do not answer worker friction with slogans or takeover. Strong direction names an
owner, executable action, and proof. A controller message should change the
route, context, evidence standard, authorization, or decision point. Otherwise it
is noise.

## Control Contract

Front-load every assignment or handoff with:

1. desired result;
2. current owner;
3. next action;
4. stop condition;
5. authoritative inputs in precedence order;
6. mutable current-state surface;
7. evidence and history.

Long-running work needs an execution owner for the process, output, logs, and
immediate retries. The controller owns the run contract, evidence checks,
reroutes, and completion decision.

Each mutable control surface has one named writer. Delegated prep, execution,
monitoring, and review roles may propose policy changes but do not edit the
controller-owned contract unless the assignment grants that exact authority.
Before accepting an edit, verify the expected prior revision and preserve the
previous state as evidence.

After interruption, compaction, restart, or handoff, re-open the authoritative
inputs in order before routing work. Use history to explain how the current
state arose, not to override the current-state surface. If execution, monitoring,
and immediate local repair remain with the runner, that is normal. If controller
judgment also collapses into that execution context, preserve evidence and
restore the controller and runner split before dispatching more work.

## Autonomous Continuation

Once dispatched, an owner keeps the assignment while useful, safe, authorized
work remains. The end of a model turn, a progress update, or controller silence
does not transfer ownership. The owner returns control only after completing the
objective or reaching a real exception: an exact missing input, a named external
wait with no parallel work, an explicit hold or cancellation, an authorization
or safety boundary, or an unrecoverable failure after local recovery.

When a host forces a checkpoint, preserve the objective and evidence and requeue
the same owner unless the controller explicitly changes the route. Do not add an
acknowledgement handshake to ordinary progress.

When an active worker has a coherent plan and is producing new evidence, send
no worker-directed message. Intervene only to supply missing input, correct
course, change scope,
set a hold, cancel, reassign, or choose a recovery action.

## Read Return Signals

The host owns lifecycle state. A worker report is a claim about the artifact or
an exception that may require routing:

- A **progress report** should include evidence and the next action. If progress
  is coherent, it requires no controller response.
- A **completion claim** triggers independent checks against the parent
  objective. Remaining concerns are recorded separately from completion.
- An **input request** must name the exact fact, decision, permission, or context
  that blocks all remaining safe work.
- An **external wait** must name the event or process, its owner, and why no useful
  parallel work remains. Route mechanical waiting to a monitor.
- A **failure report** must name the failed action, evidence, local recovery,
  current system state, smallest reversible next move, and required owner.
- A **negative result** is evidence to assess, not a reason to stop by itself.

A useful exception diagnosis is short:

```text
What exactly prevents the next safe action?
What did the last attempt prove?
What state exists now?
What is the smallest reversible move?
Who owns that move?
```

The worker performs diagnosis and execution inside its boundary. The controller
chooses the route without absorbing the task.

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
judgment, not another reporting ritual. Route findings back to the implementation
owner.

## Controller Handoff

A handoff should preserve control state, not narrate every attempt.

```text
Objective:
Current owner:
Current runtime state:
Authoritative inputs, in order:
Mutable current-state surface:
Running now:
Evidence matched:
Signals needing judgment:
Reroutes or questions sent:
Next decision point:
Remaining dependency:
Re-anchor action:
```

## Goal Activation

When a child needs active goal state, tell it to apply and confirm the slice
goal in its own context. Delegated goal text alone is not active state. Parent
completion authority remains with the controller.
