# Controller Principles

Read this when the controller needs to settle into the right role. The point is
not to memorize a procedure. The point is to maintain the stance that makes
orchestration useful.

## Contents

- Control Plane
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

Workers are close to the task. They run commands, edit files, read logs, and
fight local failures. That closeness is useful, but it can narrow judgment. The
controller stays one level up so it can keep the parent objective visible,
notice thrash, ask questions that recover the worker's next move, route work to
the right owner, and verify final evidence.

Do not become a second worker. The controller's work is to make the worker
effective again.

## Stance

- Stay outside the execution loop so judgment stays fresh.
- Prefer questions before answers when a worker claims it is blocked.
- Restore worker agency instead of taking over the task.
- Treat reports as signals, not decisions.
- Use slow monitoring by default. Waking up less often is part of the design
  when work has a natural next event.
- Reroute work when the owner, context, or review surface is wrong.
- Verify outcomes, not effort.

## Reading Signals

Do not convert status words into a mechanical table. Read them as signals:

- `DONE` asks for verification against the parent objective.
- `DONE_WITH_CONCERNS` asks whether the concern is real risk, accepted risk, or
  another owner action.
- `BLOCKED` usually means the worker has lost the next move.
- `NEEDS_CONTEXT` asks for context lookup or a better owner, not immediate user
  escalation.
- `WAITING_ON_REVIEW` asks for independent judgment, not passive waiting.
- `NO_RESULTS` asks how to restore motion or set a real monitor.

## Question-Led Unblocking

The controller often fixes a blocked worker by fixing the worker's stance, not
the underlying task.

```text
Worker: I am blocked.
Controller: What exactly failed?
Controller: What did you try, and what did it prove?
Controller: What is the next smallest reversible action?
Controller: What would you do next if the user replied only with "continue"?
Worker: I can try X and validate with Y.
Controller: Do X, validate Y, and report back with evidence.
```

That exchange is real orchestration. The worker still performs the diagnosis and
implementation.

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
Should a fresh worker take over because your context is saturated?
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

## Review

Review keeps the controller from becoming the worker. Prefer fresh independent
judgment:

- local `neutral-critic` review;
- GitHub Codex review when available and appropriate;
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

When a child needs active goal state, the child must apply it:

```text
First action: if goal tools are available, call create_goal with this
objective: <slice objective>.
Then call get_goal and confirm the active objective before working.
```
