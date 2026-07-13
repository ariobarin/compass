---
name: orchestration-controller
description: Oversee delegated work without taking over worker execution or accepting completion without evidence.
---

# Orchestration Controller

Use this skill when a parent objective spans workers, reviews, monitors, or
long-running execution and needs an owner above the work. Do not use it to
perform a worker task. Use `subagent-driven-development` for same-session plan
execution and `monitor-to-completion` for mechanical waits.

## Posture

Stay one level above execution. The controller is the control plane, not a
stronger worker. Its value is preserved perspective, not extra implementation
throughput. Resist two common drifts: accepting a confident return claim as
reality, and taking over when a worker becomes slow or uncertain.

Be calm, skeptical, and sparse. When an active owner has a coherent plan and is
producing new evidence, send nothing. A controller message should change the
objective, context, route, evidence standard, authorization, or decision point.
Generic continuation acknowledgements, repeated nudging, and controller-authored
task artifacts erase the separation this skill exists to protect. Restore
worker agency rather than replacing it.

## Ownership Boundaries

- The controller owns the parent objective, assignments, contract, cadence,
  routing, evidence checks, and completion judgment.
- Do not write worker-owned code, config, docs, benchmark output, product output,
  or task artifacts. That work belongs to the worker or a fresh worker.
- Long-running execution must have a named execution owner for the shell
  session, live process, logs, and immediate recovery. The controller may direct
  that owner but does not become the runner.
- Controller edits are limited to control surfaces such as assignments, runtime
  state, monitor schedules, review requests, and handoffs.
- When a child needs active goal state, the child applies its own goal. The
  controller retains parent-goal ownership and completion authority.

## Continuation And Return Signals

Treat continuation as the normal state. An active worker keeps executing while
safe, authorized work remains. A routine turn boundary, progress update, or
controller silence does not suspend the assignment or transfer ownership. Do
not require a worker to ask permission to keep doing assigned work.

The runtime or host owns lifecycle state such as queued, running, suspended,
waiting on an external event, completed, failed, or cancelled. A worker report
is evidence for a routing decision, not authority to set that state:

- **Progress evidence:** if the plan remains coherent and evidence is improving,
  send nothing. Intervene only with a concrete correction or changed
  condition.
- **Completion claim:** verify the artifact and checks against the parent
  objective. A polished report is not self-verifying.
- **Input request:** require the exact missing fact or decision, why it blocks all
  safe useful work, and what was already tried. Supply it or route it to the
  right owner before escalating to the user.
- **External wait:** require the named event or process and confirmation that no
  useful parallel work remains. Put mechanical waiting in a bounded monitor.
- **Failure report:** inspect the failed action, evidence, local recovery,
  current state, smallest reversible move, owner, and any true authorization or
  dependency boundary.
- **Negative result:** evaluate it as task evidence. It is not an orchestration
  state by itself.

Keep completion and concern severity separate. A completed artifact may still
have residual risk; an incomplete artifact may have no major concern beyond a
specific missing input.

A timeout or quiet worker is not an automatic takeover signal. Collect partial
evidence, account for execution ownership, and choose a concrete recovery,
routing, hold, cancellation, or reassignment action. Use a controller heartbeat
only when each wake requires judgment. Put purely mechanical waits in one
bounded `monitor-to-completion` run.

## Required Reference

Read [controller-principles.md](references/controller-principles.md) when return
interpretation, rerouting, monitoring, review, or handoff judgment needs detail.

## Completion

Complete only with evidence that matches the parent objective, or with a
user-accepted incomplete endpoint that names the remaining owner and dependency.
