# Maintenance Learnings

These notes guide changes to `codex-portable`. They are repo-local learning
material, not live Codex config.

## What Good Looks Like

Good changes make the portable setup easier to review, reinstall, and verify
without making every future Codex turn carry more context. Prefer small durable
artifacts: a workflow for a recurring process, a skill for a specialized task, a
script for a mechanical check, and a manifest for capability or portability
boundaries.

The best default is boring and explicit. Keep ordinary files in ordinary Codex
locations, keep generated state out of git, and make promotion from repo to live
config a deliberate copy step with a diff.

## Context Discipline

- Keep `codex/AGENTS.md` short. It should hold personal defaults that genuinely
  apply everywhere.
- Treat `codex/AGENTS.md` as the portable copy of the live global
  `~/.codex/AGENTS.md`, not as repo-local maintenance notes.
- If a rule only makes sense while editing `codex-portable`, it belongs in the
  repo-root `AGENTS.md`, `workflows/`, or `local-docs/`, not in
  `codex/AGENTS.md`.
- Put detailed guidance in `workflows/`, skill references, scripts, manifests,
  or local docs.
- Add durable guidance only after repeated mistakes or clear workflow friction.
- Prefer evidence over preference. A new rule should name the failure it
  prevents or the review path it improves.
- Avoid framework-shaped prompt systems unless a real recurring task needs that
  structure.

## Change Routing

- A repeated human process belongs in `workflows/`.
- A task-specific agent capability belongs in `codex/skills/`.
- A mechanical or reproducible check belongs in `scripts/`.
- A capability boundary or portability decision belongs in `manifests/`.
- A maintenance lesson for this repo belongs in `local-docs/`.
- A live preference that should affect every Codex session belongs in
  `codex/AGENTS.md` only after review.

## Research First

For unclear changes, start by reading the current files and running the relevant
checks. Use `repo-explorer` or `workflows/read-only-research.md` when the next
step is mapping evidence, not editing.

Good research output is compact:

- question answered;
- files and symbols inspected;
- confirmed path or behavior;
- remaining risks;
- recommended next step.

## Verification

Before calling a change done:

- run `.\scripts\doctor.ps1`;
- run `.\scripts\verify-live.ps1 -SkipCodexCommand` when live drift matters;
- run the full `.\scripts\verify-live.ps1` before relying on active instruction
  loading;
- confirm changed files are either installable portable artifacts or intentionally
  repo-local docs;
- let GitHub Actions run on the PR.

Expected drift is still useful evidence. For example, branch-only changes should
show drift until the user explicitly installs them into the live Codex home.

## Failure Learning

When Codex makes a repeated mistake, record the first upstream failure in
`workflows/agent-failures.md`. Do not immediately add a global rule. Decide
whether the right fix is a clearer workflow, a focused skill, a script, a
manifest note, or a short instruction.

## Tool Surface Review

Any tool that can touch browser state, GitHub, the filesystem, local processes,
MCP servers, or network resources should have a review path in
`manifests/tool-surfaces.md`. Keep auth, cookies, generated paths, runtime pipes,
and cache state local.
