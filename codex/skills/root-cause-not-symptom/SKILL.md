---
name: root-cause-not-symptom
description: Diagnose the mechanism and owning boundary before repairing bugs, errors, regressions, and failing tests.
---

# Root Cause, Not Symptom

Repair the mechanism that produces the failure. This skill exists because a
visible error invites guards, retries, catches, rewrites, and suppressions that
make the symptom disappear while the broken ownership remains.

The first deliverable is a causal model strong enough to locate the repair.

## State The Causal Model

Before production edits, state:

> The observed symptom is S. The supported cause is X. The repair belongs at Y
> because Z. The evidence is E.

`X` names the producing mechanism. `Y` names the narrowest ownership boundary
that can correct it. `Z` explains why that boundary owns the behavior. `E`
distinguishes observation from inference.

Some failures have interacting or independent causes. Name the causal chain or
cause set when one site cannot truthfully explain the result.

When the statement is not yet supportable, investigate. Trace inputs, state,
ownership, execution flow, and the earliest divergence from the required
contract.

## Let Recurrence Reopen The Model

A recurring symptom is new evidence. Reopen the causal model before adding
another layer. Determine whether:

- the first cause was incomplete;
- another independent cause produces the same symptom;
- the repair landed outside the owning boundary;
- stale state or a different runtime path bypasses the repair;
- the verification never exercised the real failure path.

A second patch begins with a changed explanation, not a larger pile of guards.

## Repair The Owning Boundary

Make the smallest coherent change that removes the supported cause while
preserving required behavior. Verification should reproduce the original path
from a clean state and show that the mechanism, not only the visible message,
changed.

Crisp boundaries remain firm:

- Error suppression is not a repair when the error source remains.
- A rewritten requirement is not evidence that a broken implementation became
  correct.
- A component swap follows diagnosis; it does not substitute for diagnosis.

## Subtractive Review

After the repair works, inspect the changed and neighboring surface:

- Which guard, wrapper, fallback, branch, state, or compatibility path became
  obsolete?
- Did the patch introduce a second source of truth?
- Did an existing abstraction already own the behavior?
- Is the changed surface broader than the causal boundary requires?
- Can the same behavior remain with fewer maintained concepts or states?

Line reduction is useful evidence, not the target. The target is a system with a
simpler truthful explanation.

## Completion Evidence

Report the symptom, causal model, evidence, owning boundary, repair, focused
checks, clean-state reproduction, removed obsolete machinery, and any remaining
unverified cause.
