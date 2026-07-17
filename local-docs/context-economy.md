# Context Economy

Context economy is a property of the system, not a recurring burden placed on
the worker.

The retired `input-token-economy` skill correctly identified repeated full-file
reads, log dumps, growing conversations, and model-turn polling as expensive.
A callable reminder was the wrong durable surface. The economical route should
be built into how Compass structures work.

## System Shape

- Read the smallest complete slice that answers the question.
- Keep large logs outside model context and return compact diagnostics.
- Use principal-authored anchors and checkpoints so completed conversation can
  be released.
- Start fresh, non-forked delegates for self-contained assignments.
- Give each delegate only the anchors and evidence target it needs.
- Put mechanical waits inside one bounded command.
- Use a fresh narrow monitor when periodic observation needs limited judgment.
- Archive completed workstreams instead of carrying their narrative forever.

## Continuity Over Transcript

A long transcript is not durable project state. It is expensive, hard to audit,
and vulnerable to compaction loss.

The stronger test is whether a fresh context can resume from the named goal,
anchors, current ledger, and checkpoint. When it can, context can be replaced
without losing the work's logic.

## Reduction Standard

Optimize maintained surface rather than visible answer length. Prefer fewer
sources of truth, states, branches, wrappers, dependencies, and repeated reads
when the same capability remains intact.
