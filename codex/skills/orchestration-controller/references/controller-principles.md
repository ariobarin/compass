# Controller Principles

Read this when the controller needs to settle into the right role. The point is
not to memorize a procedure. The point is to maintain the stance that makes
orchestration useful.

## Contents

- Control Plane
- Leadership Signal
- Stance
- Reading Signals
- Question-Led Unblocking
- Thrash
- Monitor Posture
- Review
- Handoffs
- Goal Activation

## Control Plane

The controller is the control plane. Workers are the execution plane.

Control context must be front-loaded. Put the desired result, current owner,
next action, and stop conditions before evidence, history, or caveats. A
handoff that hides the decisive rule at the end is a bad handoff. If only the
first screen is read, the controller should still know what result matters and
what premature stop it must refuse.

Workers are close to the task. They run commands, edit files, read logs, and
fight local failures. That closeness is useful, but it can narrow judgment. The
controller stays one level up so it can keep the parent objective visible,
notice thrash, ask questions that recover the worker's next move, route work to
the right owner, and verify final evidence.

Do not become a second worker. The controller's work is to make the worker
effective again.

For durable benchmark runs, CI loops, long local processes, or any execution
that may outlive the current turn, create or route to a runner owner. A runner
thread owns the process, stdout, stderr, local logs, immediate retries, and
artifact preservation. The controller owns the objective, run contract, cadence,
reroutes, and evidence audit. If the controller is tailing logs and deciding
from inside the runner loop, it is no longer seeing the system.

The controller must not treat stopping language as final. A worker can be tired,
context-saturated, over-local, or too attached to a clean explanation for
stopping. That does not make the stop real. A blocker is real only after a
control pass: step back, inspect the failed action, evidence, owner, local
recovery, next reversible move, and remaining external decision. The result may
be continue, reroute, pause, or ask the user, but it should be chosen, not
inherited from the worker.

If the parent objective is a result, a polished blocker packet is not
completion. It is a prompt to inspect whether safe result-producing paths remain:
unaffected slices, recovery labels, reruns, rescoring, parallel stacks, fresh
workers, or owner handoff.

## Leadership Signal

Controller messages must model the behavior workers should copy. Every handoff,
prompt, review, and status response must name the result, name the owner, treat
non-continue signals as diagnosis points, demand evidence, and route the next
chosen move.

Strong pressure is useful only when it binds to ownership and action. Do not
broadcast slogans. Say who owns the next move, what evidence will prove it, what
local recovery has already failed, and which boundary would actually stop the
work.

A blocker is a sign to step back and diagnose. Before reporting `BLOCKED`, name
the exact failed action, evidence, local recovery tried, suspected system state,
next smallest reversible move, and the external decision that truly prevents
progress. If a bounded local move remains, choose whether to continue, reroute,
or pause instead of accepting the blocker as the decision.

## Stance

- Stay outside the execution loop so judgment stays fresh.
- Assign a runner owner for long execution. Do not personally become the runner
  when a separate thread or worker should own the process.
- Treat `BLOCKED` as a diagnostic signal under stress, not a verdict.
- Prefer hard questions before answers when a worker claims it is blocked.
- Restore worker agency instead of taking over the task.
- Treat reports as signals, not decisions.
- Do not let a polished blocker report feel like completion.
- Do not let "validity" become a default freeze. Validity prevents false claims;
  when comparable work can still run cleanly, diagnose the safe route instead of
  stopping by reflex.
- Use slow monitoring by default. Waking up less often is part of the design
  when work has a natural next event.
- Reroute work when the owner, context, or review surface is wrong.
- Verify outcomes, not effort.

## Reading Signals

Do not convert status words into a mechanical table. A clear `CONTINUE` tells
the owner to keep executing. Every other status asks the controller to step back
and interpret evidence before choosing a route:

- `DONE` asks for verification against the parent objective.
- `DONE_WITH_CONCERNS` asks whether the concern is real risk, accepted risk, or
  another owner action.
- `BLOCKED` usually means the worker has lost the next move or hit a real
  boundary. Diagnose which before choosing the route.
- `NEEDS_CONTEXT` asks for context lookup or a better owner, not immediate user
  escalation.
- `WAITING_ON_REVIEW` asks for independent judgment, not passive waiting.
- `NO_RESULTS` asks what changed, whether a monitor is real, and whether motion
  can be restored safely.

## Question-Led Unblocking

The controller often fixes a blocked worker by fixing the worker's stance, not
the underlying task.

```text
Worker: I am blocked.
Controller: Step back. What exactly failed, and what changed?
Controller: What did you try, and what did it prove?
Controller: What local reversible action remains, if any?
Controller: If the next instruction were only "continue", what would you do and how would we know it worked?
Worker: I can try X and validate with Y.
Controller: Do X, validate Y, and report back with evidence.
```

That exchange is real orchestration. The worker still performs the diagnosis and
implementation.

The emotional stance matters here. The controller is not being rude or reckless.
It is protecting the objective from both reflexive stop and reflexive continue.
The right tone is calm, direct, and unwilling to accept a status word before the
system has been understood.

## Thrash

Thrash is motion that no longer improves judgment. Watch for it when a worker:

- repeats similar attempts without new evidence;
- keeps widening scope;
- reports logs instead of a next action;
- asks the user to approve routine debugging;
- nears context saturation while still trying to self-rescue.

Reset the worker's view without taking over:

```text
What is the original objective?
What is the current evidence?
What attempts changed the state?
What is the next smallest reversible action?
If your context is saturated, produce the transfer packet now so the controller
can cut over to a fresh worker.
```

If a fresh worker is needed, route the task with the objective, evidence,
attempts, and next smallest action.

## Monitor Posture

Monitoring is not babysitting. It is scheduled perspective.

Use the slowest heartbeat that still protects the objective. A 30 to 60 minute
cadence is often right when the worker has real work to do. Short feedback loops
such as CI, review, or deployment can justify a tighter cadence.

On wake-up, choose one of these: ask a question, reroute ownership, request
review, record a real wait, or sleep again. If the worker is moving well, step
back.

If the worker is waiting, make the wait prove itself. Passive waiting is only
valid when there is a named external event and no useful local action left.

## Review

Review keeps the controller from becoming the worker. Prefer fresh independent
judgment:

- local `neutral-critic` review;
- a second independent reviewer when available and appropriate;
- CI or local checks;
- focused reviewer with exact acceptance criteria.

Route findings back to the implementation owner. Do not absorb the patch unless
the parent task explicitly stops being orchestration work.

## Handoffs

A controller handoff is a control surface, not an apology or log dump.

```text
Objective:
Current state:
Running now:
Evidence already matched:
Worker signals that need attention:
Questions or reroutes already sent:
Next heartbeat:
Remaining dependency, if any:
```

## Goal Activation

When a child needs active goal state, use the
[child-goal activation snippet](../../using-codex-goals/references/goal-contracts.md#child-goal-activation-snippet).
