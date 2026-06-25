# Runner Handoff Template

Use this when a benchmark run, recovery loop, or monitor handoff may move
between controller and runner owners. Put the control contract first so the
next owner can act without reading the full history.

## First-Screen Contract

Front-load these fields:

- objective;
- done means;
- runner owner;
- controller owner;
- current next action;
- stop conditions;
- validity contract;
- recovery stance.

## Template

```text
objective: <exact result set to produce>
done means: <terminal, countable, comparable artifact condition>
runner owner: <thread, worker, process label, or explicit unassigned state>
controller owner: <parent thread or person keeping completion authority>
current next action: <the next command, monitor check, recovery action, or wait>
stop conditions: <only the concrete states that justify stopping>
validity contract: <arms, model, task set, timeout, scorer, stack, provenance>
recovery stance: invalid rows are debug-and-repair work until protocol evidence
  proves otherwise

state now:
- active labels:
- active processes:
- latest countable rows:
- invalid rows:
- missing rows:
- dominant error cluster:
- latest task ids:

runner instructions:
- own shell process, stdout, stderr, logs, immediate retries, and artifact
  preservation
- pause only the smallest poisoned labeled slice before it corrupts provenance
  or comparability
- keep unrelated comparable work moving
- ask the controller only after local recovery paths are exhausted or a
  benchmark-validity decision is truly needed

controller instructions:
- keep completion authority
- verify runner evidence before accepting status claims
- reroute failures into concrete next actions
- reject polished blocker reports while safe result-producing work remains

evidence and history:
- handoff path:
- artifact roots:
- monitor command:
- report command:
- relevant prior decisions:
```

## Use Notes

- The runner owns local execution and immediate recovery, not parent-goal
  judgment.
- The controller owns cadence, scope changes, review paths, and completion.
- If a handoff hides owners, stop conditions, or next action below the first
  screen, rewrite it before passing control.
