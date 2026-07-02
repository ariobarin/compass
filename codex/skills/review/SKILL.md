---
name: review
description: Route explicit multi-specialist, clean-handoff, or contaminated-context review requests to the reviewer coordinator with a neutral handoff.
---

# Review

Use this skill only when the user invokes `$review`, explicitly asks for
multi-specialist review, asks for a clean handoff, or known contaminated context
would weaken direct review.

Your job is not to review or choose specialists. Launch `reviewer` with a clean
handoff.

Give `reviewer` only:

- target: repo, PR, branch, commit range, patch, files, artifact paths, or URL;
- user request and scope;
- raw evidence: checks, logs, screenshots, command output, artifacts, or none;
- constraints: no edits, command limits, network limits, time limits, and repo
  guidance.

Do not give expected verdicts, confidence, defenses, "already handled" claims,
hints, favorable summaries, or owner intent unless the target cannot be
understood without it. Label unavoidable framing as unverified.

Use this shape:

```text
You are coordinating specialist review. Do not review directly.

Review target:
[target locator]

User request:
[exact request]

Scope:
[review scope]

Evidence:
[raw evidence or "none provided"]

Constraints:
[constraints]
```

If `reviewer` cannot run, say coordinated review could not run. Do not claim
specialist review. Use ordinary review only when you label it as a fallback.
