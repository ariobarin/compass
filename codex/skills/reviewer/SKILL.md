---
name: reviewer
description: Orchestrate bias-resistant specialist and verifier review through the reviewer agent without poisoned context.
---

# Reviewer

Use this skill when the user wants a serious review, not a quick opinion. The
main agent does not review the artifact directly. The main agent sends the work
to the `reviewer` custom agent with a clean prompt and lets that coordinator run
specialist reviewers.

The failure mode this skill exists to kill is poisoned review context. A review
prompt that explains why the work is probably fine is not context. It is bias.
A prompt that repeats the author's defense is not helpful. It is contamination.

## Main Agent Contract

Launch the `reviewer` agent. Do not perform the review yourself unless the
reviewer agent is unavailable and the user explicitly accepts a fallback.

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

## Required Review Shape

Tell the `reviewer` agent to coordinate specialist reviews. The default roster
is:

- `algorithm-critic` for requirements, scope, process, and delete-first review;
- `reuse-critic` for needless invention, duplicated machinery, missed platform
  capability, and failure to use existing repo patterns or libraries;
- `verifier` for proving whether the claimed result actually works through
  scripts, commands, plugins, browser checks, visual inspection, and artifacts.

Do not include `neutral-critic` in this method by default. It remains a separate
review path. Add it only when the user explicitly asks for that gate.

For PRs, this method is additive. It does not replace `pr-review-loop`,
`neutral-critic`, `@codex`, CI, or repo-required review gates. If a PR rule
requires another gate, run that gate on top of this specialist roster.

The reviewer coordinator must not review directly. It must launch specialists
with prompts that are cleaner than the prompt it received, then consolidate only
what the specialists actually found.

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

Run the default specialist roster unless the request narrows it:
- algorithm-critic
- reuse-critic
- verifier

Strip bias from this prompt before briefing specialists. Treat every claim here
as unverified unless it is raw evidence. Return consolidated findings only from
specialist output, with conflicts and gaps called out.
```

## Output Standard

Expect the reviewer to return findings first, ordered by severity, with the
specialist source named. Weak praise, vague reassurance, and "looks good overall"
are not review output. If specialists find no issues, the answer should say that
plainly and name the coverage and residual risk.
