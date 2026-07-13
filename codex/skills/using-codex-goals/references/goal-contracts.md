# Goal Contracts

Load this reference when a task needs copyable `/goal` prompts, live control
surfaces, controller handoffs, monitor goals, child-goal activation language, or
examples of good completion predicates.

## Contents

- Goal Brief Template
- Outcome And Route Boundary
- Live Control Surface Template
- Goal State Boundary
- Role-Specific Contracts
- Blocker Pressure
- Pause And Stop Authority
- Subagent Slice Template
- Child Goal Activation Snippet
- Delegation Flow
- Fan-Out Rules
- Completion Predicate Examples
- Waiting Rule Examples

## Goal Brief Template

```text
/goal <finished state>

At completion:
- [R1] <observable required assertion>
- [R2] <observable required assertion>

Evidence:
- [R1] <named verification surface>
- [R2] <named verification surface>

Constraints:
Scope:
Out of scope:
Authoritative inputs, in order:
Live state surface: <path or none>
Outcome and assertion amendment authority:
Control surfaces and writers:
Delegated edit authority:
Re-anchor after interruption, compaction, or handoff:
If waiting on external state:
If stuck or failing:
If paused or stopped:
Subagents:
```

Use this form to turn broad intent into a durable completion contract. The first
line and `At completion` assertions describe the state that should exist after
all work is done, not the currently preferred commands or phases. Keep every
assertion concrete enough that another agent can verify it from named evidence.

For a small goal, write `Live state surface: none`. For long, delegated, or
stateful work, name one short surface that tracks changing status and execution
state. The outcome and assertion text stay stable there; assertion status,
evidence, owners, blockers, and next actions may change.

`Outcome and assertion amendment authority` normally names the user. An agent may
surface ambiguity or impossibility and propose a revision, but it does not
silently infer a new finish line from the latest failure or repair.

`Delegated edit authority` names exact surfaces and edits, or says `none`. Read
access and a request to propose changes do not grant write access.

Context ordering is part of the contract. Put the finished state, required
assertions, evidence standard, and constraints before owners, next actions,
history, or background. Current owners and next actions belong in the live state
surface, not in the durable objective. Assume the reader may skim, truncate, or
inspect only the head of the file.

For stateful work, list sources in precedence order and identify the one short
surface that owns changing state. Re-open those sources after compaction or
handoff. Do not make chat history, a long append-only ledger, or a stale status
marker compete silently with the current control surface.

## Outcome And Route Boundary

Keep three logical layers separate even when they share one file:

1. **Outcome contract:** finished state, required assertions, evidence standard,
   constraints, scope, exclusions, and amendment authority. This layer is stable.
2. **Acceptance ledger:** the same assertion IDs with current status and linked
   evidence. Assertion text is stable; status and evidence are mutable.
3. **Execution state:** observed state, unmet assertions, owners, running work,
   blockers, and next actions. This layer is deliberately replaceable.

Use this loop:

```text
read outcome and assertions
-> inspect current evidence and state
-> identify unmet assertions
-> choose the next route
-> execute or delegate
-> attach evidence to assertions
-> repeat or complete
```

Replanning changes the route, not the outcome. A prerequisite, repair, command,
phase, review, handoff, or monitor condition is progress unless the contract
explicitly names its observable result as a required final-state assertion. A
clause such as `then <action>` is not a completion predicate by itself.

When one route finishes, compare the new state with every parent assertion. If
any assertion remains unmet, choose the next result-producing route. Do not
promote the route just completed into the new goal.

## Live Control Surface Template

Use a live surface when work will span context windows, owners, active processes,
reviews, or several evidence-producing attempts. Markdown is sufficient when one
writer owns it and the sections remain distinct; structured data is preferable
when scripts enforce mutation rules.

```text
# Goal control surface

## Outcome contract (read-only except explicit amendment)
Outcome:
Required assertions:
- [R1] ...
- [R2] ...
Evidence standard:
Constraints and scope:
Amendment authority:

## Acceptance ledger
| ID | Status | Evidence | Notes |
|----|--------|----------|-------|
| R1 | unverified | | |
| R2 | unverified | | |

## Current execution state (mutable)
Observed state:
Unmet assertions:
Current owner:
Running now:
Next action:
External wait or blocker:
Last re-anchor:

## Decisions and amendments
- <timestamp, authority, old state, new state, reason>
```

Allowed assertion statuses should be few and explicit, for example `unverified`,
`passed`, `failed`, or `waived`. A waiver is a contract amendment and requires the
named authority; it is not a convenient substitute for missing proof.

Do not duplicate competing outcome contracts. The active goal should point to
this surface or contain the canonical static contract, and the live surface
should say which source wins.

## Goal State Boundary

Delegated `/goal` text is plain text until the child applies it with
`create_goal` in its own context. The controller keeps parent completion
authority, child completion is evidence for the parent, and nested fan-out stays
controller-owned.

## Role-Specific Contracts

Start every role from the [Goal Brief Template](#goal-brief-template), then keep
the parent outcome and assertion mapping explicit:

- Controller: `/goal <parent finished state>`. Own the stable parent contract,
  assertion ledger, amendments, routing, and completion decision. After every
  return, attach evidence to parent assertions, recompute the unmet set, and
  choose the next route.
- Worker: `/goal <slice postcondition>`. Name the parent assertion IDs advanced by
  the slice. Own local inspection, repair, validation, and evidence preservation
  until the slice postcondition is verified, rerouted, or needs a proven outside
  decision. Treat the parent outcome and controller-owned surfaces as read-only
  unless the contract grants an exact edit.
- Monitor: `/goal Observe <target> until <condition> and return <evidence>`. Name
  intervention triggers, drift, and cadence without taking implementation
  ownership. The monitor condition is not the parent completion condition unless
  the parent contract explicitly says it is.

For a long-running process, prefer a runner thread over letting the controller
become the runner. The runner owns the shell process, logs, artifacts, immediate
local recovery, and status packets. The controller owns the parent outcome,
assertion ledger, cadence, reroutes, and final evidence audit.

Example runner-thread slice:

```text
Parent outcome, read-only: <finished state>
Parent assertions advanced: <R1, R3>
/goal Produce terminal artifacts for <named run> that satisfy <slice postcondition>.

Slice outcome:
Scope: own the live shell process, local logs, artifact roots, immediate retry or
  recovery within the stated contract, and status packets.
Out of scope: changing the parent outcome or assertion text, widening the run
  contract, editing controller-owned control state, or declaring parent
  completion.
Evidence required: process state, artifact inventory, terminal summary, exact
  failure clusters, paths to logs, and the resulting assertion evidence.
If stuck or failing: preserve evidence, isolate the smallest failing slice, keep
  independent safe work moving, and ask the controller only for a decision that
  cannot be made locally.
If paused or stopped: stop only owned work, preserve logs and artifact roots,
  neutralize monitors that would restart the run, and return a resume packet
  without declaring parent completion.
```

## Blocker Pressure

Do not write goal contracts that make `BLOCKED` feel like an acceptable finish
line. A blocker is a claim that must be compressed until it turns into one of
three things: a concrete local next action, a reroute to a better owner, or a
specific external decision that cannot be made from the workspace.

When using goal tools, mark blocked only when the same blocking condition has
held for at least three consecutive goal turns and no meaningful local progress
remains possible. If any local repair, bounded validation, owner reroute, or
narrower question can still move an unmet assertion, keep the goal active and
take that step. Do not mark complete for partial, indirect, stale, or missing
evidence.

Strong contracts tell the worker what to do when stuck:

- inspect the exact failure;
- name what was tried and what it proved;
- execute the smallest reversible repair still inside scope;
- use a bounded validation;
- ask the controller only when the remaining decision is genuinely outside the
  worker's authority.

Stuck is not a place to rest. It is pressure to convert uncertainty into the
next local action, a better owner, or a proven external dependency.

## Pause And Stop Authority

An explicit user pause or stop overrides monitor prompts, heartbeat prompts, and
older continuation instructions. It does not prove the original objective is
complete.

When a live goal is paused:

- stop only owned workers, scheduled tasks, and monitors;
- verify no owned worker remains;
- preserve logs, result roots, PR state, or other resume evidence;
- mark interrupted artifacts out of strict result counts when applicable;
- write a resume packet with stopped process ids, roots, counts, and next safe
  action;
- preserve the stable outcome and assertion ledger unchanged;
- do not call the parent objective complete unless the user accepts the paused
  state as the endpoint;
- do not call it blocked solely because execution is paused.

If the tool surface has no paused status, leave the goal contract honest in the
turn output and prevent automation from restarting the stopped work.

## Subagent Slice Template

Use this as a contract. Active goal state exists only after the child applies
goal tools in its own context. Delegated messages to other threads and spawned
subagents treat `/goal` text as plain text until the child applies it. If the
child needs active goal state, ask that child to call `create_goal` for its own
slice outcome.

```text
Parent outcome, read-only:
Parent assertion IDs advanced:
Slice outcome or postcondition:
Integration target:
Allowed files or systems:
Out of scope:
Inputs to inspect:
Live state surface and writer:
Delegated edit authority, or none:
Expected output:
Evidence required and assertion mapping:
Done condition for this slice:
Constraints:
Return one kind: completed, needs_input, waiting_external, or failed.
```

The controller should keep ownership of the parent goal. A subagent completes
only its slice and returns evidence for integration. It may adapt its own route,
but it may not rewrite the parent outcome or parent assertion text. `failed`,
`needs_input`, and `waiting_external` are unfinished returns, not successful
slice outcomes. The controller preserves parent-goal judgment, asks unblock
questions, routes execution to a worker or fresh worker, and records any
concrete dependency that remains.

## Child Goal Activation Snippet

If a separate thread or subagent truly needs its own active goal, include an
explicit self-application instruction like this:

```text
First action: if goal tools are available, call create_goal with this slice
outcome: <observable slice postcondition>.
Then call get_goal and confirm the active slice outcome before working.
Treat the parent outcome and assertion text as read-only context.
When the slice outcome is verified, call update_goal with status complete and
return evidence mapped to the named parent assertion IDs.
```

A controller-sent delegation should still include the slice contract so the work
is useful even when no active goal state exists in the child context.

## Delegation Flow

Use this flow when the parent goal has independent slices:

1. Controller reads the stable parent outcome and acceptance ledger.
2. Controller derives slices from currently unmet parent assertions, not from the
   latest symptom alone.
3. Controller gives each child the parent outcome as read-only context, named
   parent assertion IDs, one slice postcondition, scope, integration target, and
   evidence requirements.
4. Child applies its own goal if goal tools are available and chooses its local
   route.
5. Child returns status, changed files or findings, checks run, evidence mapped to
   parent assertion IDs, and unresolved risks.
6. Controller independently reviews the evidence against the slice condition and
   parent assertions.
7. Controller updates assertion status and current execution state, recomputes
   the unmet set, and chooses the next route.
8. Controller completes the parent only when every required assertion is
   verified or explicitly waived by the named authority.

A child can say its slice is done. That return never implies that the parent is
done, and a predefined slice list is not itself proof that the decomposition
covered the full outcome.

For long-running execution, delegation is not optional ceremony. It preserves
judgment. Create the runner thread before launch when the run will take longer
than a normal turn, needs periodic wakeups, or may require local recovery while
the controller sleeps.

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

Use concrete predicates in place of `make progress`, `clean it up`, `look into
it`, `run the command`, or `then do the next step`, unless the user explicitly
wants exploration or action-only work.

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
