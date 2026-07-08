# Skill Retrieval Audit

This audit packet covers installed skill frontmatter descriptions. Skill
descriptions are runtime retrieval context: they decide whether a skill enters a
task before the agent reads the skill body.

Packet status:

- Refreshed after Codex review on #184 pointed out that Claude installed skill
  descriptions are also runtime retrieval context.
- Use current `SKILL.md` frontmatter and `manifests/portable-files.toml` before
  deriving any retrieval edit from this packet.
- Treat verification commands as audit history, not current proof.

## Scope

Codex installed skills listed under `[agents].skills` in
`manifests/portable-files.toml`:

- `action-items-to-prs`
- `benchmark-infra-reviewer`
- `benchmark-run-operator`
- `compass`
- `git-branch-resolver`
- `grill-me`
- `input-token-economy`
- `monitor-to-completion`
- `orchestration-controller`
- `pr-merge-closeout`
- `pr-review-loop`
- `root-cause-not-symptom`
- `specialist-review`
- `subagent-driven-development`
- `to-prd`
- `update-compass`
- `using-codex-goals`
- `webmcp-eval-triage`
- `webmcp-tool-authoring`
- `webmcp-verify-tool`
- `workspace-steward`
- `write-a-skill`

Claude direct skills listed under `[claude].skills` in
`manifests/portable-files.toml`:

- `action-items-to-prs`
- `benchmark-infra-reviewer`
- `benchmark-run-operator`
- `compass`
- `git-branch-resolver`
- `grill-me`
- `orchestration-controller`
- `pr-review-loop`
- `specialist-review`
- `subagent-driven-development`
- `to-prd`
- `write-a-skill`

Claude derived skills listed under `[claude].derived_skills`:

- `input-token-economy`
- `monitor-to-completion`
- `root-cause-not-symptom`
- `workspace-steward`

## Standard

A skill description is not a summary. It is retrieval law.

Good descriptions name the work state where the skill belongs, not the history
of why the skill exists. They should be narrow enough to avoid ordinary-task
noise and strong enough to pull the skill in when the task would fail without
it.

Descriptions should avoid:

- project-specific triggers unless the skill is intentionally project-specific;
- vague "help with" phrasing;
- maintainer history;
- compatibility or fallback language;
- broad nouns that retrieve the skill for work it should not own.

## Findings

### S1: Current Codex descriptions are specific enough to keep

Evidence:

- Each manifest-listed Codex skill has a `description:` line.
- Descriptions mostly name a concrete work state: PR review, benchmark
  operation, Compass maintenance, branch resolution, mechanical waiting,
  root-cause diagnosis, WebMCP verification, workspace stewardship, or skill
  authoring.
- Domain-shaped skills use domain names because the domain is the retrieval
  trigger. That is not project leakage by itself.
- `compass` explicitly targets edits to installed skills, agents, hooks,
  workflows, manifests, scripts, or install wiring.
- `subagent-driven-development` is narrow: approved implementation plans with
  mostly independent tasks.
- `update-compass` is narrow: live Codex setup refreshes from reviewed Compass
  source.

Decision:

- Keep current Codex skill descriptions.
- Do not rewrite descriptions without retrieval-noise evidence from real use.

Recommended PR:

- None for runtime description edits now.

### S2: Current Claude descriptions are specific enough to keep

Evidence:

- Each manifest-listed direct Claude skill has a `description:` line.
- Direct Claude descriptions match the Codex descriptions where the same
  wording applies.
- `write-a-skill` differs intentionally: Claude says "portable skills" instead
  of "portable Codex skills" because the Claude skill should not imply Codex
  runtime ownership.
- Derived Claude skills use Codex source descriptions at install time, so their
  retrieval wording is covered by the Codex source audit unless Claude later
  needs runtime-specific wording.

Decision:

- Keep current Claude direct and derived skill descriptions.
- Do not rewrite Claude descriptions without retrieval-noise evidence from real
  use or a runtime-specific Claude need.

Recommended PR:

- None for runtime description edits now.

### S3: Retrieval metadata should stay visible in future audits

Evidence:

- Earlier audit packets review skill bodies, references, mirrors, and manifest
  placement.
- Retrieval descriptions are the first line the skill retriever sees, and a bad
  description can load the wrong context even when the skill body is good.
- The current descriptions pass a source audit, but the review program should
  treat them as their own runtime surface when future retrieval noise appears.

Decision:

- Keep this packet as the retrieval-metadata audit surface.
- Refresh it when a skill description changes, a new global skill is added, or
  real use shows a Codex or Claude skill was retrieved too broadly or missed
  when needed.

Recommended PR:

- Add this audit packet and link it from local review-program handoff docs.

## Verification

Commands used while preparing this audit:

```powershell
git status --short --branch
gh pr view 183 --json number,url,title,isDraft,baseRefName,headRefName,headRefOid,reviewDecision,statusCheckRollup,comments,reviews
Get-Content -Raw manifests\portable-files.toml
Get-ChildItem codex\skills -Directory | ForEach-Object { $skill = $_.Name; $file = Join-Path $_.FullName 'SKILL.md'; $desc = Select-String -Path $file -Pattern '^description:' | Select-Object -First 1; "$skill`t$($desc.Line)" }
Get-ChildItem claude\skills -Directory | ForEach-Object { $skill = $_.Name; $file = Join-Path $_.FullName 'SKILL.md'; $desc = Select-String -Path $file -Pattern '^description:' | Select-Object -First 1; "$skill`t$($desc.Line)" }
Select-String -Path manifests\portable-files.toml -Pattern "\[claude\]|skills =|derived_skills|workspace-steward|monitor-to-completion|input-token-economy|root-cause-not-symptom" -Context 0,18
```
