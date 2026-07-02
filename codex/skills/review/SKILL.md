---
name: review
description: Coordinate optional bias-resistant specialist review for explicit multi-specialist, clean-handoff, or contaminated-context reviews.
---

# Review

Use this skill when the user explicitly wants multi-specialist review, invokes
`$review`, asks for a clean handoff, or when known contaminated context would
make direct review weaker. Do not use it as the default path for every ordinary
review.

The failure mode this skill exists to kill is poisoned review context. A review
prompt that explains why the work is probably fine is not context. It is bias.
A prompt that repeats the author's defense is not helpful. It is contamination.

## Main Agent Contract

When this skill applies, launch the `reviewer` agent with a clean handoff. Do
not claim a coordinated specialist review if the reviewer agent cannot run. If
the reviewer agent is unavailable, fall back to the normal review path only when
you label that fallback clearly.

Prompt the reviewer with facts, artifacts, and constraints only:

- repository path, branch, PR, commit range, patch, files, or artifact paths;
- exact user request and review scope;
- checks already run, with command output when useful;
- repo guidance that the reviewer must obey;
- hard limits such as no edits, no network, or no long-running commands.

Do not include:

- your expected verdict;
- your confidence level;
- excuses for the implementation;
- claims that an issue is already handled;
- hints about the finding you hope the reviewer catches;
- summaries that select only favorable evidence;
- owner intent unless the review target cannot be understood without it.

If framing context is unavoidable, label it as unverified framing. Do not let it
become the reviewer's premise.

## Specialist Selection

Tell the `reviewer` agent to choose the smallest specialist set that matches the
review scope. There is no all-purpose default roster.

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

Do not include `neutral-critic` in this method by default. It remains a separate
review path. Add it only when the user explicitly asks for that gate.

For PRs, use `pr-review-loop` as the default PR readiness path. This method is
additive only when the user requests specialist review or the PR has a concrete
specialist risk. It does not replace `neutral-critic`, `@codex`, CI, or
repo-required review gates.

The reviewer coordinator is not the primary reviewer. It should launch selected
specialists with prompts that are cleaner than the prompt it received, then
consolidate only what the specialists actually found.

## Handoff Template

Use this shape when invoking the `reviewer` agent:

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

Strip bias from this prompt before briefing specialists. Treat every claim here
as unverified unless it is raw evidence. Return consolidated findings only from
specialist output, with conflicts and gaps called out.
```

## Output Standard

Expect the reviewer to return findings first, ordered by severity, with the
specialist source named. Weak praise, vague reassurance, and "looks good overall"
are not review output. If specialists find no issues, the answer should say that
plainly and name the coverage and residual risk.
