# Agent Retrieval Audit

This audit packet covers installed agent descriptions. Agent descriptions are
delegation and retrieval context: they decide which specialist role a
controller can see before it reads the agent body.

Packet status:

- Created after reviewing current Codex agent descriptions, Claude agent
  frontmatter, manifest-listed agents, and #184 review-gate state.
- Use current agent metadata and `manifests/portable-files.toml` before
  deriving any routing edit from this packet.
- Treat verification commands as audit history, not current proof.

## Scope

Codex agents listed under `[claude].agents` and installed under
`codex/agents/`:

- `algorithm-critic`
- `neutral-critic`
- `repo-explorer`
- `research-critic`
- `reuse-critic`
- `reviewer`
- `verifier`

Claude mirrors under `claude/agents/`:

- `algorithm-critic`
- `neutral-critic`
- `repo-explorer`
- `research-critic`
- `reuse-critic`
- `reviewer`
- `verifier`

## Standard

An agent description should route delegation, not summarize the agent.

Good descriptions name the role, the work state that needs that role, and the
boundary that keeps the role from stealing adjacent work. They should let a
controller choose the right critic or explorer quickly without reading every
agent body.

Descriptions should avoid:

- broad "review anything" wording that hides the specialist boundary;
- soft language that makes critique feel optional;
- implementation details that belong inside the agent body;
- project-specific triggers unless the agent is intentionally project-specific;
- claims that the agent edits when its role is non-editing.

## Findings

### A1: Current Codex and Claude descriptions are aligned

Evidence:

- Codex and Claude descriptions match for all seven agents.
- `algorithm-critic` names first-principles scope, requirements, and process
  critique.
- `neutral-critic` names fresh-eyes skeptical review and says the agent is
  non-editing but able to validate.
- `repo-explorer` names read-only repository exploration and the conditions
  that justify it.
- `research-critic` names external prior art, official docs, standards,
  packages, issues, examples, and known solutions.
- `reuse-critic` names needless invention, custom machinery, duplication, and
  missed reuse.
- `reviewer` names explicit specialist-review requests and clean specialist
  handoff.
- `verifier` names executable, script, plugin, browser, visual, log, and
  artifact-backed completion proof.

Decision:

- Keep current agent descriptions.
- Do not rewrite descriptions without delegation-noise evidence from real use.

Recommended PR:

- None for runtime agent metadata now.

### A2: Agent retrieval metadata should stay visible in future audits

Evidence:

- The PR and review surfaces packet reviews agent bodies, mirrors, and review
  roles.
- Agent descriptions are still a distinct routing surface. A weak description
  can send work to the wrong critic even when the agent body is strong.
- The current metadata passes a source audit, but future delegation failures
  need a place to record whether the routing problem was in description,
  manifest placement, controller instruction, or the agent body.

Decision:

- Keep this packet as the agent-routing metadata audit surface.
- Refresh it when an agent description changes, an agent is added or removed,
  or real use shows an agent was selected too broadly or missed when needed.

Recommended PR:

- Add this audit packet and link it from local review-program handoff docs.

## Verification

Commands used while preparing this audit:

```powershell
git status --short --branch
gh pr view 184 --json number,url,title,isDraft,baseRefName,headRefName,headRefOid,reviewDecision,statusCheckRollup,comments,reviews
Get-ChildItem codex\agents -File | ForEach-Object { $name = $_.BaseName; $desc = Select-String -Path $_.FullName -Pattern '^description\s*=' | Select-Object -First 1; "$name`t$($desc.Line)" }
Get-ChildItem claude\agents -File | ForEach-Object { $name = $_.BaseName; $desc = Select-String -Path $_.FullName -Pattern '^description:' | Select-Object -First 1; "$name`t$($desc.Line)" }
rg -n -i "description|sandbox_mode|reviewer|neutral|critic|explorer|verifier|Use when|Use for|delegate|routing|frontmatter" codex\agents claude\agents manifests\portable-files.toml local-docs\pr-review-surfaces-audit.md
```
