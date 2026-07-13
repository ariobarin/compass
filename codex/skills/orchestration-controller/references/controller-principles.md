# Controller Principles

Use this reference when the controller needs more detail than the router.

## Stance

A controller protects judgment by staying outside execution. Workers are close
to commands, edits, logs, and local failures. The controller remains close enough
to understand evidence but far enough away to keep the parent result, required
assertions, ownership, and stop conditions visible.

Do not answer worker friction with slogans or takeover. Strong direction names an
owner, executable action, and proof. A controller message should change the
route, context, evidence standard, authorization, or decision point. Otherwise it
is noise.

## Control Contract

Front-load the stable contract before mutable execution state:

1. desired finished state;
2. required final-state assertions and verification surfaces;
3. constraints, scope, exclusions, and amendment authority;
4. authoritative inputs in precedence order;
5. live state surface and its writer;
6. current owner and execution state;
7. next action, evidence, and history.

The first four items describe what completion means and should not change merely
because the current route changes. The final three are operating state and may be
rewritten as evidence arrives.

Treat controller state as four linked variables:

- **O - outcome:** stable finished-state assertions;
- **S - observed state:** what current evidence says exists now;
- **G - gap:** required assertions not yet verified from `S`;
- **P - plan:** the current route for reducing `G`.

Worker returns normally change `S`, `G`, and `P`. Only an explicit authorized
amendment changes `O`. If the current obstacle vanished, `O` should still tell a
fresh controller what finished work looks like.

Long-running work needs an execution owner for the process, output, logs, and
immediate retries. The controller owns the outcome contract, acceptance ledger,
evidence checks, reroutes, and completion decision.

Each mutable control surface has one named writer. Delegated prep, execution,
monitoring, and review roles may propose policy changes but do not edit the
controller-owned contract unless the assignment grants that exact authority.
Before accepting an edit, verify the expected prior revision and preserve the
previous state as evidence. Outcome or assertion edits also require the named
amendment authority and a recorded reason.

After interruption, compaction, restart, or handoff, re-open the authoritative
inputs in order before routing work. Use history to explain how the current state
arose, not to override the current-state surface. If execution, monitoring, and
immediate local repair remain with the runner, that is normal. If controller
judgment also collapses into that execution context, preserve evidence and
restore the controller and runner split before dispatching more work.

## Autonomous Continuation

Once dispatched, an owner keeps the assignment while useful, safe, authorized
work remains. The end of a model turn, a progress update, or controller silence
does not transfer ownership. The owner returns control only after verifying its
slice postcondition or reaching a real exception: an exact missing input, a named
external wait with no parallel work, an explicit hold or cancellation, an
authorization or safety boundary, or an unrecoverable failure after local
recovery.

When a host forces a checkpoint, preserve the parent assertion mapping, slice
outcome, current route, and evidence, then requeue the same owner unless the
controller explicitly changes the route. Do not add an acknowledgement handshake
to ordinary progress.

When an active worker has a coherent plan and is producing new evidence, send no
worker-directed message. Intervene only to supply missing input, correct course,
change scope, set a hold, cancel, reassign, or choose a recovery action.

## Read Return Signals

The host owns lifecycle state. A worker report is a claim about the artifact or
an exception that may require routing:

- A **progress report** should include evidence, the parent assertions it
  advances, and the next action. If progress is coherent, it requires no
  controller response.
- A **completion claim** triggers independent checks against the slice
  postcondition and named parent assertions. Remaining concerns are recorded
  separately from completion.
- An **input request** must name the exact fact, decision, permission, or context
  that blocks all remaining safe work.
- An **external wait** must name the event or process, its owner, and why no useful
  parallel work remains. Route mechanical waiting to a monitor.
- A **failure report** must name the failed action, evidence, local recovery,
  current system state, smallest reversible next move, and required owner.
- A **negative result** is evidence to assess, not a reason to stop by itself.

A useful exception diagnosis is short:

```text
Which parent assertion is still unmet?
What exactly prevents the next safe action?
What did the last attempt prove?
What state exists now?
What is the smallest reversible move?
Who owns that move?
```

The worker performs diagnosis and execution inside its boundary. The controller
chooses the route without absorbing the task.

After a return, the controller updates evidence and status, recomputes the gap to
the full parent outcome, and then chooses the next route. A completed slice never
short-circuits this reconciliation.

## Detect Thrash

Thrash is motion that no longer improves judgment. It includes repeated attempts
without new evidence, widening scope, log dumps without a next action, routine
debugging escalated to the user, a worker nearing context saturation, or repeated
rewrites of the objective to match whichever route is currently active.

Reset the route with:

```text
Parent outcome, read-only:
Required parent assertions:
Assertions advanced by this slice:
Current evidence:
Still-unmet assertions:
Attempts that changed state:
Next smallest reversible action:
Fresh owner needed:
```

A fresh owner receives that packet and owns execution. The controller does not
absorb the task or replace the parent outcome with the recovery action.

## Monitoring And Review

Use a controller heartbeat only when each wake requires judgment such as
inspecting new evidence, rerouting, requesting review, or choosing recovery. Put
mechanical waits inside one bounded command through `monitor-to-completion`.

A monitor's exit condition is evidence for the controller. It is not parent
completion unless the stable parent contract explicitly defines it as a required
assertion.

Monitoring should create perspective, not constant presence. When work is moving
under a clear owner and evidence gate, step back. When the next event is purely
mechanical, do not spend model turns watching it.

Use independent review or checks to test worker claims. Review is a source of
judgment, not another reporting ritual. Route findings back to the implementation
owner and then update the parent acceptance ledger from evidence.

## Controller Handoff

A handoff should preserve the completion contract and current control state, not
narrate every attempt.

```text
Parent outcome, read-only:
Required assertions and evidence standard:
Outcome amendments, if any:
Acceptance ledger or canonical path:
Authoritative inputs, in order:
Live state surface and writer:
Current owner:
Current runtime state:
Running now:
Evidence matched to assertion IDs:
Still-unmet assertions:
Signals needing judgment:
Reroutes or questions sent:
Next decision point:
Remaining dependency:
Re-anchor action:
```

## Goal Activation

When a child needs active goal state, tell it to apply and confirm an observable
slice outcome tied to named parent assertion IDs in its own context. Delegated
goal text alone is not active state. The parent outcome remains read-only context,
and parent completion authority remains with the controller.
