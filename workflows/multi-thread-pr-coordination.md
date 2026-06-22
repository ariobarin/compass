# Multi-Thread PR Coordination

Use this workflow when launching multiple Codex threads, worktrees, or agents
against one repository objective. The goal is parallel discovery without public
PR sprawl.

This is repo-maintainer guidance. It is not installed into a live Codex home or
user skill home.
Use it from this checkout when coordinating local branches, scratch notes, and
reviewable upstream PRs.

## Coordinator Stance

The coordinator is not a passive tracker. It protects the public review surface
while workers do the ground work. Local notes can be messy and provisional.
Public PRs should be focused, verified, and useful to future reviewers.

## Default Shape

- One coordinator thread owns public branch and PR hygiene.
- Worker threads use their own branches and worktrees outside this checkout.
- Tracking notes stay local by default, under `.local/` or another ignored
  private note.
- Repo-local `.local/` is for ignored notes and scratch evidence, not nested
  worktrees.
- Public PRs are only for independently reviewable upstream changes.

## Before Launching Workers

1. Write a short coordinator goal: what success means, what is in scope, and
   what is out of scope.
2. Decide where local tracking lives. Prefer `.local/<topic>/` when the notes
   are not useful upstream. Put worker worktrees outside this checkout.
3. Set a PR budget, usually no more than three active PRs from the workstream.
4. Tell workers whether they may open PRs, or whether coordinator approval is
   required first. Default to coordinator approval when the workstream could
   produce tracker notes, broad audits, or overlapping fixes.
5. Tell workers how to report findings:
   - finding;
   - files affected;
   - risk;
   - verification available;
   - recommended target branch.

## Worker Rules

Workers should not open a PR for tracker notes, partial findings, broad audits,
or speculative fixes. They should update local evidence and report back to the
coordinator.

Workers may open a PR only when all are true:

- the change is focused;
- the target branch is clear;
- the diff is not mixed with tracker notes;
- verification is listed or the verification gap is explicit;
- the coordinator has approved opening that PR.

## PR Types

Keep each PR in exactly one class:

- behavior fix;
- guard or check improvement;
- docs intended for upstream readers;
- eval or fixture update;
- preservation branch for a specific known risk.

Do not mix audit tracking, tool code, eval changes, and local evidence in one
PR. If a finding needs both a fix and documentation, prefer one fix PR and one
small upstream-doc PR only when the docs are useful to future readers.

## Consolidation Loop

During active parallel work, the coordinator should periodically inspect PRs
created by the current workstream:

Mutate current-workstream PRs only when the user granted that authority for the
workstream. Otherwise, report the recommended cleanup and ask before closing,
rebasing, retargeting, or refreshing.

1. List current-workstream PRs and classify them.
2. Close duplicate, scratch, or mixed workstream PRs with a short comment.
3. Rebase or refresh viable workstream PRs on current main.
4. Keep the PR budget visible to the workers.
5. Preserve local evidence without pushing it upstream.

Treat unrelated PRs as context only. Do not close, rebase, retarget, or refresh
an unrelated PR without explicit owner approval.

## When To Keep Tracking Local

Keep tracking local when it contains:

- scratch findings;
- temporary matrices;
- local ports, paths, containers, screenshots, or logs;
- seeded benchmark values used only for setup;
- notes useful only to the current operator.

Promote tracking upstream only when it becomes durable documentation for future
contributors.
