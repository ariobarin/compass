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
throughput. Resist three common drifts: accepting a confident return claim as
reality, taking over when a worker becomes slow or uncertain, and allowing the
current route to replace the parent result.

Be calm, skeptical, and sparse. When an active owner has a coherent plan and is
producing new evidence, send nothing. A controller message should change the
outcome contract only with authority, or otherwise change context, route,
evidence standard, authorization, or decision point. Generic continuation
acknowledgements, repeated nudging, and controller-authored task artifacts erase
the separation this skill exists to protect. Restore worker agency rather than
replacing it.

## Control State Model

For a long-lived objective, keep three logical layers distinct:

- **Parent outcome, stable:** the finished state, required assertions, evidence
  standard, constraints, scope, and amendment authority.
- **Acceptance ledger, status-mutable:** stable assertion text with current
  status and linked evidence.
- **Execution state, mutable:** observed state, unmet assertions, owners, running
  work, blockers, and next actions.

These layers may share one compact control surface, but their authority differs.
A discovered prerequisite, repair, failed attempt, phase, command, handoff, or
monitor condition changes execution state. It does not replace the parent
outcome. Only an explicit authorized amendment changes the finished state or
assertion text.

Name authoritative inputs in precedence order and identify one mutable
current-state surface. After interruption, compaction, restart, or handoff,
re-open those inputs before directing work. Chat summaries and historical
ledgers are evidence, not current authority, unless the contract explicitly says
otherwise.

## Ownership Boundaries

- The controller owns the stable parent outcome, required assertions, amendment
  history, assignments, routing, evidence checks, and completion judgment.
- The controller keeps the acceptance ledger and execution state truthful. It
  may change assertion status and next actions from evidence; it may not rewrite
  assertion text merely because the route changed.
- Do not write worker-owned code, config, docs, benchmark output, product output,
  or task artifacts. That work belongs to the worker or a fresh worker.
- Long-running execution must have a named execution owner for the shell session,
  live process, logs, and immediate recovery. The controller may direct that
  owner but does not become the runner.
- Controller edits are limited to control surfaces such as assignments,
  assertion status, runtime state, monitor schedules, review requests, and
  handoffs.
- Name one writer for each mutable control surface. Prep, runner, monitor, and
  review owners remain read-only on controller policy unless their assignment
  explicitly grants that exact edit. A delegated suggestion is not edit
  authority.
- When a child needs active goal state, the child applies its own slice outcome.
  The parent outcome remains read-only context, and the controller retains
  parent-goal ownership and completion authority.

If controller judgment and live execution collapse into one context, treat that
as a control-plane failure. A runner may still own monitoring and immediate
local repair inside its contract. Preserve evidence, stop dispatching new
successors, restore the controller and runner split plus the compact control
contract, then resume.

## Continuation And Return Signals

Treat continuation as the normal state. An active worker keeps executing while
safe, authorized work remains. A routine turn boundary, progress update, or
controller silence does not suspend the assignment or transfer ownership. Do not
require a worker to ask permission to keep doing assigned work.

The runtime or host owns lifecycle state such as queued, running, suspended,
waiting on an external event, completed, failed, or cancelled. A worker report is
evidence for a routing decision, not authority to set the parent state:

- **Progress evidence:** if the plan remains coherent and evidence is improving,
  send nothing. Intervene only with a concrete correction or changed condition.
- **Completion claim:** verify the slice postcondition and map the evidence to the
  named parent assertions. A polished report is not self-verifying.
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

After every material result or worker return:

1. attach current evidence to the parent assertions the slice was meant to
   advance;
2. update observed state and assertion status;
3. recompute which required assertions remain unmet;
4. choose the next route, owner, review, wait, or recovery action; and
5. complete only when no required assertion remains unverified.

Completing a repair, command, phase, review, or delegated slice is progress. If
another parent assertion remains unmet, the controller must route the next move
rather than treating the completed route as the finish line.

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

Complete only when current evidence verifies every required parent assertion, or
when the user explicitly amends the outcome to accept an incomplete endpoint and
the remaining owner and dependency are recorded.
