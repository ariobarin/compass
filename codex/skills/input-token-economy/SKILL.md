---
name: input-token-economy
description: Input dominates agent cost. Read targeted slices not whole files, keep the working set small, and split long sessions instead of one ever-growing thread.
---

# Input Token Economy

On a coding agent, input is almost the entire bill. Every turn re-sends the
whole context to the model: instructions, tools, file reads, tool outputs, and
the full running history. Output, reasoning included, is usually a rounding
error next to it. Caching helps the stable prefix, but every new line dragged
in is paid for on the turn you add it and again on every turn after. So the two
things that cost are how much you read per turn and how many turns you run.

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

A long thread is expensive by construction, because the growing tail is sent
again every turn. A session twice as long is not twice the cost; late turns
cost more than early ones, since each carries everything before it.

- Start a fresh session for a new sub-goal. Restating the small piece of
  context a new task needs is cheaper than carrying the whole history of the
  last one forward.
- When a thread has grown large and the work shifts, summarize the result so
  far and continue lean, rather than dragging the full transcript along.
- Prefer a subagent or a fresh run for self-contained chunks of work. They
  start with a small context and return a short result, instead of inflating
  the main thread.

The frontier case is the monitoring thread: one long-running session that
watches something can dwarf everything else, because each watch cycle is a full
turn. The monitor-to-completion skill handles that one directly.

## What This Rules Out

- read-then-reread: pulling the same large file whole across multiple turns.
- dump-into-context: pasting a huge log or directory listing into the thread
  when a count, a tail, or a grep would have answered.
- one-thread-forever: running unrelated sub-goals in a single ever-growing
  session just because it is the one already open.
- optimize-the-wrong-axis: trimming the answer or lowering reasoning effort to
  save tokens, when the real cost is input the user never asked to re-send.

## Judgment Over Checklist

The model is the part that thinks. The expensive part is everything it has to
look at again each turn. Read the slice you need, keep the thread to the work at
hand, and let finished context go. Spend input like it is the bill, because it
is.
