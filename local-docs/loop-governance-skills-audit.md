# Loop Governance Skills Audit

This audit covers Queue 2 from `local-docs/compass-surface-inventory.md`.
It reviews the installed skills that shape long-running agent loops before any
skill text is rewritten.

Branch context:

- Base stack: PR #106 through PR #110
- Inspected current worktree, not memory, for file content
- No runtime skill text was changed in this audit

## Surfaces Reviewed

Codex skills:

- `codex/skills/compass/SKILL.md`
- `codex/skills/using-codex-goals/SKILL.md`
- `codex/skills/using-codex-goals/references/goal-contracts.md`
- `codex/skills/orchestration-controller/SKILL.md`
- `codex/skills/orchestration-controller/references/controller-principles.md`
- `codex/skills/subagent-driven-development/SKILL.md`
- `codex/skills/subagent-driven-development/implementer-prompt.md`
- `codex/skills/subagent-driven-development/spec-reviewer-prompt.md`
- `codex/skills/subagent-driven-development/code-quality-reviewer-prompt.md`
- `codex/skills/monitor-to-completion/SKILL.md`
- `codex/skills/input-token-economy/SKILL.md`
- `codex/skills/root-cause-not-symptom/SKILL.md`

Claude mirrors:

- `claude/skills/compass/SKILL.md`
- `claude/skills/orchestration-controller/SKILL.md`
- `claude/skills/subagent-driven-development/SKILL.md`

Manifest evidence:

- `using-codex-goals` is Codex-only.
- `monitor-to-completion` and `input-token-economy` are Claude-derived from
  Codex source.
- `root-cause-not-symptom` is Codex-only.

## Standard

Loop governance skills earn global runtime context when they do at least one of
these jobs:

- keep a durable goal from collapsing into a tidy blocker report;
- preserve parent-child authority boundaries;
- restore worker agency without letting the controller become the worker;
- turn waiting into either a mechanical wait or a real orchestration heartbeat;
- prevent repeated symptom patching;
- reduce context load so long work stays viable.

The question is not whether these skills are long. The question is whether they
make future loops stronger than a vanilla agent would be.

## Findings

### L1: The loop family belongs in global runtime context

Evidence:

- `using-codex-goals` defines completion predicates, blocker pressure, goal
  state boundaries, child activation, and evidence requirements.
- `orchestration-controller` defines the control-plane role and refuses worker
  status as final truth.
- `subagent-driven-development` governs same-session fan-out with explicit
  dispatch, review, and worker-status handling.
- `monitor-to-completion` prevents model-as-timer loops.
- `input-token-economy` protects long sessions from runaway context cost.
- `root-cause-not-symptom` forces cause statements before patches.
- `compass` routes durable setup work to the right source surfaces.

Decision:

- Do not demote this family into carried capabilities.
- Audit for pruning and mirror consistency instead.

Recommended PR:

- None for demotion.

### L2: The family has a coherent pressure pattern

Evidence:

- `using-codex-goals` says a blocker report is not completion and keeps the
  goal active until evidence proves done.
- `orchestration-controller` treats `DONE`, `BLOCKED`, `NEEDS_CONTEXT`,
  `WAITING_ON_REVIEW`, and `NO_RESULTS` as signals to interpret.
- `subagent-driven-development` requires worker reports to return concrete
  status and makes `BLOCKED` diagnostic, not terminal.
- `monitor-to-completion` splits mechanical waiting from orchestration
  heartbeat work.
- `root-cause-not-symptom` refuses symptom disappearance as proof of cause
  removal.

Decision:

- Preserve this pressure pattern. It is the core of loop engineering.

Recommended PR:

- Future pruning should keep the shared pattern visible: status claims are
  evidence prompts, not endpoints.

### L3: `compass` needs the new review-program route

Evidence:

- `compass` tells maintainers to read root `AGENTS.md`,
  `local-docs/maintenance-learnings.md`, `workflows/portable-config.md`, and
  `workflows/addition-intake.md`.
- The new review program, surface inventory, carried design, and carried route
  now govern audits and skill pruning, but `compass` does not mention them.

Decision:

- The skill remains a global keeper.
- It should learn the review route without absorbing the full review program.

Recommended PR:

- Add a short `Read First` bullet to `codex/skills/compass/SKILL.md` and
  `claude/skills/compass/SKILL.md`: read
  `workflows/compass-review-program.md` before auditing or pruning installed
  skills, agents, hooks, or maintainer guidance.

Follow-up status:

- Completed by the review-program routing PR. The Compass skill points audit
  and pruning work at `workflows/compass-review-program.md`. Later hook-routing
  PRs extended the same route to installed hook surfaces.

### L4: `root-cause-not-symptom` should be mirrored or explicitly justified

Evidence:

- `root-cause-not-symptom` is broad loop-governance behavior: it prevents
  symptomatic fixes before patching.
- It has no obvious Codex-only dependency in the text inspected.
- It is not listed under `[claude].skills` or `[claude].derived_skills`.

Decision:

- The skill belongs globally for Codex.
- The Claude gap should be closed or documented.

Recommended PR:

- Add `root-cause-not-symptom` to `[claude].derived_skills` if install-time
  derivation works cleanly. Otherwise document why it stays Codex-only.

Follow-up status:

- Completed by the Claude derivation PR. `root-cause-not-symptom` is now listed
  under `[claude].derived_skills`.

### L5: `using-codex-goals` is correctly Codex-only

Evidence:

- The skill depends on Codex goal state, `create_goal`, `get_goal`, and
  `update_goal`.
- `workflows/claude-config.md` says Codex-only features such as `/goal` should
  be dropped or reworded when porting to Claude.

Decision:

- Keep `using-codex-goals` Codex-only unless Claude gains matching goal
  runtime.

Recommended PR:

- None.

### L6: `subagent-driven-development` is the first pruning candidate, not a demotion candidate

Evidence:

- It is the longest main skill in this family at 184 lines, plus three prompt
  templates.
- Much of the length is necessary because it preserves dispatch and review
  contracts.
- The skill repeats some controller ideas from `orchestration-controller`,
  but it also owns a narrower implementation fan-out lane.
- It contains "review fallback" wording in related-skill routing. That phrase
  may be harmless in context, but the review program has already identified
  fallback-shaped language as risky when Compass controls the route.

Decision:

- Keep it global.
- Prune only after a focused read against `orchestration-controller` so the
  implementation fan-out contract stays intact.

Recommended PR:

- Audit `subagent-driven-development` against `orchestration-controller` for
  duplicated controller prose and risky fallback-shaped wording.

Follow-up status:

- Completed by `local-docs/subagent-pruning-audit.md`; the runtime pruning PR
  followed that audit.

### L7: `monitor-to-completion` and `input-token-economy` form a tight pair

Evidence:

- `monitor-to-completion` names the model-as-timer failure mode and points to
  `input-token-economy` for cost rationale.
- `input-token-economy` names the monitoring thread as the frontier case and
  points back to `monitor-to-completion`.
- Both are compact and already Claude-derived.

Decision:

- Keep both global.
- No immediate pruning needed.

Recommended PR:

- None.

## Next PR Boundaries

Recommended order:

1. Leave `using-codex-goals`, `monitor-to-completion`, and
   `input-token-economy` unchanged unless future use shows friction.

Completed follow-ups:

- `compass` now routes audit and pruning work to the review program.
- `root-cause-not-symptom` is Claude-derived.
- `subagent-driven-development` was audited and pruned against
  `orchestration-controller`.

## Verification

Commands used while preparing this audit:

```powershell
git status --short --branch
git fetch origin
gh pr view 110 --json number,state,isDraft,mergeStateStatus,baseRefName,headRefName,url,title
Get-Content -Raw <reviewed skill and reference files>
rg -n -i "fallback|best-effort|if possible|try to|maybe|manual|history|provenance|blocked|waiting|done|complete" codex\skills\<loop family>
rg -n "\[[^\]]+\]\([^\)]+\.md\)" codex\skills\<loop family>
```

The grep was an audit aid. The findings come from reading the files named
above.
