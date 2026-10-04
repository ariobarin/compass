---
name: retro
description: Learn from a coding session's corrections, failed attempts, and wasted work. Use when asked for a retrospective or when repeated interventions warrant a durable change to the agent's environment.
---

# Retro

Improve the coding agent's environment so the next run needs less correction.
Design the repo so a change that looks right from one file is right for the
whole repo.

## Start With The Intervention

Read the primary record for the requested session, defaulting to the current
one. Trace actual corrections, failed approaches, and costly searches back to
what the agent could see and chose. Separate the cause from its symptoms.

Select lessons that would change a future decision. Repetition strengthens the
case; one consequential failure can justify a fix. Say when the record does
not support a durable lesson.

## Fix The Environment

- Prefer eliminating a mistake through architecture, ownership, types, or a
  single source of truth. Remove obsolete paths an agent would copy.
- Read the repo's existing lint, test, and CI commands before proposing
  enforcement. An unwired or broken check is the finding, not a reinvention.
  Weigh new enforcement against its recurring cost, using `$test-for-risk`
  when available. An absent check alone is not evidence that one belongs.
- Reserve prose for judgment the environment cannot enforce or information it
  cannot reveal. Repair a navigation pointer or the owning document before
  adding another rule. Delete instructions made redundant by the fix.
- Keep project lessons in the project. A recurring, selectively invoked
  capability may warrant a skill; use `$write-a-skill` when available.

## Return The Smallest Durable Fix

Rank the few consequential findings by expected benefit. Give the session
evidence, the cause, the proposed change at its owning boundary, and why it
should prevent a repeat. Recommend changes by default; implement when the
user's request or existing session authority includes them.

Validate an applied fix against the recorded failure. A new or repaired check
must catch that mistake. Distinguish proposed changes from proven ones, and
report no change when the evidence earns none.

Source provenance lives in [references/sources.md](references/sources.md). Do not
load it during normal retrospectives.
