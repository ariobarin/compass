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

If `reviewer` cannot run, say coordinated review could not run. Do not claim
specialist review. If you continue, label the result as a non-coordinated
fallback.

If `reviewer` can run but reports that it cannot launch specialist subagents,
continue the coordinated path from the parent context instead of stopping:

1. Ask `reviewer` for a delegation packet with selected specialist names and
   exact prompts only.
2. Launch each selected specialist from the parent context with the exact prompt.
3. Send only raw specialist outputs back to `reviewer` for consolidation.
4. Report the consolidated reviewer output as the specialist review result.

Do not choose or edit the specialist set yourself during this fallback. If the
delegation packet is missing or unusable, say coordinated review could not run.

Do not wait indefinitely for the coordinator's first result. If the first
bounded wait returns no coordinator output, send one follow-up asking `reviewer`
to either return current specialist-backed results, report that specialist
subagents are still running, or return the parent-delegation packet now.

If `reviewer` says specialist subagents are still running, keep using bounded
waits for the live coordinator until it returns specialist-backed results,
reports that it cannot launch or continue specialists, or stops returning status.
Use the parent-delegation path only when `reviewer` explicitly reports that it
cannot launch or continue specialist subagents. If follow-up waits stop
returning usable status, report that coordinated review stalled at the reviewer
coordinator and include the thread or agent id.
