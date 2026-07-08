# Maintainer Workflows Audit

This audit covers the repo-local workflow set listed in
`local-docs/compass-surface-inventory.md`.

Scope:

- `workflows/addition-intake.md`
- `workflows/agent-failures.md`
- `workflows/claude-config.md`
- `workflows/codex-restart-recovery.md`
- `workflows/compass-review-program.md`
- `workflows/multi-thread-pr-coordination.md`
- `workflows/plan-template.md`
- `workflows/portable-config.md`
- `workflows/read-only-research.md`
- `workflows/which-llm-plugin.md`

Purpose: ensure maintainer workflows route Compass work without becoming
runtime behavior, stale history storage, or process-shaped bloat.

## Current Shape

All audited files are repo-local. None are installed into live Codex, user
skill homes, or Claude homes.

Line counts:

- `addition-intake.md`: 139
- `agent-failures.md`: 136
- `claude-config.md`: 73
- `codex-restart-recovery.md`: 79
- `compass-review-program.md`: 180
- `multi-thread-pr-coordination.md`: 102
- `plan-template.md`: 64
- `portable-config.md`: 173
- `read-only-research.md`: 50
- `which-llm-plugin.md`: 72

## Findings

### Keep Exact Operating Workflows

These workflows are doing real maintainer work and should stay:

- `addition-intake.md`
- `claude-config.md`
- `codex-restart-recovery.md`
- `multi-thread-pr-coordination.md`
- `portable-config.md`
- `read-only-research.md`
- `which-llm-plugin.md`

They answer concrete operational questions: how additions enter Compass, how
the Claude mirror is maintained, how restart recovery is installed, how
parallel PR work stays sane, how live config is installed, how research runs
without mutation, and how the separately owned `which-llm` plugin is refreshed.

They mostly route action rather than explain taste. No broad rewrite is needed.

### Keep `compass-review-program.md`

`compass-review-program.md` is the root workflow for this goal. It is long, but
the length earns its place: it defines the review stance, inventory pass,
runtime audit questions, maintainer audit questions, skill-set audit, pruning
standard, PR rhythm, and stop conditions.

No pruning is needed now. It should stay as maintainer context.

### Keep `agent-failures.md`, But Cap Its Job

`agent-failures.md` is allowed to carry history because that is its job. The
current entries preserve repeated failure patterns that produced durable
guidance.

The risk is growth without pressure. If the file becomes a log of every
mistake, it will stop being a decision tool. It should stay focused on the
first upstream failure, the root cause category, and the durable change that
followed.

No immediate edit is needed, but future entries should remain rare and should
name the route they produced.

### Audit `plan-template.md` Next

`plan-template.md` is the weakest fit in the workflow set.

The repository now has stronger planning surfaces:

- normal Plan mode and `update_plan` for interactive work;
- `using-codex-goals` for durable goal contracts;
- `workflows/compass-review-program.md` for the Compass audit loop;
- focused workflows for exact operations.

That does not prove `plan-template.md` should be removed. It may still be useful
as a written artifact shape for shared or risky work. But it now needs to earn
its place. A template that exists because planning is generally useful is weak.
A template that exists because Compass sometimes needs a durable plan artifact
is stronger.

Completed follow-up: `plan-template.md` was revised rather than retired.

The review question should be:

```text
Does Compass need a repo-local written plan artifact shape that is distinct
from interactive Plan mode and durable Codex goals?
```

If yes, narrow the file to that job. If no, remove it and update workflow links.

- Completed by the plan-template PR. The file stayed, but it is narrowed to a
  repo-local written plan artifact shape, not a competing planning or goal
  workflow.

## Decisions

- Keep the workflow directory as repo-maintainer context.
- Do not move any workflow into installed runtime guidance.
- Do not rewrite exact operating workflows now.
- Keep `agent-failures.md` as a failure-to-guidance journal, not a general log.
- Keep `plan-template.md` as a narrow written artifact shape.

## Completed PR Boundary

Completed focused PR for `plan-template.md`:

- read its current callers and links;
- decided to revise instead of retire it;
- updated `portable-config.md`, `local-docs/README.md`, and the surface
  inventory if links change;
- ran `.\scripts\doctor.ps1`.
