# Goal Contracts

Load this reference when a task needs copyable `/goal` prompts, controller
handoffs, monitor goals, child-goal activation language, or examples of good
completion predicates.

## Contents

- Goal Brief Template
- Goal State Boundary
- Controller Goal Template
- Worker Goal Template
- Monitor Goal Template
- Blocker Pressure
- Subagent Slice Template
- Child Goal Activation Snippet
- Delegation Flow
- Fan-Out Rules
- Completion Predicate Examples
- Waiting Rule Examples

## Goal Brief Template

```text
/goal <objective>

Done means:
Scope:
Out of scope:
Evidence required:
If waiting on external state:
If stuck or failing:
Subagents:
```

Use this form to turn broad intent into a durable contract. Keep every field
concrete enough that another agent can verify it from named evidence.

## Goal State Boundary

Goal state is local to the context that activates it:

- delegated `/goal` text to another thread or spawned subagent is plain text
  until the child applies it;
- a child that needs active goal state applies it by calling `create_goal` for
  itself;
- the parent controller keeps completion authority for the parent goal;
- child completion is evidence for the parent goal, not completion of the
  parent goal;
- nested fan-out stays controller-owned.

## Controller Goal Template

Use this when the parent thread owns orchestration, verification, or routing.

```text
/goal <parent objective>

Done means:
Scope:
Out of scope:
Evidence required:
If waiting:
If stuck or failing:
Subagents:
```

Good controller scopes often include:

- keep parent completion authority;
- verify child evidence before accepting status claims;
- route blockers into concrete next actions;
- keep live docs or handoffs current only when they reflect real state.

## Worker Goal Template

Use this when a child thread or subagent owns one executable slice.

```text
/goal <slice objective>

Done means:
Scope:
Out of scope:
Evidence required:
If waiting:
If stuck or failing:
Subagents:
```

Good worker scopes keep one owner, one slice, one done condition, and one
evidence set.

## Monitor Goal Template

Use this when the job is oversight, not implementation.

```text
/goal Monitor <target thread, run, or PR> until <time or completion condition>.

Done means:
Scope:
Out of scope:
Evidence required:
If waiting:
If stuck or failing:
Subagents:
```

Good monitor scopes say when to intervene, what drift counts as off-task, and
what cadence to use between checks.

## Blocker Pressure

Do not write goal contracts that make `BLOCKED` feel like an acceptable finish
line. A blocker is a claim that must be compressed until it turns into one of
three things: a concrete local next action, a reroute to a better owner, or a
specific external decision that cannot be made from the workspace.

Good contracts tell the worker what to do when stuck:

- inspect the exact failure;
- name what was tried and what it proved;
- try the smallest reversible repair;
- use a bounded validation;
- ask the controller only when the remaining decision is genuinely outside the
  worker's authority.

## Subagent Slice Template

Use this as a contract. Active goal state exists only after the child applies
goal tools in its own context.
Delegated messages to other threads and spawned subagents treat `/goal` text as
plain text until the child applies it. If the child needs active goal state, ask
that child to apply the goal to itself by calling `create_goal` for its own
slice.

```text
Parent goal:
Slice:
Allowed files or systems:
Out of scope:
Inputs to inspect:
Expected output:
Evidence required:
Done condition for this slice:
Constraints:
Return one status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED.
```

The controller should keep ownership of the parent goal. A subagent completes
only its slice and returns evidence for integration. `BLOCKED` is an unfinished
signal, not a successful slice outcome. The controller preserves parent-goal
judgment, asks unblock questions, routes execution to a worker or fresh worker,
and records any concrete dependency that remains.

## Child Goal Activation Snippet

If a separate thread or subagent truly needs its own active goal, include an
explicit self-application instruction like this:

```text
First action: if goal tools are available, call create_goal with this objective:
<slice objective>.
Then call get_goal and confirm the active objective before working.
Treat this prompt as activation instructions. Apply goal tools in this context.
When the slice is complete, call update_goal with status complete.
```

A controller-sent delegation should still include the slice contract so the work
is useful even when no active goal state exists in the child context.

## Delegation Flow

Use this flow when the parent goal has independent slices:

1. Controller derives slices from the parent completion predicate.
2. Controller gives each child one slice, allowed scope, out-of-scope boundary, and
   evidence requirements.
3. Child applies its own goal if goal tools are available.
4. Child inspects only the inputs needed for its slice.
5. Child returns status, changed files or findings, checks run, evidence, and
   unresolved risks.
6. Controller reviews the evidence against the slice done condition.
7. Controller integrates results across slices and decides whether the parent
   goal is complete, needs more work, or is still waiting.

The controller keeps final parent completion authority. A child can say its slice
is done, and the controller verifies that every slice and cross-slice requirement
satisfies the parent goal.

## Fan-Out Rules

Choose the orchestration surface deliberately:

- Use subagents for bounded worker slices that should report back to the
  controller. Spawned subagents can create their own goals when goal tools are
  available. Keep nested fan-out controller-owned: children return proposed
  slices, and the controller spawns the next layer.
- Use separate threads for durable, user-visible work streams that may need to
  persist independently in the sidebar.
- For tree-shaped work, keep fan-out controller-owned. Let children return
  proposed slices, then have the controller spawn the next layer.
- Use monitor goals for oversight threads that should check for drift, false
  blockers, or false completion while implementation ownership stays with the
  assigned worker.

## Completion Predicate Examples

Good predicates name the finish line and the proof:

- All named PRs are open, green, reviewed, and linked in the final report.
- Each listed repo has a current diff audit, a matching `MODIFICATIONS.md`, and
  verification that only requested changes were touched.
- The report exists at the requested path, covers each named comparison axis,
  and has been checked for formatting or repo-specific style constraints.

Use concrete predicates in place of "make progress", "clean it up", or "look
into it", unless the user explicitly wants exploration only.

## Waiting Rule Examples

Use waiting rules for external systems:

- If waiting on PR review, keep the goal active and poll for new review comments
  or approval signals. Use the wait time for independent checks or critique when
  they can move the goal.
- If waiting on CI, keep the goal active until checks pass, fail with actionable
  logs, or time out under the user's stated policy.
- If waiting on an external run, preserve artifacts and report the next expected
  checkpoint instead of marking complete early.

Do not treat failed setup, stale review, or a partial run as completed waiting.
Convert it into worker questions, owner reroute, a real monitor, or the concrete
dependency that remains.

Waiting must prove itself. If there is no named external event to wait for, the
goal is not waiting. It is asking for the next repair, review, reroute, or
inspection move.
