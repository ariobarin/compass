# Plan Template

Use this template for large, ambiguous, risky, or multi-step work. Keep the plan
short enough to guide execution, not so detailed that it becomes a second
implementation.

Use it when the user explicitly asks for a goal, target state, success
criteria, or plan, or when the work clearly needs structured planning.

Draft the goal collaboratively in normal prose. Do not switch into a formal
goal-management workflow unless the user explicitly asks for that workflow.

## Goal

State the concrete end state in one or two paragraphs. Include what must be true
for the work to count as done.

## Scope

- In scope:
- Out of scope:
- Repos or paths:
- Existing branches or PRs:

## Context To Gather

- Files, docs, issues, logs, or commands that must be inspected first:
- External docs or APIs that may need verification:
- User assumptions to challenge or clarify:

## Execution Steps

1. Read and map the relevant code or workflow.
2. Decide the smallest durable change that satisfies the goal.
3. Edit only the files in scope.
4. Run focused checks.
5. Broaden checks if shared behavior or user-visible workflows changed.
6. Commit, push, and open or update a PR when requested.

## Verification

- Required commands:
- Runtime or browser checks:
- GitHub checks or review path (CI, requested reviewers, `@codex review`):
- Artifacts to inspect:
- Evidence that proves completion:

## Rollback

- Files or config that would need to be reverted:
- Data, containers, branches, or services that need cleanup:

## Open Questions

List only questions that block a safe implementation. Make reasonable
assumptions for everything else and state them before editing.
