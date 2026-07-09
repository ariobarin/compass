# PR And Review Surfaces Audit

This audit packet covers the PR and review surfaces listed in
`local-docs/compass-surface-inventory.md`. It reviews the installed skills and
agents that turn changes, reports, PRs, and specialist requests into
evidence-backed review.

Packet status:

- Refreshed after the inline review-comment follow-up landed.
- Use current review skills, reviewer agents, Claude mirrors, and open PR stack
  state before deriving new work from this packet.
- Treat verification commands as audit history, not current proof.

## Surfaces Reviewed

Codex skills:

- `codex/skills/pr-review-loop/SKILL.md`
- `codex/skills/pr-review-loop/references/review-loop-playbook.md`
- `codex/skills/pr-merge-closeout/SKILL.md`
- `codex/skills/specialist-review/SKILL.md`
- `codex/skills/action-items-to-prs/SKILL.md`
- `codex/skills/git-branch-resolver/SKILL.md`
- `codex/skills/git-branch-resolver/references/pr-host-fallbacks.md`

Claude skill mirrors:

- `claude/skills/pr-review-loop/SKILL.md`
- `claude/skills/pr-review-loop/references/review-loop-playbook.md`
- `claude/skills/specialist-review/SKILL.md`
- `claude/skills/action-items-to-prs/SKILL.md`
- `claude/skills/git-branch-resolver/SKILL.md`
- `claude/skills/git-branch-resolver/references/pr-host-fallbacks.md`

Codex agents:

- `codex/agents/algorithm-critic.toml`
- `codex/agents/neutral-critic.toml`
- `codex/agents/repo-explorer.toml`
- `codex/agents/research-critic.toml`
- `codex/agents/reuse-critic.toml`
- `codex/agents/reviewer.toml`
- `codex/agents/verifier.toml`

Claude agent mirrors:

- `claude/agents/algorithm-critic.md`
- `claude/agents/neutral-critic.md`
- `claude/agents/repo-explorer.md`
- `claude/agents/research-critic.md`
- `claude/agents/reuse-critic.md`
- `claude/agents/reviewer.md`
- `claude/agents/verifier.md`

## Standard

Review surfaces earn global runtime context when they keep work from becoming
ceremony. They must preserve:

- exact PR identity;
- current-head evidence;
- independent review gates;
- neutral handoffs;
- branch and worktree preservation;
- executable verification when the claim can be tested;
- explicit merge authority.

The question is not whether a review surface sounds rigorous. The question is
whether it forces evidence into the loop before the agent claims readiness,
merges, deletes, retargets, or escalates.

## Findings

### R1: The review family belongs in global runtime context

Evidence:

- `pr-review-loop` holds PR identity, review gates, current-head discipline,
  inline review-comment inspection, re-review, stale rebuild posture, and merge
  boundaries.
- `action-items-to-prs` turns broad reports into PR-scoped ledgers with
  verification, critic review, and merge gates.
- `git-branch-resolver` protects branches, worktrees, remote refs, and PR
  identity before refresh or cleanup.
- `specialist-review` strips parent bias before handing off to `reviewer`.
- `reviewer` coordinates specialist critics instead of turning the parent
  agent's narrative into review.
- `neutral-critic`, `verifier`, `reuse-critic`, `research-critic`, and
  `algorithm-critic` each attack a distinct failure mode.
- `repo-explorer` gives read-only evidence gathering a narrow owner.

Decision:

- Keep this family globally installed.
- Do not move it to carried capabilities.

### R2: `pr-merge-closeout` is correctly Codex-only

Evidence:

- `pr-merge-closeout` is a seven-line delegator to `pr-review-loop`.
- Its unique behavior is merge closeout plus thread archive on success.
- The live thread archive behavior is Codex-app shaped and is not mirrored in
  Claude skills.
- It is present in the Codex skill manifest and absent from Claude skills.

Decision:

- Keep it Codex-only unless Claude gains matching thread archive semantics.
- Do not expand the skill unless real closeout failures show missing contract.

Recommended PR:

- None.

### R3: `pr-review-loop` alternate review wording is current

Evidence:

- Codex and Claude `pr-review-loop` now say to use an authorized alternate
  review route when review is silent.
- The rule still requires the alternate route to be named and justified.
- Missing required review remains unsatisfied until the authorized alternate
  route is explicit.
- Codex and Claude `pr-review-loop` now require inline review comments to be
  inspected separately from top-level review text before readiness or merge
  safety is claimed.

Decision:

- Keep the current authorized alternate-review-route language.
- Keep inline review-comment inspection as runtime PR-loop guidance, not only
  repo-maintainer workflow guidance.
- Do not restore fallback-shaped wording for Compass-owned review gates.

Recommended PR:

- None now.

Follow-up status:

- Completed by the review fallback wording PR. Codex and Claude
  `pr-review-loop` now use authorized alternate-review-route language.
- Current follow-up adds inline review-comment inspection to Codex and Claude
  `pr-review-loop` runtime guidance after current PR evidence showed top-level
  clean review text can coexist with actionable inline comments.

### R4: The reviewer coordinators are aligned

Evidence:

- Codex and Claude `reviewer` both carry `Specialist Selection` guidance.
- Both say Standard mode selects only specialists whose risk is real.
- Both prevent specialist review from becoming theater and tell the coordinator
  not to invent findings.

Decision:

- Keep the coordinator selection rules aligned across Codex and Claude.
- Preserve runtime judgment in the installed reviewer surfaces.

Recommended PR:

- None now.

Follow-up status:

- Completed by the reviewer-selection PR. Codex and Claude `reviewer` now both
  carry `Specialist Selection` guidance.

### R5: The critic agents are strong but intentionally sharp

Evidence:

- `algorithm-critic` explicitly deletes before optimizing.
- `neutral-critic` ignores author framing and orders real problems first.
- `research-critic` refuses memory as research and requires primary sources
  when current external knowledge matters.
- `reuse-critic` attacks custom machinery before accepting invention.
- `verifier` converts completion claims into checks against reality.

Decision:

- Keep these agents global.
- Do not soften the language. The sharpness is role-critical.

Recommended PR:

- None now.

### R6: `repo-explorer` has the right sandbox boundary

Evidence:

- `repo-explorer` is explicitly read-only.
- `codex/agents/repo-explorer.toml` sets `sandbox_mode = "read-only"`.
- `scripts/doctor/checks/agents.ps1` checks for read-only agent text without a
  read-only sandbox.

Decision:

- Keep the agent global and read-only.
- No pruning needed.

Recommended PR:

- None now.

### R7: `git-branch-resolver` is long but procedure-heavy for a reason

Evidence:

- The skill is 188 lines plus a 46-line PR-host reference.
- It owns destructive boundaries: branch deletion, worktree removal,
  retargeting, fetch and prune, preservation branches, and remote state.
- Its procedure is not replacing judgment. It prevents data loss.

Decision:

- Keep the length for now.
- Do not prune until a branch-resolution failure points to a specific weak or
  distracting section.

Recommended PR:

- None now.

### R8: `action-items-to-prs` is aligned with the review program

Evidence:

- It starts with the source artifact, extracts an item ledger, groups by
  reviewer context and verification scope, stages explicit paths only, records
  checks, and merges only when authorized.
- Claude differs only by replacing Codex `/goal` wording with generic durable
  goal-contract wording.

Decision:

- Keep global.
- No immediate pruning needed.

Recommended PR:

- None now.

## Next PR Boundaries

Recommended order:

1. Leave `pr-merge-closeout`, `action-items-to-prs`, `git-branch-resolver`,
   `specialist-review`, and the critic agents unchanged unless later use shows
   friction.

Completed follow-ups:

- `pr-review-loop` fallback-shaped wording was replaced.
- `pr-review-loop` gained inline review-comment inspection.
- Codex `reviewer` gained the specialist-selection clarity already present in
  the Claude mirror.

## Verification

Commands used while preparing this audit:

```powershell
git status --short --branch
git fetch origin
gh pr list --state open --json number,title,isDraft,baseRefName,headRefName,url --limit 30
Get-Content -Raw <reviewed skill, reference, and agent files>
rg -n -i "fallback|authorized alternate|silent|blocked|optional|advisory|theater|evidence|review gate|current-head|merge|coordinated|specialist" codex\skills\pr-review-loop codex\skills\pr-merge-closeout codex\skills\specialist-review codex\skills\action-items-to-prs codex\skills\git-branch-resolver codex\agents claude\skills\pr-review-loop claude\skills\specialist-review claude\skills\action-items-to-prs claude\skills\git-branch-resolver claude\agents
rg -n "authorized alternate review route|Specialist Selection|for theater|do not invent findings" codex\skills\pr-review-loop claude\skills\pr-review-loop codex\agents\reviewer.toml claude\agents\reviewer.md
rg -n "inline review comments|top-level review text|pull review comments" codex\skills\pr-review-loop claude\skills\pr-review-loop workflows\compass-review-program.md local-docs\compass-review-state.md
```
