---
name: monitor-to-completion
description: Wait on one observable condition inside one bounded command and return one compact terminal result.
---

# Monitor To Completion

Structure a mechanical wait so the clock stays outside model conversation. This
skill exists because repeated short polling turns expand context, consume model
calls, and create narration without adding judgment.

The parent chooses the condition, deadline, and response policy. One blocking
command owns the wait.

## Wait Contract

Wait for one stable observable condition, such as:

- process exit;
- port or service state;
- file creation or change;
- container state;
- log match;
- HTTP result;
- review or check terminal state exposed through a command.

Prefer a native wait. Otherwise poll inside one command. Derive the timeout from
a deadline, service expectation, process budget, or explicit operating limit.

Return distinct outcomes for success, target failure, and timeout. Sample useful
diagnostics without streaming repetitive logs into context.

## Compact Result

Print only what the parent needs:

- condition;
- outcome;
- elapsed time;
- final observed value;
- compact diagnostic on failure or timeout.

A successful wait is evidence for the parent objective. The parent decides what
that evidence means.

## Judgment Boundary

Use a fresh narrow `progress-monitor` agent when periodic checks require limited
interpretation, anomaly detection, or escalation. Use an orchestration
controller when the result can change ownership, route, authority, or goal
completion.

A timeout returns judgment to the parent. Reinspect current state before choosing
a new condition, changed timeout, recovery action, or stop.
