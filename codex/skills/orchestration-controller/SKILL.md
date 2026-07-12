---
name: orchestration-controller
description: Oversee delegated work without taking over worker execution or accepting completion without evidence.
---

# Orchestration Controller

Use this skill when a parent objective spans workers, reviews, monitors, or
long-running execution and needs an owner above the work.

Do not use it to perform a worker task. Use `subagent-driven-development` for
same-session plan execution and `monitor-to-completion` for mechanical waits.

## Posture

Stay one level above execution. The controller's value is preserved perspective,
not extra implementation throughput.

Actively resist two common drifts: accepting a confident status as reality, and
taking over when a worker becomes slow or uncertain. Be calm, skeptical, and
sparse. Each intervention should clarify the result, owner, next action, or
evidence. Generic pressure, repeated nudging, and controller-authored task
artifacts erase the separation this skill exists to protect.

A worker can be close to the details and still lose the parent objective. The
controller keeps that objective visible, notices bad ownership or thrash, and
routes the next executable move. It restores agency rather than replacing it.

## Ownership Boundaries

- The controller owns the parent objective and assignments. The controller owns
  the contract, cadence, routing, evidence checks, and completion judgment.
- Do not write worker-owned code, config, docs, benchmark output, product output,
  or task artifacts. That work belongs to the worker or a fresh worker.
- Long-running execution must have a named execution owner for the shell
  session, live process, logs, and immediate recovery. The controller may direct
  that owner but does not become the runner.
- Controller edits are limited to control surfaces such as assignments, status,
  monitor schedules, review requests, and handoffs.
- When a child needs active goal state, the child applies its own goal. The
  controller retains parent-goal ownership and completion authority.

Treat worker statuses as claims. Verify `DONE` against the parent objective.
Diagnose `BLOCKED` from the failed action, evidence, recovery tried, current
state, next reversible move, and any true external dependency. Do not confuse a
well-written explanation of stopping with proof that stopping is correct.

## Required Reference

Read [controller-principles.md](references/controller-principles.md) when signal
interpretation, rerouting, monitoring, review, or handoff judgment needs detail.

## Completion

Complete only with evidence that matches the parent objective, or with a
user-accepted incomplete endpoint that names the remaining owner and dependency.
