# Goal Contracts

Load this reference when a task needs copyable `/goal` prompts, subagent
handoffs, or examples of good completion predicates.

## Goal Brief Template

```text
/goal <objective>

Done means:
Scope:
Do not touch:
Evidence required:
If waiting:
If blocked:
Subagents:
```

Use this form to turn broad intent into a durable contract. Keep every field
concrete enough that another agent could verify it later without guessing.

## Subagent Slice Template

Use this as a contract, not as an attempt to transfer active Codex goal state.
In observed Codex behavior, delegated messages to other threads and spawned
subagents did not interpret `/goal` as a slash command. If the child needs
active goal state, tell it to call `create_goal` for its own slice.

```text
Parent goal:
Slice:
Allowed files or systems:
Forbidden scope:
Inputs to inspect:
Expected output:
Evidence required:
Done condition for this slice:
Do not:
Return one status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED.
```

The controller should keep ownership of the parent goal. A subagent completes
only its slice and returns evidence for integration.

## Delegation Flow

Use this flow when the parent goal has independent slices:

1. Controller derives slices from the parent completion predicate.
2. Controller gives each subagent one slice, allowed scope, forbidden scope, and
   evidence requirements.
3. Subagent inspects only the inputs needed for its slice.
4. Subagent returns status, changed files or findings, checks run, evidence, and
   unresolved risks.
5. Controller reviews the evidence against the slice done condition.
6. Controller integrates results across slices and decides whether the parent
   goal is complete, needs more work, or is still waiting.

The controller should not outsource final parent completion. A subagent can say
its slice is done, but only the controller can verify that every slice and
cross-slice requirement satisfies the parent goal.

If a separate thread or subagent truly needs its own active goal, include an
explicit instruction like this:

```text
If goal tools are available, call create_goal with objective: <slice objective>.
Then call get_goal and confirm the active objective before working. When the
slice is complete, call update_goal with status complete.
```

A controller-sent delegation should still include the slice contract so the work
is useful even when no active goal state exists in the child context.

## Fan-Out Choice

Choose the orchestration surface deliberately:

- Use subagents for bounded worker slices that should report back to the
  controller. Spawned subagents can create their own goals, but they could not
  spawn nested subagents in observed behavior.
- Use separate threads for durable, user-visible work streams that may need to
  persist independently in the sidebar.
- For tree-shaped work, keep fan-out controller-owned. Let children return
  proposed slices, then have the controller spawn the next layer.

## Completion Predicate Examples

Good predicates name the finish line and the proof:

- All named PRs are open, green, reviewed, and linked in the final report.
- Each listed repo has a current diff audit, a matching `MODIFICATIONS.md`, and
  verification that unrelated changes were not touched.
- The report exists at the requested path, covers each named comparison axis,
  and has been checked for formatting or repo-specific style constraints.

Avoid predicates like "make progress", "clean it up", or "look into it" unless
the user explicitly wants exploration only.

## Waiting Rule Examples

Use waiting rules for external systems:

- If waiting on PR review, keep the goal active and poll for new review comments
  or approval signals.
- If waiting on CI, keep the goal active until checks pass, fail with actionable
  logs, or time out under the user's stated policy.
- If waiting on a benchmark, preserve artifacts and report the next expected
  checkpoint instead of marking complete early.
