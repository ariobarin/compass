# Plan Template

Use this template only when Compass needs a written plan artifact that will be
reviewed, handed off, or kept with repo-local evidence.

This is repo-maintainer guidance and is not installed into a live Codex home or
user skill home.
Put reusable agent behavior in `codex/agents/` or `codex/skills/` instead.

Do not use this for normal in-chat planning. Prefer Plan mode or `update_plan`
when the work is interactive. Use `using-codex-goals` when the user asks for a
durable Codex goal. Use this file only when a plan itself is an artifact.

Keep the plan short enough to guide execution. If a section does not change a
future decision, cut it.

## Goal

State the end state in one or two paragraphs. Include what must be true for the
work to count as done.

## Scope

- In scope:
- Out of scope:
- Repos or paths:
- Existing branches or PRs:

## Context To Gather

- Files, docs, issues, logs, or commands that must be inspected first:
- External docs or APIs that may need verification:
- Assumptions to challenge or verify:

## Execution Steps

Use numbered steps only when order matters. Each step should name an action and
the evidence it should produce.

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

List only questions that block useful progress. Make reasonable assumptions for
everything else and state them before editing.
