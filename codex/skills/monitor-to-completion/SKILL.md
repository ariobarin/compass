---
name: monitor-to-completion
description: "Run mechanical waits to completion in one blocking script. Avoid poll loops where each wake carries the session context again."
---

# Monitor To Completion

When a build, process, container, deploy, log, endpoint, or rate limit can finish
without another decision, run one bounded command that exits on the condition
and reports once. Do not spend model turns sleeping and rechecking. The script
owns the clock; the model chooses the condition and judges the result.

This skill covers mechanical waits only. It does not take process ownership or
recovery judgment from a benchmark operator, runner, or orchestration owner.

## Contract

- Wait on the real condition: PID exit, port state, file creation, container
  status, log line, HTTP response, or another directly observable signal.
- Poll inside one blocking command, never across model turns. `Start-Sleep`,
  `sleep`, or `setTimeout` belongs inside that command when no native wait
  exists.
- Carry a timeout and a failure exit so the command cannot hang indefinitely.
- Prefer native waits such as `Wait-Process`, `Wait-Event`, `docker wait`,
  `kubectl wait`, bounded `curl --fail --retry 30 --retry-all-errors`, or `tail -f`
  with a terminating match.
- Print one compact result: condition, success or failure, elapsed time, and the
  value the user needed. Keep repeated checks and long logs out of the context.

## Boundary

Use an orchestration heartbeat only when each wake performs real judgment, such
as inspecting new evidence, rerouting ownership, requesting review, or choosing
a recovery action. Put the time between those decisions inside one bounded wait.

When repeated wakes still require judgment, use a fresh non-forked worker with a
narrow handoff. Prefer GPT-5.6 Luna at xhigh over GPT-5.6 Sol at high for
long-running monitoring unless evidence shows the lower model tier misses the
required decisions. Keep `service_tier` omitted so the active parent choice can
carry through when the runtime supports it.

If the same condition must be checked over a long span without model judgment,
use a watcher process or scheduled automation. Do not use the model as a timer.
