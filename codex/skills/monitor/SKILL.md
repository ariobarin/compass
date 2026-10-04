---
name: monitor
description: Supervise long-running work through health checks, recovery, and terminal evidence while keeping waits and unchanged logs outside model context. Use when a process, agent, or external wait needs continued attention beyond a single status check.
---

# Monitor

Keep the clock and unchanged output outside model context. Wake to decide or
act. Monitoring includes recovery within the task's authority.

## Establish The Watch

Identify the real target, terminal evidence, signs of progress or failure,
authorized recovery, and any deadline. Keep the output location and last known
good state available so a handoff can resume the watch. Record only what is
needed to recover; update it on meaningful transitions.

Do not claim a watch is active without an observable target. Identify the
missing evidence surface if one prevents supervision.

## Choose The Watcher

Prefer a native wait, callback, notification, or one bounded watcher command.
Otherwise write the smallest surface-specific loop. Let it sleep, sample, and
retain bounded state outside the conversation. Return only on:

- terminal evidence;
- an actionable anomaly;
- a heartbeat needed to establish liveness;
- explicit cancellation;
- a deadline requiring a fresh decision.

Prefer events over timers. Use heartbeats or a watchdog only when a missed
wakeup is a real risk. Never send unchanged polls or full logs through the
model, or wrap a working native watch in a second polling loop.

Delegate when checks need sustained interpretation or concurrent attention.
Give a fresh agent the objective, evidence pointers, recovery authority, and
return condition. The delegate owns the loop, including authorized repair and
resumption. Keep one repair owner when watches overlap.

## Supervise To Completion

At each wake:

1. Recover the watch context and inspect the smallest useful delta.
2. Distinguish healthy progress, a stall, failure, and terminal evidence.
3. If healthy, adjust cadence when risk or progress changed, then wait again.
4. If recoverable within authority, diagnose, repair, restart or resume, update
   the watch context, and keep watching.
5. Escalate only when recovery exceeds authority, needs a material decision, or
   has exhausted credible in-scope repairs.

Judge liveness from evidence the target can actually expose. Silence alone
cannot establish health. Completion requires terminal evidence; elapsed time
and the absence of errors cannot establish it.

Explicit cancellation ends the watch. A deadline returns control for a fresh
decision; it never proves completion or failure.

Source provenance lives in [references/sources.md](references/sources.md). Do not
load it during normal monitoring.
