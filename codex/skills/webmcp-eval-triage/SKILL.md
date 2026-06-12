---
name: webmcp-eval-triage
description: Triage failing WebArena or WebMCP benchmark tasks into tool faults, stale eval expectations, agent executor mistakes, infrastructure failures, or long-run drift using logs, eval definitions, runtime evidence, and result artifacts.
---

# webmcp-eval-triage

Use this skill before changing tools, evals, prompts, or benchmark operations in
response to failures. The first job is to classify the real owner of the
failure.

## Required References

Read the local references that match the failure:

- [failure-rubric.md](references/failure-rubric.md): fault buckets, compact
  critique codes, stale-eval decisions, and WebMCP tool-shape failure modes.
- [log-and-artifact-triage.md](references/log-and-artifact-triage.md): logs,
  result directories, exact error grouping, long-run drift, and valid-row rules.

## Triage Loop

1. Read the failing task definition, eval definition, run output, tool logs, and
   result artifacts.
2. Bucket the failure: tool, stale eval, agent executor, infrastructure, or
   long-run drift.
3. Check whether the pattern is one task, one site, one tool family, one arm, or
   a broad stack failure.
4. Use direct runtime evidence when available. A reward score alone is weaker
   evidence than tool execution and persisted state.
5. Recommend the owner and next action. Stop or pause the run if it is producing
   invalid evidence.

## Output

For each task or cluster, report the bucket, evidence, likely owner, suggested
fix, and whether human sign-off is needed before changing eval expectations.
