# Maintainer Workflows Audit

This audit packet covers the repo-local workflow set listed in
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

Packet status:

- Refreshed after the reviewer-authority gate follow-up landed.
- Use current workflow files, local-doc links, inventory state, and open PR
  stack state before deriving new work from this packet.
- Treat verification commands as audit history, not current proof.

## Current Shape

All audited files are repo-local. None are installed into live Codex, user
skill homes, or Claude homes.

Line counts:

- `addition-intake.md`: 142
- `agent-failures.md`: 138
- `claude-config.md`: 73
- `codex-restart-recovery.md`: 79
- `compass-review-program.md`: 224
- `multi-thread-pr-coordination.md`: 102
- `plan-template.md`: 56
- `portable-config.md`: 174
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
standard, PR rhythm, review gate, and stop conditions.

No pruning is needed now. It should stay as maintainer context.

The review gate is repo-maintainer workflow guidance, not installed runtime
behavior. It makes green draft PRs build evidence rather than readiness, then
routes final readiness through live PR state, stacked-base checks, current-head
review gates, reviewer-authority checks, and `pr-review-loop`.

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

### Keep `plan-template.md` Narrow

`plan-template.md` had to justify itself because Compass already has stronger
planning surfaces:

- Plan mode and `update_plan` for interactive work;
- `using-codex-goals` for durable goal contracts;
- `workflows/compass-review-program.md` for the Compass audit loop;
- focused workflows for exact operations.

The file now earns its place only as a written artifact shape:

- it is repo-maintainer guidance, not runtime behavior;
- it tells agents not to use it for normal in-chat planning;
- it points interactive work to Plan mode or `update_plan`;
- it points durable Codex goals to `using-codex-goals`;
- it says to use this template only when a plan itself is an artifact.

Decision:

- Keep `plan-template.md` as a narrow written plan artifact shape.
- Do not let it compete with interactive planning or durable goal contracts.

- Completed by the plan-template PR. The file stayed, but it is narrowed to a
  repo-local written plan artifact shape, not a competing planning or goal
  workflow.

## Decisions

- Keep the workflow directory as repo-maintainer context.
- Do not move any workflow into installed runtime guidance.
- Do not rewrite exact operating workflows now.
- Keep the Compass review-program gate in repo-local workflow guidance,
  including the rule that missing reviewer authority leaves the gate
  unsatisfied.
- Keep `agent-failures.md` as a failure-to-guidance journal, not a general log.
- Keep `plan-template.md` as a narrow written artifact shape.

## Completed PR Boundary

Completed focused PRs:

- `plan-template.md` was narrowed to a written plan artifact shape after
  reading its current callers and links.
- `compass-review-program.md` gained a review gate that keeps green draft PRs
  separate from readiness and routes final readiness through `pr-review-loop`.
- `compass-review-program.md` gained a reviewer-authority gate so a required
  reviewer that cannot be invoked is named as unsatisfied instead of replaced by
  self-review or local checks.
- `.\scripts\doctor.ps1` passed for the focused changes.

## Verification

Commands used while refreshing this audit:

```powershell
Get-Content -Raw workflows\plan-template.md
rg -n "plan-template|written plan|Plan mode|using-codex-goals|durable goal|repo-local" workflows local-docs README.md AGENTS.md
(Get-Content workflows\addition-intake.md).Count
(Get-Content workflows\agent-failures.md).Count
(Get-Content workflows\claude-config.md).Count
(Get-Content workflows\codex-restart-recovery.md).Count
(Get-Content workflows\compass-review-program.md).Count
(Get-Content workflows\multi-thread-pr-coordination.md).Count
(Get-Content workflows\plan-template.md).Count
(Get-Content workflows\portable-config.md).Count
(Get-Content workflows\read-only-research.md).Count
(Get-Content workflows\which-llm-plugin.md).Count
```
