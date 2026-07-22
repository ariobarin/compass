# Source-of-truth register

This register is the single inventory of every fact that more than one place
used to maintain. For each fact family it names exactly one canonical source,
the mechanism that binds every other copy to it, the check that enforces the
binding, and the current status. Later consolidation PRs update a row's status
from `planned` to `consolidated`, or to `canonical` when the binding already
existed before the audit.

Mechanism values:

- `generate`: a secondary copy is derived from the canonical source by a script
  under `scripts/generators/` and committed.
- `link`: a secondary copy is reduced to a pointer at the canonical source.
- `accepted`: intentional separation, documented below, no binding needed.
- `pin`: copies stay, but a policy contract or check requires a shared phrase
  or structural anchor, so drift fails doctor.
- `keep`: already single-source before the audit.

Status values:

- `canonical`: already one source before the audit.
- `consolidated`: the binding shipped.
- `planned`: the binding is designed but not yet shipped.
- `accepted`: intentional separation, no binding planned.

| ID | Fact family | Canonical source | Mechanism | Bound by | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Control-state templates | workflows/templates/*.md, project-template pair, and using-goals blocks | pin | template-anchors.ps1 | consolidated |
| 2 | Retired skill names | manifests/retired-skills.json | pin | retired-skills.ps1 and test-compass-architecture.py | consolidated |
| 3 | Skill roster | codex/skills/*/ and manifests/portable-files.toml | keep | skill-sources.ps1 | canonical |
| 4 | Required-files list | git index (tracked files) | generate | required-files.ps1 | consolidated |
| 5 | Doctor dispatch list | manifests/doctor-checks.json | generate | doctor.ps1 | consolidated |
| 6 | Codex and Claude agent pairs | codex/agents/*.toml and carried/*/agents/*.toml | generate | claude.ps1 and generated-artifacts.ps1 | consolidated |
| 7 | Worker Result enum | manifests/policy-contracts.json | pin | policy-contracts.ps1 | consolidated |
| 8 | Model-tier defaults | manifests/model-tiers.json | generate | model-tiers.ps1 | consolidated |
| 9 | Ledger schema version | scripts/_orchestration_ledger_core.py | generate | generated-artifacts.ps1 | consolidated |
| 10 | Skill-description length cap | scripts/common.ps1 MaxSkillDescriptionLength | pin | test-compass-architecture.py | consolidated |
| 11 | Routing source reference (checklist prose deferred) | workflows/addition-intake.md | pin | policy-contracts.ps1 | consolidated |
| 12 | Glossary terms | glossary.md | link | editorial convention | accepted |
| 13 | Shared runtime-global prose | manifests/policy-contracts.json | pin | policy-contracts.ps1 | consolidated |

## Intentional separations

These duplications are deliberate and stay. They are listed here so future
audits do not re-flag them.

- `codex/AGENTS.md`, `claude/CLAUDE.md`, and `apps/compass-mcp/profile.md`
  serve different runtimes. Policy contracts pin the applicable shared blocks:
  Writing, Git, and PR prose across all three surfaces, plus continuity,
  planning, repository, and Windows prose across the Codex and Claude globals.
  Runtime-specific deltas stay separate.
- `workflows/templates/*.md` (maintainer, long form),
  `codex/skills/workspace-steward/references/project-template` copies (starter
  pack), and the embedded blocks in
  `codex/skills/using-goals/references/goal-contracts.md` serve different
  audiences. All are intentional canonicals with different field sets;
  `template-anchors.ps1` pins their shared structural anchors so none silently
  loses its identity.
- `workflows/plan-template.md` is elaborated maintainer guidance distinct from
  the bare `workflows/templates/plan.md` template. Both stay.
- `scripts/test-compass-architecture.py` asserts skill names as a behavior
  contract, not as a second roster. The manifest remains the roster.
- `scripts/doctor/checks/agents.ps1` allowed-models allowlist is a different
  fact from the model-tier defaults in `manifests/model-tiers.json`. Both stay.
- `codex/skills/workspace-steward/references/project-template/glossary.md` is a
  starter-pack glossary for adopting workspaces, distinct from the terminology
  authority at root `glossary.md`. It stays separate so a new workspace gets a
  compact self-contained reference.
- `.gitignore` governs the working tree while `manifests/portable-files.toml`
  `[local_only]` governs install boundaries. Every `[local_only].files` entry
  must also appear in `.gitignore`; unrelated repository ignore patterns remain
  independent.

## Deferred decisions (need user input)

- Cluster 1 (control-state templates): the three template families keep
  intentionally different field sets. Full generation remains deferred until a
  canonical field set is chosen for each control document. The shipped
  `template-anchors.ps1` pin covers the shared goal, catalog, assignment, and
  checkpoint identities, plus plan and decision identities where both file
  families provide those artifacts, so the registered binding is consolidated.
- Cluster 13 (shared runtime-global prose): policy contracts pin the verbatim
  Writing, Git, and PR blocks across `codex/AGENTS.md`, `claude/CLAUDE.md`, and
  `apps/compass-mcp/profile.md`, plus the shared continuity, planning,
  repository, and Windows blocks across the Codex and Claude globals. Full
  generation (a `generate-runtime-globals.py` reassembling each file from a
  shared source plus runtime deltas) was deferred because these are load-bearing
  runtime instructions; the pin is the safe fallback authorized in the plan.
- Cluster 11 (routing table and update-together checklist): the canonical
  routing source `workflows/addition-intake.md` is already referenced from the
  key surfaces, and policy contracts now require the two skill-authoring
  surfaces to keep that reference. Cutting the surface-specific restatements of
  the update-together checklist is editorial work that needs a per-surface
  review, so it is deferred; the pins bind the canonical source in the meantime.
- Cluster 12 (glossary terms): `glossary.md` is the named terminology authority.
  Skills should link to it rather than redefine terms, but enforcing that
  mechanically would be brittle, so it stays an editorial convention with no
  mechanical check. A sweep of the most redundant in-skill re-definitions is
  deferred for per-surface review.

## Status summary

Of the 13 fact families, 12 are consolidated or already canonical and 1 is
accepted as an intentional separation (cluster 12 glossary). The
surface-specific update-together checklist prose (part of cluster 11) is
deferred as editorial work. The consolidations are
enforced mechanically: new manifests and doctor checks (`retired-skills`,
`model-tiers`, `generated-artifacts`, `source-of-truth`, `template-anchors`),
generators under `scripts/generators/`, policy-contract pins, git-derived
required files, and dynamic doctor dispatch.

Required files (cluster 4) use the git index as the source of repository
membership. The architecturally mandatory entrypoints the old hand-written list
covered are already enforced elsewhere: root docs and `[repo_only]` files by
`manifest-boundaries.ps1`, each manifest by its own check, Codex agents by
`portable-data.py`, skills by `skills.ps1`, runtime globals by policy contracts,
and test scripts by CI. No broad path roster was restored; the one soft spot
(generator deletion) is review-visible. Run `pwsh scripts/doctor.ps1` to verify
the whole binding holds.
