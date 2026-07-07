---
name: specialist-review
description: Route explicit coordinated specialist review requests to the reviewer coordinator with a neutral handoff.
---

# Specialist Review

Use this skill only when the user invokes `$specialist-review`, explicitly asks
for coordinated specialist review, or asks for a clean specialist handoff.

Do not use this skill for ordinary PR review. PR review loops belong to
`pr-review-loop`; this skill is an additive specialist layer only when the user
asks for one.

Your job is not to review or choose specialists. Launch `reviewer` with a clean
handoff.

Give `reviewer` only:

- target: repo, PR, branch, commit range, patch, files, artifact paths, or URL;
- user request and scope;
- raw evidence: checks, logs, screenshots, command output, artifacts, or none;
- user-stated hard limits, if any.

Do not synthesize command, network, time, or repo constraints. The coordinator
owns operational limits for specialist prompts.

Do not give expected verdicts, confidence, defenses, "already handled" claims,
hints, favorable summaries, or owner intent unless the target cannot be
understood without it. Label unavoidable framing as unverified.

Use this shape:

```text
Review target:
[target locator]

User request:
[exact request]

Scope:
[review scope]

Evidence:
[raw evidence or "none provided"]

User-stated hard limits:
[verbatim limits or "none provided"]
```

`reviewer` is a required part of this installed Compass bundle. If it cannot
run, the configured environment is broken. Name the missing capability or tool
state, and state that coordinated specialist review failed. Do not claim
specialist review completed.
