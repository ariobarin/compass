# Goal Contracts

Load this reference when a task needs copyable `/goal` prompts, subagent
handoffs, or examples of good completion predicates.

## Goal Brief Template

```text
/goal <objective>

Done means:
Scope:
Do not touch:
Evidence required:
If waiting:
If blocked:
Subagents:
```

Use this form to turn broad intent into a durable contract. Keep every field
concrete enough that another agent could verify it later without guessing.

## Subagent Slice Template

```text
Parent goal:
Slice:
Allowed files or systems:
Forbidden scope:
Inputs to inspect:
Expected output:
Evidence required:
Done condition for this slice:
Return one status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED.
```

The controller should keep ownership of the parent goal. A subagent completes
only its slice and returns evidence for integration.

## Completion Predicate Examples

Good predicates name the finish line and the proof:

- All named PRs are open, green, reviewed, and linked in the final report.
- Each listed repo has a current diff audit, a matching `MODIFICATIONS.md`, and
  verification that unrelated changes were not touched.
- The report exists at the requested path, covers each named comparison axis,
  and has been checked for formatting or repo-specific style constraints.

Avoid predicates like "make progress", "clean it up", or "look into it" unless
the user explicitly wants exploration only.

## Waiting Rule Examples

Use waiting rules for external systems:

- If waiting on PR review, keep the goal active and poll for new review comments
  or approval signals.
- If waiting on CI, keep the goal active until checks pass, fail with actionable
  logs, or time out under the user's stated policy.
- If waiting on a benchmark, preserve artifacts and report the next expected
  checkpoint instead of marking complete early.
