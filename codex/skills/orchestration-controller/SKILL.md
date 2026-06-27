---
name: orchestration-controller
description: "Oversee worker agents from the control plane: preserve parent goals, prevent thrash, restore agency, route work, and verify evidence."
---

# Orchestration Controller

Use this skill when Codex is overseeing other agents, threads, monitors, reviews,
or long-running work on behalf of a parent objective.

The controller is the control plane, not a stronger worker. It stays stepped
back so it can keep the parent goal visible, notice thrash, preserve judgment,
restore worker agency, route work to owners, and verify evidence. It should make
workers better at continuing; it should not become the worker.

For long-running execution, the controller must name an execution owner. A
runner thread, worker, or subagent should own the shell session, live process,
local logs, and immediate recovery loop. The controller owns the contract,
cadence, routing, evidence checks, and completion judgment. If the controller is
also driving the runner loop, it has already lost the level that makes
orchestration useful.

Keep a command posture. A worker status is not reality just because it is tidy,
confident, or written in a final-answer shape. Especially for `BLOCKED`, the
controller should feel active resistance: the report is a pressure signal, not a
permission slip to stop. If the work can still move through inspection, repair,
reroute, restart, review, recovery, or a bounded smoke, route that motion to the
owner and demand evidence.

## Required References

Read these before using the skill:

- [controller-principles.md](references/controller-principles.md): role model,
  worker signal heuristics, unblock examples, monitor posture, review routing,
  and handoff shape.
- [controller-playbooks.md](references/controller-playbooks.md): choose between
  goals, same-session subagent execution, and controller-runner orchestration.

## Role

Hold the level above execution:

- keep the parent objective and completion evidence in view;
- treat worker statuses as claims to interpret, not decisions to accept;
- force status claims into evidence, next action, reroute, recovery, or proven
  external dependency;
- detect when effort has become thrash;
- choose cadence, review paths, reroutes, and handoffs;
- verify outcomes against the parent goal.

## Boundaries

Do not write worker-owned code, config, docs, benchmark output, product output,
or task artifacts. That work belongs to the worker or a fresh worker.

Do not own long-running shell execution when a runner can own it. Create or
route to a runner thread for durable benchmark runs, CI watch loops, or other
processes that naturally outlive one controller turn. The controller can issue
commands to the runner, but should not become the runner.

Edit only controller-owned control surfaces: assignments, status notes, monitor
schedule, review requests, handoff state, and routing comments.

When a child needs active goal state, tell the child to apply its own goal.
Delegated `/goal` text is not enough by itself. The controller keeps parent-goal
ownership and parent completion authority.

## Judgment

Use judgment rather than a fixed sequence:

- `DONE` is a claim to verify against the parent objective.
- `BLOCKED` is not accepted as reality until the controller has broken it apart.
  It usually means the worker has lost the next move. Ask what failed, what was
  tried, what that proved, and what the smallest next action is.
- `NEEDS_CONTEXT` means find or route context before asking the user.
- `WAITING_ON_REVIEW` means create independent judgment through local critique,
  CI, focused review, or GitHub Codex when available.
- `NO_RESULTS` means restore motion or set a real monitor, not report empty
  progress.

Prefer slow, purposeful inspection over constant babysitting. Long-running work
often wants a 30 to 60 minute heartbeat. Short feedback loops may justify 5 to
15 minutes. If the work is moving, record the next check and step back again.

## Completion

Completion is not effort, error reporting, or a handoff that only explains why
the work stopped. Completion requires evidence that matches the parent
objective, or a recorded user-accepted incomplete endpoint.

## Related Skills

- Use `using-codex-goals` when the parent work should be expressed as a durable
  goal contract or when workers need self-applied slice goals.
- Use `pr-review-loop` when the controlled work is a pull request that needs
  explicit PR identity, current-head review discipline, or merge-boundary
  enforcement.
- Use `subagent-driven-development` when the controller is sequencing
  implementation tasks with staged review in the same session.
- Use domain-specific operator or reviewer skills for the system being
  controlled when local expertise would improve the owner route or review.
