---
name: monitor-to-completion
description: "Run waits and monitoring to completion in one blocking script. Never poll in a sleep loop: each wake re-sends the whole context."
---

# Monitor To Completion

When the task is to wait for, watch, or babysit something that finishes on its
own, a build, a container, a benchmark run, a log tail, a process, a deploy, a
rate limit clearing, your default is one command that runs to completion and
reports once. Not a loop where you sleep, re-check, and sleep again.

The reason is cost, not correctness. A polling loop can produce the right
answer. But every wake is a full model turn: the entire conversation, files,
tool outputs, and reasoning history are sent to the model again as input. One
wait that polls itself thirty times pays for thirty full-context turns. On a
frontier model with a long thread, that single habit can dwarf the rest of the
session bill. Waiting is cheap when a script does it and expensive when the
model does.

## The Posture

If you are about to write Start-Sleep, sleep, setTimeout, "check again in",
"retry until", or a while loop that re-reads the same source, stop. Ask whether
this can run to completion in one shell call. Almost always, it can.

The model's job is to decide what to wait for, write the wait, and read the
result. The model's job is not to be the timer.

## How To Wait Instead

Run the wait inside the command, then return a short result.

- Block on the real condition, polling inside the script rather than across
  turns. Wait on the PID, the port, the file, the container status, the log
  line, or the HTTP 200. Exit when it is true or the timeout fires.
- One script, one report. The command sleeps, checks, and prints a short final
  summary: done or failed, how long, and the one number the user actually
  wanted. Long logs stay out of the context; summarize them inside the script.
- Bound it. Always carry a timeout and a failure exit so the turn ends even if
  the condition never holds. A hang is worse than a poll.
- Use the platform's wait where one exists. docker wait, kubectl wait,
  Wait-Process, Wait-Event, a single curl with --retry, or tail -f piped to
  grep -m1. These exist precisely so you do not hand-roll a sleep loop.

If you genuinely need to re-check something at intervals over a long span, that
is a scheduled job or a watcher process, not a model turn repeated.

## When A Loop Across Turns Is Actually Fine

Rare, and the exception proves the rule. A loop across turns is defensible only
when each wake must do real model work a script cannot: read fresh results,
judge quality, and decide the next variant. Even then, do the waiting inside one
blocking call and let the wake be about the decision, not about the passage of
time. If a wake does nothing but sleep and re-read, fold it into the script.

## What This Rules Out

- sleep-and-recheck: Start-Sleep then Get-Content then Start-Sleep, repeated,
  to watch a file or process grow.
- retry-by-pinging: polling an endpoint across turns until it responds, when
  one curl with --retry or a single wait does it.
- babysit-by-re-read: re-reading the same log every turn to see whether it
  finished, instead of one command that exits when it does.
- model-as-timer: using the model turn as the clock. The script owns the clock.

## Judgment Over Checklist

The stance is simple: if it can finish on its own, finish it in one command and
report once. Keep the model for deciding and judging, not for counting seconds.
When you catch yourself writing a sleep, that is the signal to move the wait
into the script.
