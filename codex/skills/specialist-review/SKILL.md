---
name: specialist-review
description: Coordinate explicit specialist review requests in the current context with direct specialist subagents and neutral evidence.
---

# Specialist Review

Use this skill only when the user invokes `$specialist-review`, explicitly asks
for coordinated specialist review, or asks for a clean specialist handoff.

Do not use this skill for ordinary PR review. PR review loops belong to
`pr-review-loop`; this skill is an additive specialist layer only when the user
asks for one.

Your job is not to perform the review yourself. Run the reviewer-coordinator
flow in the current context, choose the smallest justified specialist set, then
spawn only those specialists as direct subagents.

Do not launch `reviewer` as an intermediate subagent unless the active Codex
configuration explicitly allows nested subagents. The default subagent depth
allows direct children only, so a child coordinator cannot normally spawn
specialist children.

Use the active Codex subagent route for custom agents. Do not use `codex exec`,
a new thread, or a shell-launched session as a substitute. If subagents cannot
be spawned, say coordinated review could not run. If you continue, label the
result as a non-coordinated fallback and return clean specialist prompts for
manual use.

Select only specialists whose risk is real:

- `algorithm-critic`: requirements, scope, process, and delete-first review.
- `reuse-critic`: needless invention, duplicated machinery, missed repo
  patterns, platform or library reuse.
- `research-critic`: external prior art, current docs, packages, standards,
  papers, issues, known solutions.
- `verifier`: executable, visual, artifact, integration, or claim-proof
  verification.
- `neutral-critic`: fresh-eyes review, only when the user asks for that gate or
  repo guidance requires it.

Use `research-critic` only when external current knowledge materially affects
the decision. Use `verifier` only when there is a real thing to run, inspect,
render, query, or prove. Never run specialists for theater.

Give each specialist only:

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

If a specialist cannot run through the active Codex subagent route, say
coordinated review could not run. Do not claim specialist review.

After specialists return, report findings first, ordered by severity. Name the
source specialist and evidence. Preserve conflicts. Name coverage, missing
evidence, and residual risk. Put recommendations after findings; they must be
specialist-backed or directly evidence-derived. Do not invent findings,
recommendations, or consensus.
