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

## Goal Handoff Ablation

Keep these behaviors separate when testing or designing a handoff:

| Question | Test | Observed behavior | Use when |
| --- | --- | --- | --- |
| Can `/goal` be transported? | Send `/goal ...` through thread or subagent delegation. | No. It arrives as text or delegated input. | Avoid relying on slash-command transport. |
| Can the child own a goal? | Tell the child to call `create_goal`, then `get_goal`. | Yes, when goal tools are available in that context. | Use when the child needs persistence in its own context. |
| Can the child work from a contract? | Send a slice with scope, evidence, done condition, and return status. | Yes. The child can report evidence without active goal state. | Use for bounded subagent slices and controller-owned parent goals. |

Do not stop after proving slash-command transport fails if the actual question
is whether the child can create and own its own goal. Test self-activation
separately.

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

## Observed Patterns

- Sending `/goal ...` through delegation: child receives text, not active goal
  state.
- Sending a slice contract without active goal state: child can execute the
  bounded work and return status with evidence.
- Explicitly telling the child to call `create_goal`: child can create and later
  complete its own local active goal when goal tools are available.

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
