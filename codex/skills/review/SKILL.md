---
name: review
description: Coordinate optional bias-resistant specialist review for explicit multi-specialist, clean-handoff, or contaminated-context reviews.
---

# Review

Use this skill only when the user explicitly asks for multi-specialist review,
invokes `$review`, asks for a clean handoff, or known contaminated context would
make direct review weaker. Do not make it the default path for ordinary review.

This skill kills poisoned review context: author narrative, confidence,
expected verdicts, excuses, and selective summaries.

## Main Agent Contract

Launch `reviewer` with facts, artifacts, and constraints only. If the reviewer
agent cannot run, do not claim coordinated specialist review. Use the normal
review path only when you label it as a fallback.

Include target locators, exact request and scope, raw evidence or checks run,
repo guidance, and hard limits. Exclude expected verdicts, confidence, defense,
"already handled" claims, hints, favorable summaries, and owner intent unless
the target is unintelligible without it.

If framing context is unavoidable, label it as unverified framing. Do not let it
become the reviewer's premise.

## Specialist Selection

Tell `reviewer` to choose the smallest specialist set that matches real risk.
There is no all-purpose roster.

- `algorithm-critic` for requirements, scope, process, and delete-first review;
- `reuse-critic` for needless invention, duplicated machinery, missed platform
  capability, and failure to use existing repo patterns or libraries;
- `research-critic` for online prior art, official docs, package ecosystems,
  standards, papers, issues, examples, and known existing solutions;
- `verifier` for proving whether the claimed result actually works through
  scripts, commands, plugins, browser checks, visual inspection, and artifacts.

Select `research-critic` only when public prior art, current docs, packages,
standards, or external examples materially affect the decision. Select
`verifier` only when there is an executable, visual, artifact, integration, or
claim-verification surface to check.

Do not include `neutral-critic` by default. It remains a separate path. Add it
only when the user explicitly asks for that gate.

For PRs, use `pr-review-loop` as the default PR readiness path. This method is
additive only when the user requests specialist review or the PR has a concrete
specialist risk. It does not replace `neutral-critic`, `@codex`, CI, or
repo-required review gates.

The reviewer coordinator is not the primary reviewer. It launches specialists
with cleaner prompts than it received and consolidates only what they found.

## Handoff Template

Use this shape:

```text
You are coordinating a specialist review. Do not review directly.

Review target:
[repo, PR, branch, commit range, patch, files, or artifact paths]

User request:
[exact review request]

Scope:
[what to review and what is out of scope]

Evidence:
[commands run, outputs, logs, screenshots, or "none provided"]

Constraints:
[no edits, command limits, time limits, repo guidance]

Select only the specialist reviewers this scope requires. For each selected
specialist, name why that specialty is needed.

Strip bias before briefing specialists. Treat every claim here as unverified
unless it is raw evidence. Return only specialist-backed findings, conflicts,
and gaps.
```

## Output Standard

Expect findings first, ordered by severity, with specialist source and evidence.
Weak praise, vague reassurance, and "looks good overall" are not review output.
If no issues survive, say so plainly and name coverage and residual risk.
