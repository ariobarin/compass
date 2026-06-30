# Controller Playbooks

Use this reference when the routing choice is unclear. The point is not to
stack every coordination skill at once. The point is to pick the smallest
surface that keeps ownership and evidence clear.

## Choose The Surface

- Use `using-codex-goals` when the main problem is setting or preserving a
  durable objective in the current context.
- Use `subagent-driven-development` when a real implementation plan exists,
  tasks are mostly independent, and the work should stay in the same session.
- Use `orchestration-controller` when the work is mostly routing, monitoring,
  review fallback, or long-running execution that needs a separate runner owner.

## Common Shapes

### Goal only

Use this when one context can still own execution directly.

- one objective;
- one owner;
- evidence gathered in the current thread;
- no separate runner or monitor needed.

### Goal plus same-session subagents

Use this when the objective is durable but the execution slices are bounded and
independent.

- parent keeps the goal and completion authority;
- fresh implementers own the local slices;
- reviews happen before the parent advances;
- work should still fit the current session.

### Controller plus runner

Use this when the result depends on execution that may outlive one turn or one
context.

- controller owns the contract, cadence, reroutes, and evidence audit;
- runner owns the shell process, logs, local recovery, and status packets;
- the controller does not become the runner;
- the goal, if any, stays with the context that activated it.

## Switch Signals

Switch from `using-codex-goals` to `orchestration-controller` when:

- the next job is mostly wakeups, monitoring, or rerouting;
- a long-running process needs a separate owner;
- review or CI waiting now dominates the task.

Switch from `subagent-driven-development` to `orchestration-controller` when:

- the work stops being same-session implementation sequencing;
- the parent is mostly managing blocked workers or review loops;
- execution should move to a runner thread instead of another bounded slice.

Switch from `orchestration-controller` back to worker execution when:

- a concrete owner and next action are clear again;
- a fresh worker can take over a bounded slice;
- the controller no longer needs to hold the level above execution.
