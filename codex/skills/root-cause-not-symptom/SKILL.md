---
name: root-cause-not-symptom
description: Force root-cause-first on bugs, errors, and failing tests. Use before any patch, suppress, swap, retry, or premature done call on a symptom.
---

# Root Cause, Not Symptom

A symptom is what you see: an error, a failing test, a wrong value, a strange
output. The cause is the mechanism, one or more layers down, that produces it.
You fix causes. You do not patch symptoms. A bandage stops the bleeding for a
minute. The cut is still open. This skill exists to make you get the stitches.

The posture is the point: name the cause before you touch code. If you cannot
state the mechanism in one sentence, you do not understand the bug yet, and
investigating is the correct next move, not editing. The discipline below is
firm because every item is a documented way agents ship a fix that does not
hold. It is orientation, not a cage.

## Name The Cause Before The Fix

Before you write, edit, delete, or swap a line, state in one sentence:

  The cause is X. The fix lives at Y. Because Z.

- X is the mechanism, not the symptom. "The string double-quotes a JSON value,
  so it is escaped on serialization" is a cause. "Quotes are escaped" is a
  symptom.
- Y is the single site or boundary that owns the behavior, not the site that
  displays it. If you cannot point to one site or boundary, the cause is not
  understood yet.
- Z is why that site owns the behavior.

If you cannot fill X, Y, and Z, stop and investigate. Patching a cause you
cannot name is the exact failure this skill prevents.

## The Recurrence Rule

If the same class of symptom returns after your fix, your fix was symptomatic.
Do not patch again.

A returning symptom is a signal, not a todo. Reopen the cause statement,
assume your first cause was wrong, and look one layer deeper. One fix per
cause. A second fix for the same symptom is reason to re-examine the cause.

## What This Rules Out

These are the recurring shapes of the failure. Recognize them and refuse them.

- fix-output-not-cause: editing the producing string or display layer to hide
  a symptom while the data contract underneath is wrong.
- patch-and-pray: stacking a second guard on a guard that "did not fully work."
  Layers mean you missed the cause.
- declare-done-on-disappearance: calling it fixed because the symptom vanished
  in one run. Symptom gone is not cause fixed. Re-run from a clean state and
  confirm the cause is gone.
- suppress-the-signal: catching, swallowing, filtering, or defaulting past the
  error instead of removing its source.
- swap-instead-of-diagnose: rewriting the format or delivery shape, or swapping
  a component, because the real fix is hard. Diagnose first; swap only if
  diagnosis says swap.
- react-to-surface-signal: reshaping behavior around a heuristic you inferred
  ("these look simple") instead of the stated requirement. Re-read the spec.
  The spec beats your read of the surface.
- enshrine-as-policy: rewriting docs, evals, or READMEs to make a symptomatic
  fix permanent instead of reverting it.

## When To Stop And Surface

- You have written more than one fix for the same symptom. Stop.
- The spec is ambiguous or self-contradictory. Ask; do not infer and proceed.
- Fixing the cause would delete or reshape behavior the user did not ask to
  change. Confirm scope first.

## Judgment Over Checklist

The lists above are guardrails against known failures, not a replacement for
thinking. Keep the stance: causes first, symptoms second, and a returning
symptom is always a reason to go deeper, never a reason to patch again.
