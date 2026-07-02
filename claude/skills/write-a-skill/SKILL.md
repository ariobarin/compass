---
name: write-a-skill
description: Create or revise portable skills with metadata, install wiring, and validation. Use when adding or refreshing a skill in Compass.
---

# Write A Skill

Use this skill for the Compass maintenance path, not as a replacement
for generic skill-design guidance. The job here is to turn a repeated agent
workflow into a portable, reviewable skill that fits the current repo
conventions and install surface.

This skill is for reusable global skills that belong in Compass.
If the capability only makes sense for one project or repository, keep that
skill in the target repo instead of promoting it here.

## Decide Whether It Should Be A Skill

Before creating or expanding a skill, check whether the problem is actually:

- a repeated agent capability: skill;
- a repo-local human process: `workflows/`;
- a mechanical check: `scripts/`;
- a portability boundary: `manifests/`;
- a repo-only lesson: `local-docs/`.

Choose a repo-local workflow or script when that surface carries the behavior
more cleanly.

For skill placement, distinguish global from project-local scope:

- reusable cross-repo developer capability: Compass skill;
- codebase-specific workflow, schema, or policy: put the skill in that target
  repo instead of Compass.

## Start From Real Trigger Examples

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

## Preferred Skill Shape

For Compass skills, the normal installable shape is:

```text
skill-name/
  SKILL.md
  references/
  scripts/
```

Use only the folders that the skill actually needs. Keep frontmatter to
`name` and `description` only.

Treat `claude/skills/` here as the repo's portable source tree for reviewed
Claude skills, parallel to `codex/skills/` for Codex. Do not assume that every
project should use the same path just because this repo does.

## Author The Skill

1. Keep the `name` and `description` metadata present and accurate.
2. Keep the description specific about both capability and trigger.
3. Keep `SKILL.md` lean. Put detailed workflows, variants, or domain reference
   material in one-level-deep files under `references/`.
4. Keep "when to use" guidance in the description, not in a long trigger
   section in the body.
5. Add scripts only for deterministic repeated work, validation, or fragile
   mechanics.
6. Use portable paths and assumptions by default. Include local-only paths or
   machine-specific assumptions only when the repo intentionally owns that
   boundary.

## Portable Repo Wiring

When the skill should install into the user skill home, update all of these in
the same branch:

1. `claude/skills/<name>/`
2. `manifests/portable-files.toml`
3. `scripts/common.ps1`

If the skill is intentionally repo-only, keep it out of the install manifest
and explain the boundary in the relevant repo docs instead.

When a skill belongs in the target repo rather than in the portable global
setup, do not wire it into `manifests/portable-files.toml` or
`scripts/common.ps1`.

Do not pull a project-specific skill into Compass just because you are
editing it from this repo. If the skill mainly exists to serve one repository,
its home should usually be that repository.

When promoting a live-only or branch-only skill, make the repo copy complete:
include the real `SKILL.md` and any references or scripts needed for a normal
install.

## Verify Before Opening Or Updating A PR

Run the narrowest checks that prove the skill is well-formed and portable:

- `.\scripts\doctor.ps1` (validates skill frontmatter and manifest wiring)
- `git diff --check origin/main...HEAD`

Run `.\scripts\verify-live.ps1 -SkipCodexCommand` only when live drift matters.
Expected drift is fine for branch-only skills that are not meant to be
installed into `~/.claude/skills` yet.

## Review Pass

Before calling the PR ready, check for nearby stale patterns:

- duplicated or overlapping skills that should route through one capability;
- false workflow splits in neighboring skills or docs;
- stale description or trigger text after a skill rewrite;
- manifest or installer lists that forgot the new skill;
- references that exist on disk but are not linked from `SKILL.md`.
