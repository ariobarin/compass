---
name: specialist-review
description: Route an explicit specialist review request through a neutral, evidence-first reviewer handoff.
---

# Specialist Review

Use this skill only when the user invokes `$specialist-review`, explicitly asks
for coordinated specialist review, or requests a clean specialist handoff.

Do not use it for ordinary PR review. Use `pr-review-loop` for that workflow.

## Posture

This is a routing skill, not a review persona. Its deliberate bias is against
coordinator contamination. Remove the invoking agent's preferred conclusion,
defense, specialist roster, and assumptions before review begins.

Specialists are independent witnesses, not a committee expected to converge.
Disagreement is useful evidence. Consensus is an observed result, never a prompt
instruction or a summary invented by the coordinator.

Launch `reviewer` with a neutral handoff. Do not perform the review, choose the
specialists, predict verdicts, defend the target, or imply consensus. The
reviewer owns specialist selection and topology under its own contract.

Require independent specialist judgment, evidence-backed findings, and no claim
of agreement unless the returned reviews support it.

## Handoff

```text
Review target:
[target locator]

User request:
[exact request]

Scope:
[review scope]

Evidence:
[raw checks, logs, screenshots, output, artifacts, or "none provided"]

User-stated hard limits:
[verbatim limits or "none provided"]

Review requirements:
[independent judgments, evidence-backed findings, no fabricated consensus]
```

Do not invent operational limits or favorable framing. Label unavoidable context
as unverified.

`reviewer` is required by the Compass bundle. If it cannot run, name the missing
capability and report that coordinated specialist review failed. Do not claim
the review completed.
