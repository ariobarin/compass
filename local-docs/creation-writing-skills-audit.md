# Creation And Writing Skills Audit

This audit covers Queue 5 from `local-docs/compass-surface-inventory.md`.

Scope:

- `codex/skills/grill-me`
- `codex/skills/to-prd`
- `codex/skills/update-compass`
- `codex/skills/write-a-skill`
- Claude mirrors for shared behavior

Purpose: make the planning, writing, update, and skill-authoring surfaces carry
the same standard as Compass itself: understand the job, talk to the right
agent, cut what does not change behavior, and make placement decisions real.

## Current Shape

Installed state:

- Codex installs all four skills.
- Claude installs `grill-me`, `to-prd`, and `write-a-skill`.
- `update-compass` is Codex-only because it updates the live Codex setup from
  the reviewed Compass `origin/main`.

Size:

- `grill-me`: 32 lines in Codex and Claude.
- `to-prd`: 92 lines in Codex and Claude.
- `update-compass`: 19 Codex-only lines.
- `write-a-skill`: 187 Codex lines, 175 Claude lines.

Mirror state:

- `grill-me` and `to-prd` are direct mirrors except for Codex
  `agents/openai.yaml` metadata.
- `write-a-skill` differs intentionally. Codex needs `codex/skills`,
  `agents/openai.yaml`, and Codex validation commands. Claude needs
  `claude/skills`, no `agents/openai.yaml`, and explicit mirror guidance.

## Findings

### Keep `grill-me` Global

`grill-me` belongs in the global bundle.

It is dense, concrete, and aimed at the invoking agent. It does not explain why
the skill exists as history. It makes the loop behavior real: one sharp
question, a recommended answer when useful, and a hard stop when the plan has
enough decisions, risks, and next actions.

No pruning is needed now.

### Keep `to-prd` Global

`to-prd` belongs in the global bundle.

It has the right audience boundary. It drafts from available context, refuses to
publish to an external tracker without an explicit user request, and treats
tracker metadata as a target-system concern instead of PRD text.

No pruning is needed now.

### Keep `update-compass` Codex-Only

`update-compass` should stay Codex-only.

It is not a general writing or maintenance skill. It operates on the live Codex
setup, fetches the reviewed Compass `origin/main`, runs the updater, and reports
the installed state. A Claude mirror would mostly restate work that Claude does
not own.

No pruning is needed now.

### Keep `write-a-skill` Global

`write-a-skill` belongs in the global bundle.

Skill authoring is one of the highest-leverage Compass operations. Bad skill
creation pollutes future context. Good skill creation compounds. This surface
must remain always available because it protects the installed bundle from weak
or misplaced additions.

The skill is longer because it owns real wiring: metadata, source roots,
manifest entries, Codex prompts, Claude mirrors, validation, and install
boundaries. The length is justified, and the two earlier corrections now define
the current placement and validation contract.

### `write-a-skill` Teaches The Carried Route

`write-a-skill` now makes new skill work choose among:

- globally installed runtime skill;
- carried but not global capability under `carried/`;
- target-repo skill.

That distinction matters. Some material should travel with Compass because it is
useful portable capability, but it should not load into every session. The
installed authoring skill now teaches that route directly instead of forcing
material into the wrong surface.

- Completed by the carried skill-authoring PR. Codex and Claude
  `write-a-skill` now teach the carried-but-not-global route.

### Stacked Diff Checks Use The Actual Base

Both `write-a-skill` versions now tell agents to run:

- `git diff --check`;
- diff checks against the actual PR base for stacked branches instead of
  assuming `origin/main`.

That keeps Compass stack work from dragging unrelated upstream stack changes
into the validation target.

- Completed by the carried skill-authoring PR. Codex and Claude
  `write-a-skill` now use actual-base wording for stacked branches.

## Decisions

- Keep all four audited Codex skills installed.
- Keep `grill-me`, `to-prd`, and `write-a-skill` mirrored for Claude.
- Keep `update-compass` Codex-only.
- Do not prune `grill-me`, `to-prd`, or `update-compass` now.
- Keep `write-a-skill` global and mirrored. The carried-route placement and
  stacked-branch validation wording are complete.

## Completed PR Boundary

Completed runtime PR:

- changed `codex/skills/write-a-skill/SKILL.md`;
- changed `claude/skills/write-a-skill/SKILL.md`;
- added the carried-but-not-global route;
- replaced the `origin/main` diff-check assumption with actual-base wording;
- ran skill validation and `doctor.ps1`.

## Verification

Commands used while refreshing this audit:

```powershell
(Get-Content codex\skills\grill-me\SKILL.md).Count
(Get-Content claude\skills\grill-me\SKILL.md).Count
(Get-Content codex\skills\to-prd\SKILL.md).Count
(Get-Content claude\skills\to-prd\SKILL.md).Count
(Get-Content codex\skills\update-compass\SKILL.md).Count
(Get-Content codex\skills\write-a-skill\SKILL.md).Count
(Get-Content claude\skills\write-a-skill\SKILL.md).Count
rg -n "carried|target-repo|global|origin/main|actual PR base|git diff --check|codex/skills|claude/skills|agents/openai.yaml" codex\skills\write-a-skill\SKILL.md claude\skills\write-a-skill\SKILL.md
Select-String -Path manifests\portable-files.toml -Pattern "grill-me|to-prd|update-compass|write-a-skill|derived_skills"
```
