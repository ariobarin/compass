---
name: input-token-economy
description: In long agent sessions, accumulated input often dominates cost. Read targeted slices, keep the working set small, and split long sessions deliberately.
---

# Input Token Economy

On a coding agent, accumulated input often becomes the largest cost in long
sessions. Each turn may carry a large working set: instructions, tools, file
reads, tool outputs, and running history. Compaction, caching, and response
state can reduce what is charged or re-sent, but every new line dragged into
the working set still has to be paid for somewhere. Output and reasoning effort
matter too, especially when quality permits smaller answers or lower reasoning.
This skill focuses on the cost that quietly compounds: how much context you
carry per turn and how many turns you keep carrying it.

This skill is about spending input on purpose. Not about being stingy with the
answer.

## Read Slices, Not Whole Files

Most questions about a file are about a part of it. Read that part.

- Prefer a targeted read over a full one: the part you need, an end, a known
  line range, or the matching lines. Go whole-file only when you truly need the
  whole file, and say why.
- One good read beats several full ones. If you will need the same large file
  more than once, read the slice you need, or extract the relevant region once,
  rather than re-reading the whole thing each turn.
- Keep big output out of the context. Tail long logs, count and summarize, or
  write results to a file and read the summary back. A 50k-line dump read
  across five turns is paid for five times.

The test: could you have answered from the last forty lines, or the matched
lines, instead of the whole file? Then read those.

## Keep Sessions Short Enough To Re-Send

A long thread is expensive by construction, because the growing tail tends to
stay in the working set. A session twice as long is not twice the cost; late
turns often cost more than early ones, since they carry more accumulated
context.

- Start a fresh session for a new sub-goal. Restating the small piece of
  context a new task needs is cheaper than carrying the whole history of the
  last one forward.
- When a thread has grown large and the work shifts, summarize the result so
  far and continue lean, rather than dragging the full transcript along.
- Prefer a subagent or a fresh run for self-contained chunks of work only when
  you can preserve the work cleanly. Carry a compact handoff with the objective,
  constraints, branch or file state, pending verification, and known risks. For
  governed implementation splits, use `subagent-driven-development`. When
  durable goal state matters, include the objective, completion evidence, and
  owner in the handoff instead of relying on thread memory.

The frontier case is the monitoring thread: one long-running session that
watches something can dwarf everything else, because each watch cycle is a full
turn. The monitor-to-completion skill handles that one directly.

## What This Rules Out

- read-then-reread: pulling the same large file whole across multiple turns.
- dump-into-context: pasting a huge log or directory listing into the thread
  when a count, a tail, or a grep would have answered.
- one-thread-forever: running unrelated sub-goals in a single ever-growing
  session just because it is the one already open.
- optimize-only-the-visible-axis: trimming the answer while repeatedly loading
  large irrelevant input. Lower reasoning effort and shorter output can be valid
  when quality permits, but they do not fix an oversized working set.

## Judgment Over Checklist

The model is the part that thinks. The expensive part is everything it may have
to keep looking at while the session grows. Read the slice you need, keep the
thread to the work at hand, and let finished context go. Spend input like it is
often the bill, because in long agent work it often is.
