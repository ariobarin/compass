# Compass Orientation Audit

This audit covers the first queue from `local-docs/compass-surface-inventory.md`.
It reviews the surfaces that orient a fresh maintainer before deeper skill and
agent, hook, and workflow work.

Branch context:

- Base stack: PR #106 and PR #107
- Related external PR: #105, `Document loop engineering philosophy`
- Inspected current worktree, not memory, for file content

## Surfaces Reviewed

- `AGENTS.md`
- `README.md`
- `philosophy.md`
- `workflows/compass-review-program.md`
- `local-docs/maintenance-learnings.md`
- `local-docs/compass-surface-inventory.md`

## Orientation Standard

A fresh maintainer should understand these things fast:

- Compass is reviewed source, not a backup.
- Runtime context and maintainer context are different audiences.
- Installed skills and agents must speak to the agent using them.
- Installed hooks must stay narrow, mechanical, reviewed, and tested.
- Repo-only docs can preserve history, rationale, and process.
- Mechanical truth belongs in manifests, scripts, and checks.
- Pruning is not cosmetic. It removes audience mismatch and weak signal.
- Broad rewrites are wrong. The review program moves through small PRs with
  evidence.

## Findings

### O1: The orientation spine is coherent

Evidence:

- `AGENTS.md` states the install boundary, route surfaces, Compass-owned
  capability rule, Claude mirror rule, and review guidelines.
- `README.md` explains the repo layout and now points to the review program.
- `local-docs/maintenance-learnings.md` separates installed guidance from
  maintainer docs and captures exact capability contracts.
- `workflows/compass-review-program.md` defines the audit stance, inventory
  pass, pruning standard, PR rhythm, and stop conditions.
- `local-docs/compass-surface-inventory.md` maps current surfaces and audit
  queues.

Decision:

- Preserve the current split. It matches the purpose of Compass and does not
  leak maintainer process into runtime context.

Recommended PR:

- None for structure. Continue the review program from this spine.

### O2: `philosophy.md` is missing the newest doctrine on this stack

Evidence:

- Current `philosophy.md` has strong sections on judgment, roles, authority,
  evidence, human-owned power, and writing that embodies the system.
- PR #105 adds the prompt, context, and loop engineering doctrine from the
  recent discussion, but this stack does not include that branch.

Decision:

- Do not duplicate PR #105 here.
- Treat #105 as the active philosophy update for loop-engineering doctrine.

Recommended PR:

- Merge or restack #105 before using `philosophy.md` as the complete source for
  loop-engineering language.

### O3: `AGENTS.md` is already dense enough for root guidance

Evidence:

- It front-loads the repo purpose and route boundaries.
- It names the exact files that belong to installed runtime behavior.
- It directs nontrivial changes to `local-docs/maintenance-learnings.md`.
- It avoids carrying the full review program in root instructions.

Decision:

- Do not add the full review workflow to root `AGENTS.md`.
- A short pointer to `workflows/compass-review-program.md` may be useful only
  when an agent is explicitly auditing skills, agents, hooks, or maintainer
  guidance.

Recommended PR:

- Optional narrow PR: add one root-guidance bullet that says to use
  `workflows/compass-review-program.md` for Compass audits. Skip it if the
  added line feels like root bloat.

### O4: `README.md` serves public orientation, not audit execution

Evidence:

- It explains what Compass is, what it is not, repo layout, common commands,
  and high-level rules.
- It links the review program from the workflow list.
- It does not try to carry the audit rubric.

Decision:

- Keep `README.md` high-level.
- Do not move audit details into the README.

Recommended PR:

- None.

### O5: `maintenance-learnings.md` is carrying the right kind of history

Evidence:

- It records install boundaries, exact capability contracts, context
  discipline, routing, verification, failure learning, tool surface review, and
  local override surfaces.
- This history would distract a runtime agent, but it helps a maintainer avoid
  repeated mistakes.

Decision:

- Keep it as local maintainer context.
- During future audits, prune only stale or duplicated sections after a specific
  workflow or runtime surface has absorbed the live rule.

Recommended PR:

- No immediate cut. Revisit after the first few skill audits prove what
  maintainer history still earns its place.

### O6: The review program is actionable, but its first proof is still ahead

Evidence:

- `workflows/compass-review-program.md` defines classification, audit
  questions, pruning standards, PR rhythm, and stop conditions.
- This audit is the first use of that workflow against a real queue.

Decision:

- Keep the workflow unchanged for now.
- Let the first skill-family audits test whether the rubric is too broad,
  too soft, or missing a decision point.

Recommended PR:

- After auditing the loop governance skills, update the workflow only if actual
  friction appears.

### O7: The carried-but-not-global route is the first structural gap

Evidence:

- `local-docs/compass-surface-inventory.md` names a carried-but-not-global gap.
- `manifests/portable-files.toml` has global install surfaces, repo-only
  surfaces, and local-only denylist surfaces.
- There is no reviewed directory or manifest category for useful skills that
  should travel with Compass but not load into every session.

Decision:

- Do not move skills yet.
- Design the route before pruning the global skill set.

Recommended PR:

- Add a carried-but-not-global design note covering directory shape, manifest
  category, install behavior, doctor checks, Claude handling, and project opt-in.
  See `local-docs/carried-capabilities-design.md`.

Follow-up status:

- Completed by the carried-capability route stack. The route now has a design
  note, source directory, manifest section, and doctor checks.

## Next PR Boundaries

Recommended order:

1. Land #105, #106, and #107 or keep future PRs stacked explicitly.
2. Optional: add a one-line root pointer to the review program if it does not
   bloat `AGENTS.md`.
3. Audit the loop governance skills as the first runtime family:
   `compass`, `using-codex-goals`, `orchestration-controller`,
   `subagent-driven-development`, `monitor-to-completion`,
   `input-token-economy`, and `root-cause-not-symptom`.

Completed follow-ups:

- The carried-but-not-global route has been designed and wired.
- The loop governance skill audit has been completed.
- Hook surfaces have been added to the inventory and review-program route.

## Verification

Commands used while preparing this audit:

```powershell
git status --short --branch
git fetch origin
gh pr view 107 --json number,state,isDraft,mergeStateStatus,baseRefName,headRefName,url,title
gh pr view 105 --json number,state,isDraft,mergeStateStatus,baseRefName,headRefName,url,title,headRefOid
git grep -n -i "fallback\|best-effort\|compatibility\|maybe\|should\|history\|context" -- AGENTS.md README.md philosophy.md workflows/compass-review-program.md local-docs/maintenance-learnings.md
```

The grep was an audit aid, not proof of quality. The audit conclusions come
from reading the files named above.
