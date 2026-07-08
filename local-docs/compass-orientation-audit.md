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

### O2: `philosophy.md` now carries the loop doctrine

Evidence:

- PR #105, `Document loop engineering philosophy`, is merged.
- Current `philosophy.md` has strong sections on judgment, roles, authority,
  evidence, human-owned power, writing that embodies the system, and durable
  guidance that shapes agent behavior.

Decision:

- Treat `philosophy.md` as the current doctrine source for orientation-level
  loop-engineering language.
- Do not duplicate that doctrine into root guidance, README, or runtime skills
  without a narrower audience need.

Recommended PR:

- None.

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

- Completed by the root audit pointer PR. The added root-guidance bullet points
  Compass audits to `workflows/compass-review-program.md` without carrying the
  full rubric.

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

### O6: The review program has working proof

Evidence:

- `workflows/compass-review-program.md` defines classification, audit
  questions, pruning standards, PR rhythm, and stop conditions.
- The review stack has now used that workflow across orientation, loop
  governance, review surfaces, domain-shaped skills, writing skills,
  maintainer workflows, mechanical truth, and hook surfaces.
- Later refresh PRs keep audit packets aligned when completed follow-ups make
  old recommendations stale.

Decision:

- Keep the workflow as the active route for Compass audits.
- Update it only when actual review friction exposes a missing decision point.

Recommended PR:

- None now.

### O7: The carried-but-not-global route is wired

Evidence:

- `local-docs/carried-capabilities-design.md` defines the route, eligibility
  test, source shape, manifest contract, demotion flow, promotion flow, project
  opt-in, Claude handling, and doctor checks.
- `manifests/portable-files.toml` lists `carried` as repo-only and defines
  `[carried]` lists for Codex and Claude skills and agents.
- `local-docs/compass-surface-inventory.md` now names the carried route as
  current state instead of an open gap.

Decision:

- Do not move skills until an audit proves a capability fails the global-install
  test.
- Use the carried route for useful material that should travel with Compass but
  not load into every session.

Recommended PR:

- None now.

Follow-up status:

- Completed by the carried-capability route stack. The route now has a design
  note, source directory, manifest section, and doctor checks.

## Next PR Boundaries

Recommended order:

1. Keep future PRs stacked explicitly until the surface-inventory branch or its
   successor lands.

Completed follow-ups:

- The carried-but-not-global route has been designed and wired.
- PR #105 has landed, so `philosophy.md` is the current doctrine source.
- The loop governance skill audit has been completed.
- Hook surfaces have been added to the inventory and review-program route.
- Root guidance now points Compass audits to
  `workflows/compass-review-program.md`.

## Verification

Commands used while preparing this audit:

```powershell
git status --short --branch
git fetch origin
gh pr view 107 --json number,state,isDraft,mergeStateStatus,baseRefName,headRefName,url,title
gh pr view 105 --json number,state,isDraft,mergeStateStatus,baseRefName,headRefName,url,title,headRefOid
rg -n "compass-review-program|carried|\\[carried\\]|Completed follow-ups|Audit packet" AGENTS.md README.md workflows local-docs manifests\portable-files.toml
Select-String -Path manifests\portable-files.toml -Pattern "\\[carried\\]|carried"
```

The grep was an audit aid, not proof of quality. The audit conclusions come
from reading the files named above.
