---
name: specialist-review
description: Coordinate explicit specialist reviews with direct specialist subagents, including full runs across all specialists.
---

# Specialist Review

Use this skill only when the user invokes `$specialist-review`, explicitly asks
for coordinated specialist review, or asks for a clean specialist handoff.

Use `pr-review-loop` for ordinary PR review. This skill is an additive
specialist layer for explicit coordinated specialist review requests.

Act as the reviewer coordinator for this request. Choose the review mode, then
spawn the matching specialists as direct subagents.

Review modes:

- Standard: route the request to the smallest justified subset of the roster.
- Full: run the full roster: `algorithm-critic`, `reuse-critic`,
  `research-critic`, `verifier`, and `neutral-critic`.

A completed coordinated specialist review requires direct specialist subagent
results. CLI runs, new threads, and shell-launched sessions are manual fallback
material. Manual fallback path: return clean specialist prompts for manual use
and label the result as manual fallback.

Standard routing:

- Requirements, scope, process, or delete-first risk: `algorithm-critic`.
- Needless invention, duplication, or missed reuse risk: `reuse-critic`.
- External current knowledge, docs, packages, standards, or prior art risk:
  `research-critic`.
- Executable, visual, artifact, integration, or claim-proof risk: `verifier`.
- Requested fresh-eyes gate or explicit repo review gate: `neutral-critic`.

Give each specialist only:

- target: repo, PR, branch, commit range, patch, files, artifact paths, or URL;
- user request and scope;
- raw evidence: checks, logs, screenshots, command output, artifacts, or none;
- user-stated hard limits, if any.

Pass raw target, request, evidence, and explicit user limits. The coordinator
owns operational limits for specialist prompts.

Keep prompts neutral. Include only facts needed to understand the target, and
label unavoidable framing as unverified.

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

Use the manual fallback path when direct specialist spawning is unavailable.

After specialists return, report findings first, ordered by severity. Name the
source specialist and evidence. Preserve conflicts. Name coverage, missing
evidence, and residual risk. Put recommendations after findings; they must be
specialist-backed or directly evidence-derived. Use only supported findings,
recommendations, and consensus.
