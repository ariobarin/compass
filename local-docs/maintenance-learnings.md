# Maintenance Learnings

These notes guide changes to Compass. They are repo-local learning
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

## Install Boundary

Installed agentic documentation changes future Codex behavior. It belongs in
`codex/AGENTS.md`, `codex/agents/`, or `codex/skills/`, and should describe
durable role, stance, judgment, and capability boundaries.

Installed docs should speak to the agent that will use them at runtime. State
the contract directly. Do not put provenance, dated observations, platform
caveats, or repo review history into installed skills or agents when the agent
just needs to act. Put that context in repo-maintainer docs instead.

For goal delegation, the installed skill should say how goal state works: goal
state is local to the context that activates it, delegated `/goal` text is plain
text until the child applies it, and parent completion authority stays with the
controller. The reason this wording exists belongs here, not in the runtime
skill.

Repo-maintainer documentation helps humans and agents maintain this repository.
It belongs in the root `AGENTS.md`, `workflows/`, `local-docs/`, `manifests/`,
or `scripts/`, and should explain promotion rules, checks, local review habits,
and portability boundaries. These surfaces are not copied into live Codex as
agent behavior.

## Context Discipline

- Keep `codex/AGENTS.md` short. It should hold personal defaults that genuinely
  apply everywhere.
- Treat `codex/AGENTS.md` as the portable copy of the live global
  `~/.codex/AGENTS.md`, not as repo-local maintenance notes.
- If a rule only makes sense while editing Compass, it belongs in the
  repo-root `AGENTS.md`, `workflows/`, or `local-docs/`, not in
  `codex/AGENTS.md`.
- Put detailed guidance in the narrowest surface: installed skill references for
  reusable agent capability, workflows or local docs for repo maintenance,
  scripts for mechanical checks, and manifests for boundaries.
- Add durable guidance only after repeated mistakes or clear workflow friction.
- Prefer evidence over preference. A new rule should name the failure it
  prevents or the review path it improves.
- Avoid framework-shaped prompt systems unless a real recurring task needs that
  structure.

## Change Routing

Use `workflows/addition-intake.md` when promoting a new durable artifact into the
portable repo.

- A repeated Compass maintenance process belongs in `workflows/`.
- A reusable personal skill that should be installed into this setup's active
  personal skill store belongs in `codex/skills/`.
- `codex/skills/` is the reviewed source tree for user skills that install to
  `$HOME/.agents/skills`.
- Project `.agents/skills` discovery belongs in the target repo, not in
  Compass.
- A reusable custom agent that should be installed belongs in `codex/agents/`.
- A project-specific custom agent belongs in the target repo.
- A shareable bundle of skills, hooks, apps, or MCP config belongs in a plugin
  repo or repo-scoped plugin folder, not in the live plugin cache.
- A mechanical or reproducible repo check belongs in `scripts/`.
- A repo-side capability boundary or portability decision belongs in
  `manifests/`.
- A repo-side maintenance lesson belongs in `local-docs/`.
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
show drift until the user explicitly installs them into the live install targets.

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

## Local Override Surfaces

Keep local override and approval-accumulation surfaces out of this repo unless
they are deliberately adopted as reviewed portable policy.

- `AGENTS.override.md` stays local.
- `rules/` stays local by default.
- Project `AGENTS.md`, project `.codex/agents/`, and project skill folders stay
  with the target repo.
