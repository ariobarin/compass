# Skill Retrieval Audit

This audit packet covers installed skill frontmatter descriptions. Skill
descriptions are runtime retrieval context: they decide whether a skill enters a
task before the agent reads the skill body.

Packet status:

- Created after reviewing current manifest-listed Codex skill descriptions and
  #183 review-gate state.
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

### S1: Current descriptions are specific enough to keep

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

### S2: Retrieval metadata should stay visible in future audits

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
  real use shows a skill was retrieved too broadly or missed when needed.

Recommended PR:

- Add this audit packet and link it from local review-program handoff docs.

## Verification

Commands used while preparing this audit:

```powershell
git status --short --branch
gh pr view 183 --json number,url,title,isDraft,baseRefName,headRefName,headRefOid,reviewDecision,statusCheckRollup,comments,reviews
Get-Content -Raw manifests\portable-files.toml
Get-ChildItem codex\skills -Directory | ForEach-Object { $skill = $_.Name; $file = Join-Path $_.FullName 'SKILL.md'; $desc = Select-String -Path $file -Pattern '^description:' | Select-Object -First 1; "$skill`t$($desc.Line)" }
```
