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
- `keep`: already single-source before the audit.

Status values:

- `canonical`: already one source before the audit.
- `consolidated`: the binding shipped.
- `planned`: the binding is designed but not yet shipped.
- `accepted`: intentional separation, no binding planned.

| ID | Fact family | Canonical source | Mechanism | Bound by | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Control-state templates | workflows/templates/*.md | generate | generated-artifacts.ps1 | planned |
| 2 | Retired skill names | manifests/retired-skills.json | generate | retired-skills.ps1 | consolidated |
| 3 | Skill roster | codex/skills/*/ and manifests/portable-files.toml | keep | skill-sources.ps1 | canonical |
| 4 | Required-files list | git index (tracked files) | generate | required-files.ps1 | consolidated |
| 5 | Doctor dispatch list | scripts/doctor/checks/*.ps1 on disk | generate | doctor.ps1 | consolidated |
| 6 | Codex and Claude agent pairs | codex/agents/*.toml and carried/*/agents/*.toml | generate | claude.ps1 and generated-artifacts.ps1 | consolidated |
| 7 | Worker Result enum | manifests/policy-contracts.json | keep | policy-contracts.ps1 | canonical |
| 8 | Model-tier defaults | manifests/model-tiers.json | generate | model-tiers.ps1 | consolidated |
| 9 | Ledger schema version | scripts/_orchestration_ledger_core.py | generate | generated-artifacts.ps1 | consolidated |
| 10 | Skill-description length cap | scripts/common.ps1 MaxSkillDescriptionLength | generate | test-compass-architecture.py | consolidated |
| 11 | Routing table and update-together checklist | workflows/addition-intake.md | pin | policy-contracts.ps1 | consolidated |
| 12 | Glossary terms | glossary.md | link | editorial convention | accepted |
| 13 | Shared user-preference prose | manifests/policy-contracts.json | pin | policy-contracts.ps1 | consolidated |

## Intentional separations

These duplications are deliberate and stay. They are listed here so future
audits do not re-flag them.

- `codex/AGENTS.md`, `claude/CLAUDE.md`, and `apps/compass-mcp/profile.md`
  serve different runtimes. PR11 generates the shared Writing, Git, and PR prose
  from one source while the runtime-specific deltas stay separate.
- `workflows/templates/*.md` (maintainer, long form) and the generated
  `codex/skills/workspace-steward/references/project-template` copies (starter
  pack) serve different audiences. One is canonical, the other is generated.
- `workflows/plan-template.md` is elaborated maintainer guidance distinct from
  the bare `workflows/templates/plan.md` template. Both stay.
- `scripts/test-compass-architecture.py` asserts skill names as a behavior
  contract, not as a second roster. The manifest remains the roster.
- `scripts/doctor/checks/agents.ps1` allowed-models allowlist is a different
  fact from the model-tier defaults in `manifests/model-tiers.json`. Both stay.

## Deferred decisions (need user input)

- Cluster 1 (control-state templates): `workflows/templates/*.md`,
  `codex/skills/workspace-steward/references/project-template/local-docs/*/TEMPLATE.md`,
  `workflows/plan-template.md`, and the embedded blocks in
  `codex/skills/using-goals/references/goal-contracts.md` have genuinely
  different field sets per audience, not accidental drift. For example the plan
  templates use different status enums and different sections (`Change Rule`
  versus `Next Principal Action` and `Open Decisions`). Generating any site from
  another requires a decision on the canonical field set for each control
  document (plan, goal, catalog, assignment, checkpoint, decision). PR8 is
  deferred until that reconciliation is decided, so these stay independent.
- Cluster 13 (shared user-preference prose): the verbatim Writing and Git
  sections across `codex/AGENTS.md`, `claude/CLAUDE.md`, and
  `apps/compass-mcp/profile.md` are bound by policy-contract pins so drift fails
  doctor. Full generation (a `generate-runtime-globals.py` reassembling each
  file from a shared source plus runtime deltas) was deferred because these are
  load-bearing runtime instructions; the pin is the safe fallback authorized in
  the plan.
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
