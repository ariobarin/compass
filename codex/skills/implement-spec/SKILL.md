---
name: implement-spec
description: Implement an agreed spec and its dependent tickets as integrated, reviewable work. Use when asked to execute an existing spec or ticket graph, especially when independent slices can run in parallel.
---

# Implement Spec

The goal is the requested spec working on one integration branch. Tickets form
a task graph with a frontier of work whose prerequisites are ready.

## Establish The Integration State

Read the spec, tickets, blocking relationships, and relevant repository
guidance. Use the existing tracker and integration branch when provided. Name
one owner for integration and acceptance; that owner remains responsible when
implementation or review is delegated.

A prerequisite is ready when its required behavior is present in the
integration state a worker will use. Inspect the landed changes and their
evidence. A closed ticket or a worker's completion message cannot establish
readiness. Honor any explicit shared integration-and-verification boundary in
the plan instead of promising that each intermediate slice works alone.

Communicate primarily through context pointers: the spec, tickets, research,
decisions, and previous changes. Reuse these artifacts across workers and
handoffs instead of copying their contents into every prompt.

## Work The Frontier

Parallelize independent tickets when the saved time justifies coordination.
Bound concurrency by available capacity and genuinely independent ownership.
Give each worker its ticket, acceptance criteria, context pointers, integration
base, and the files or interfaces it owns. Keep overlapping edits with one
owner. In a shared checkout, the integration owner owns staging and commits.
Isolate worktrees or runtime state where workers would otherwise contend over
mutable state; do not create isolation machinery by default.

Each worker starts from an integration state containing its prerequisites,
implements the slice, and chooses proof proportional to regression risk, using
`$test-for-risk` when available.
Its result identifies the actual changes, the evidence produced, and any
remaining gap. Supervise delegated work through native waits; use `$monitor`
when available for sustained attention and recovery.

Integrate completed work through the designated owner. Inspect the returned
diff and the decisive evidence behind completion claims. Check interactions
with work integrated since the worker started, then advance the frontier.
Update ticket state to reflect accepted work using the configured lifecycle.
Do not close tickets merely to unblock scheduling.

Continue independent work while a ticket is blocked. Resolve routine execution
choices within the agreed scope; return only the affected decision or missing
dependency when it needs the user or another owner.

## Review The Result

Review the integrated work against both the spec and repository standards.
Use independent review when the scope or risk warrants it. Inspect behavior
beyond the diff when a change crosses boundaries, using `$blast-radius` when
available. Give reviewers the exact
base and actual changes under review, including relevant staged, unstaged,
and untracked work. A commit-only diff cannot review uncommitted changes.

Inspect evidence cited by reviewers before treating a finding as established.
Fix concrete failures and scope gaps, then refresh the proof those fixes could
invalidate. Stop when the requested behavior and required proof hold; further
review needs a concrete remaining risk, not another round of speculative
cleanup.

Follow the requested delivery workflow for a draft PR, review readiness, and
ticket closure. Leave a runnable result and concise evidence the user can
inspect. Keep a preview alive when their next decision depends on trying it.
Report the outcome, material limits, and pointers to the work without
duplicating the spec or worker reports.

Source provenance lives in [references/sources.md](references/sources.md). Do
not load it during normal implementation.
