---
name: write-a-skill
description: Create or revise portable skills with metadata, install wiring, and validation. Use when adding or refreshing a skill in Compass.
---

# Write A Skill

Use this skill as the Compass overlay on the system Skill Creator when it is
available. Follow the same basic model: understand concrete examples, plan
reusable resources, create or edit the skill folder, validate it, and iterate
from real use. This skill adds the Compass source path, install boundary, and
PR checks.

Use Compass only for reusable global skills that should install into the user's
portable skill home. If the capability only makes sense for one project or
repository, keep that skill in the target repo's own skill folder instead of
promoting it here.

## Core Stance

Create or expand a skill only when the repeated work is specialized agent
behavior. Choose a narrower Compass surface when it fits better:

- repeated global agent capability: `codex/skills/`;
- carried but not global capability: `carried/`;
- repo-local human process: `workflows/`;
- mechanical check: `scripts/`;
- portability boundary: `manifests/`;
- repo-only lesson: `local-docs/`.

Use plugins, not Compass user skill folders, when the goal is broader
distribution, a bundle of multiple reusable skills, or a skill shipped with app
integrations or MCP servers.

Skills should shape judgment before they prescribe steps. Front-load the role,
non-negotiables, next action, and failure mode to avoid. Prefer concise
principles, boundaries, examples, and deterministic scripts over exhaustive
branching text.

## Understand The Skill

Collect concrete examples from recent prompts, PR comments, or repeated repair
work. Use those examples to answer:

- what requests should trigger the skill;
- what artifacts the skill should read or produce;
- which steps are core enough for `SKILL.md`;
- which details belong in `references/` or `scripts/`.

If the examples show the same capability under different request posture, keep
one skill and route variants inside it. Group proposal vs existing system, new
vs old project, review vs create, and similar postures when the underlying
capability is the same.

## Plan Reusable Contents

Plan the skill contents the same way the system Skill Creator does:

1. Work through each concrete example from scratch.
2. Identify reusable resources that would avoid repeated re-discovery or
   repeated code generation.
3. Put detailed reference material under `references/`.
4. Put deterministic or fragile repeated mechanics under `scripts/`.
5. Put output resources such as templates or static files under `assets/`.

Keep `SKILL.md` lean. It should carry the core workflow, resource navigation,
and decision rules. It should not carry long reference material that can be
loaded only when needed.

## Use The Compass Shape

For Compass skills, the normal installable shape is:

```text
skill-name/
  SKILL.md
  references/
  scripts/
  assets/
```

Use only the folders that the skill actually needs. Keep frontmatter to
`name` and `description` only.

Treat `codex/skills/` as the reviewed source tree. Author each skill once under
`codex/skills/<name>/`; the install map derives the Claude copy from it, so do
not keep a separate `claude/skills/<name>/` source. Do not assume every project
should use the same layout just because this repo does.

Avoid duplicating a skill name across Compass and a project skill folder.
Runtimes may not merge same-name skills, so duplicates can both appear in
selectors or override each other in ways that change routing.

## Create Or Edit The Skill

For a new skill, initialize a folder under `codex/skills/<skill-name>/`. If
editing an existing skill, read its current `SKILL.md` and linked resources
before changing it.

When authoring:

1. Keep the `name` and `description` metadata present and accurate.
2. Make the description specific about both capability and trigger.
3. Put all "when to use" trigger guidance in the description, not in a long
   trigger section in the body.
4. Keep references one level deep from `SKILL.md` and link every reference from
   the body with clear read conditions.
5. Add scripts only for deterministic repeated work, validation, or fragile
   mechanics, and test added scripts directly.
6. Use portable paths and assumptions by default. Include local-only paths only
   when Compass intentionally owns that boundary.
7. Do not add auxiliary docs such as `README.md`, installation guides, quick
   references, changelogs, or process notes inside the skill folder.

## Portable Repo Wiring

When the skill should install into the user skill home, update all of these in
the same branch:

1. `codex/skills/<name>/`
2. the `[agents].skills` list in `manifests/portable-files.toml` so the skill
   installs for Codex
3. the `[claude].derived_skills` list when the skill should also install for
   Claude, which derives it from the codex source at install time

`scripts/common.ps1` reads the manifest for installed skill names. Change it
only when the install-map logic itself needs to change.

If the skill is intentionally repo-only, keep it out of the install manifest
and explain the boundary in the relevant repo docs instead.

If the skill is carried but not global, keep it under `carried/`, leave it out
of installed manifest lists, and document the opt-in route. Carried source may
use normal `SKILL.md` shape, but its path is what keeps it out of live runtime
context.

When a skill belongs in the target repo rather than in the portable global
setup, do not wire it into `manifests/portable-files.toml` or
`scripts/common.ps1`. Put it under that repository's own skill folder.

Do not pull a project-specific skill into Compass just because you are
editing it from this repo. If the skill mainly exists to serve one repository,
its home should usually be that repository.

When promoting a live-only or branch-only skill, make the repo copy complete:
include the real `SKILL.md`, its skill metadata when the skill carries agent
metadata, and any references, scripts, or assets needed for a normal install.

## Verify Before Opening Or Updating A PR

Run the narrowest checks that prove the skill is well-formed and portable:

- `.\scripts\doctor.ps1` (validates skill frontmatter and manifest wiring)
- `git diff --check origin/main...HEAD`

Run `.\scripts\verify-live.ps1 -SkipCodexCommand` only when live drift matters.
Expected drift is fine for branch-only skills that are not meant to be
installed into the user skill home yet.

## Iterate And Review

Forward-test complex or fragile skills with fresh agents when that is practical.
Pass the skill and a realistic task, not the intended answer or your diagnosis.
Review raw artifacts, diffs, logs, and outputs before trusting the result.

Before calling the PR ready, check for nearby stale patterns:

- duplicated or overlapping skills that should route through one capability;
- false workflow splits in neighboring skills or docs;
- stale description or trigger text after a skill rewrite;
- manifest or installer lists that forgot the new skill;
- references that exist on disk but are not linked from `SKILL.md`.
