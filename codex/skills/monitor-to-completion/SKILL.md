---
name: monitor-to-completion
description: Wait on one observable condition in a bounded command and return one compact result.
---

# Monitor To Completion

Use this skill only for mechanical waiting. The script owns the clock. The
parent owner chooses the condition, timeout, and response.

## Contract

- Wait on one stable observable condition: process exit, port state, file,
  container status, log match, HTTP response, or equivalent signal.
- Prefer a native wait. Otherwise poll inside one blocking command, never across
  model turns.
- Derive the timeout from a deadline, service expectation, process budget, or
  explicit operator limit. Do not use arbitrary poll counts.
- Exit distinctly on success, target failure, and timeout.
- Sample diagnostics without streaming repetitive logs into context.
- Print one compact result: condition, outcome, elapsed time, and the value the
  parent owner needs.
- Return the result to the execution or goal owner. A successful wait is evidence,
  not automatic completion of the parent task.

## Timeout

A timeout wakes the parent owner for judgment. Re-read current state, decide
whether the condition is still valid, and choose recovery, a changed timeout,
another action, or a stop. Do not silently relaunch the same wait.

Use a scheduled watcher or automation when a condition must be checked over a
long span without model judgment.
