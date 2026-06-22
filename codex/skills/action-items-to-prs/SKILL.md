---
name: action-items-to-prs
description: Turn action items from reports, audits, checklists, issues, reviews, or notes into scoped PRs with verification, critic review, and merge gates.
---

# action-items-to-prs

Use this skill to turn a set of actionable items into reviewed PR work. Keep the
source artifact as the anchor for scope, grouping, verification, and final
status.

When the user frames the work as a Codex `/goal`, pair this with
`using-codex-goals` so each PR group has a completion predicate and evidence
ledger before publishing.

When the work centers on iterating an existing PR or review thread rather than
creating fresh PR groups, pair this with `pr-review-loop` so PR identity,
review gates, and merge authority stay explicit.

## Start with the source

Read local guidance before editing:

1. nearest `AGENTS.md` or repo-owned guidance;
2. repository README or workflow notes;
3. the report, audit, checklist, issue list, PR comments, or user notes that
   contain the action items;
4. existing open PRs that may already cover the same work.

Extract an item ledger before changing files. For each item, record:

- source location or quote;
- requested behavior or decision;
- likely files, systems, or owners;
- verification needed;
- status: todo, already handled, skipped by decision, needs repair, needs owner
  decision, or done.

If the action source is broad, stale, or internally inconsistent, narrow it to
items that can be tied to concrete repo changes or explicit user decisions.

## Group work into PRs

Choose PR boundaries around reviewer context and verification scope, not around
the number of bullets in the source artifact.

- Add to an existing compatible PR when it already covers the same area and
  branch policy allows it.
- Create a new PR when the item group has a distinct purpose, owner, or risk.
- Keep unrelated action groups separate even when they came from the same
  source artifact.
- Do not create a PR for items that are already handled, non-actionable, or
  better answered with a comment.

When the user asks for draft PRs, leave new PRs as drafts unless local guidance
or the user says otherwise.

## Implement one group at a time

For each PR group:

1. confirm the branch, base branch, and working tree state;
2. inspect nearby code and docs before editing;
3. keep changes scoped to the ledger items in that group;
4. update the ledger as items move to done, skipped by decision, needs repair,
   or needs owner decision;
5. commit with the repo's commit conventions;
6. push and open or update the PR.

Never stage unrelated user changes silently. If the worktree contains unrelated
edits, stage explicit paths only.

## Verify efficiently

Run the smallest checks that cover the changed behavior, then broaden only when
the risk or repo guidance calls for it.

Useful verification can include:

- targeted unit, lint, or doctor checks;
- direct API calls that reproduce a frontend action;
- browser verification for user-facing behavior;
- docs rendering or validation for documentation changes;
- `git diff --check` for whitespace and conflict residue.

Record the verification command, result, and date when the evidence is
time-sensitive.

## Use critic review when requested

Use the `neutral-critic` agent when the user request, repo guidance, or action
source asks for an independent review gate.

Give the critic concrete evidence:

- the source action items for the PR group;
- the branch or PR link;
- the relevant diff or file list;
- verification output;
- known tradeoffs or skipped items.

Do not give the critic the desired conclusion. Iterate on actionable critic
feedback up to the requested limit, defaulting to two passes when no limit is
provided. If feedback remains negative after the limit, stop and reassess the
scope, implementation, or source interpretation before merging.

## Merge only when authorized

Merge only when all of these are true:

- the user or repo workflow authorized merging;
- required checks pass or failures are proven unrelated;
- requested critic review is satisfied;
- no blocking review state remains;
- the PR still matches the ledger items it claims to handle.

If merge is not authorized or not ready, leave the PR open and report the next
action needed.

## Output

Report:

- source artifact or action list used;
- PRs created, updated, merged, or intentionally reused;
- items handled, skipped, already handled, needing repair, or needing an owner
  decision;
- verification commands and results;
- critic review status when used;
- remaining risks or follow-up decisions.
