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
- `write-a-skill`: 178 Codex lines, 166 Claude lines.

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
boundaries. The length is justified, but two issues should be corrected.

### Teach The Carried Route

`write-a-skill` still frames placement mostly as a binary choice:

- global Compass skill;
- target-repo skill.

Compass now has a third route: carried but not global.

That distinction matters. Some material should travel with Compass because it
is useful portable capability, but it should not load into every session. If
`write-a-skill` does not teach that route, future agents will keep forcing
material into the wrong surface.

Follow-up PR: update Codex and Claude `write-a-skill` so new skill work chooses
among:

- globally installed runtime skill;
- carried but not global capability under `carried/`;
- target-repo skill.

### Stop Assuming `origin/main` For Stacked Diff Checks

Both `write-a-skill` versions tell agents to run:

`git diff --check origin/main...HEAD`

That is too specific for Compass stack work. Much of the current review program
is intentionally stacked on earlier PR branches. Checking against `origin/main`
can include unrelated upstream stack changes and make the validation target
muddy.

Follow-up PR: keep whitespace validation, but say to use the actual PR base
when checking a stacked branch, and use plain `git diff --check` for the working
tree.

## Decisions

- Keep all four audited Codex skills installed.
- Keep `grill-me`, `to-prd`, and `write-a-skill` mirrored for Claude.
- Keep `update-compass` Codex-only.
- Do not prune `grill-me`, `to-prd`, or `update-compass` now.
- Update `write-a-skill` in a separate runtime PR for carried-route placement
  and stacked-branch validation wording.

## Next PR Boundary

Make one focused runtime PR:

- edit `codex/skills/write-a-skill/SKILL.md`;
- edit `claude/skills/write-a-skill/SKILL.md`;
- add the carried-but-not-global route;
- replace the `origin/main` diff-check assumption with actual-base wording;
- run skill validation and `doctor.ps1`.
