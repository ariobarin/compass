# PR And Review Surfaces Audit

This audit covers Queue 3 from `local-docs/compass-surface-inventory.md`.
It reviews the installed skills and agents that turn changes, reports, PRs, and
specialist requests into evidence-backed review.

No runtime text changes in this audit. The job is to decide what deserves
global context, what should be pruned, and which focused PRs should follow.

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
  re-review, stale rebuild posture, and merge boundaries.
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

### R3: `pr-review-loop` should lose fallback-shaped wording

Evidence:

- `codex/skills/pr-review-loop/SKILL.md` says: "If review is silent, use the
  approved fallback path rather than waiting passively."
- `codex/skills/pr-review-loop/references/review-loop-playbook.md` says:
  "if one reviewer is silent and fallback is allowed, use the allowed fallback
  explicitly and report which gate remains unsatisfied."
- The Claude mirror carries the same fallback-shaped wording in both files.

Decision:

- The behavior is right: passive waiting is wrong when an approved alternate
  review route exists.
- The word shape is wrong for Compass-owned review gates. It makes review
  sound like a degraded backup instead of an explicit alternate gate chosen by
  repo policy, user instruction, or tool availability.

Recommended PR:

- Replace `fallback` language in Codex and Claude `pr-review-loop` files with
  `authorized alternate review route` language.
- Preserve the rule that missing required review remains unsatisfied until the
  alternate route is named and justified.

### R4: The Claude `reviewer` coordinator is sharper than the Codex source

Evidence:

- The Codex `reviewer` agent describes Standard and Full modes, then gives
  broad routing in one opening paragraph.
- The Claude `reviewer` mirror adds a `Specialist Selection` section that says
  Standard selects only specialists whose risk is real.
- The Claude mirror adds useful constraints: never run specialists for theater,
  use `research-critic` only when external current knowledge matters, use
  `verifier` only when there is a real thing to inspect or prove, include
  `neutral-critic` only when requested or required, and do not invent findings.

Decision:

- Codex should learn the clearer selection rules.
- This is not maintainer history. It is runtime judgment for the coordinator.

Recommended PR:

- Port the useful Claude `reviewer` selection clarity back into
  `codex/agents/reviewer.toml` while preserving Codex TOML format.
- Keep Claude and Codex reviewer behavior aligned after the edit.

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

1. Update `pr-review-loop` and its Claude mirror to replace fallback-shaped
   wording with explicit alternate-review-route language.
2. Update `codex/agents/reviewer.toml` with the clearer specialist-selection
   rules already present in `claude/agents/reviewer.md`, then confirm the
   mirrors still express the same behavior.
3. Leave `pr-merge-closeout`, `action-items-to-prs`, `git-branch-resolver`,
   `specialist-review`, and the critic agents unchanged unless later use shows
   friction.

## Verification

Commands used while preparing this audit:

```powershell
git status --short --branch
git fetch origin
gh pr list --state open --json number,title,isDraft,baseRefName,headRefName,url --limit 30
Get-Content -Raw <reviewed skill, reference, and agent files>
rg -n -i "fallback|best-effort|if possible|maybe|hopefully|silent|blocked|optional|advisory|theater|evidence|review gate|current-head|merge|coordinated|specialist" codex\skills\pr-review-loop codex\skills\pr-merge-closeout codex\skills\specialist-review codex\skills\action-items-to-prs codex\skills\git-branch-resolver codex\agents claude\skills\pr-review-loop claude\skills\specialist-review claude\skills\action-items-to-prs claude\skills\git-branch-resolver claude\agents
git diff --no-index -- codex\agents\reviewer.toml claude\agents\reviewer.md
git diff --no-index -- codex\skills\pr-review-loop\SKILL.md claude\skills\pr-review-loop\SKILL.md
git diff --no-index -- codex\skills\pr-review-loop\references\review-loop-playbook.md claude\skills\pr-review-loop\references\review-loop-playbook.md
```
