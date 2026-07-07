---
name: write-a-skill
description: Create or revise portable Codex skills with metadata, install wiring, and validation. Use when adding or refreshing a skill in Compass.
---

# Write A Skill

Use this skill as the Compass overlay on Skill Creator. Follow the same basic
model as `$skill-creator`: understand concrete examples, plan reusable
resources, create or edit the skill folder, validate it, and iterate from real
use. This skill adds the Compass source path, install boundary, and PR checks.

Use Compass only for reusable global skills that should install into the user's
portable skill home. If the capability only makes sense for one project or
repository, keep that skill in the target repo instead of promoting it here.

## Core Stance

Create or expand a skill only when the repeated work is specialized agent
behavior. Choose a narrower Compass surface when it fits better:

- repeated agent capability: `codex/skills/`;
- repo-local human process: `workflows/`;
- mechanical check: `scripts/`;
- portability boundary: `manifests/`;
- repo-only lesson: `local-docs/`.

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

Plan the skill contents the same way `$skill-creator` does:

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
  agents/openai.yaml
  references/
  scripts/
  assets/
```

Use only the folders that the skill actually needs. Keep frontmatter to
`name` and `description` only.

Treat `codex/skills/` here as the repo's portable source tree for reviewed
global skills. Do not assume that every project should use the same path just
because this repo does.

## Create Or Edit The Skill

For a new skill, initialize the folder with the system Skill Creator helper
when available, targeting Compass instead of the live skill home:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
python (Join-Path $codexHome "skills\.system\skill-creator\scripts\init_skill.py") <skill-name> --path .\codex\skills
```

Add `--resources scripts,references,assets` only for resources the skill
actually needs. If editing an existing skill, read its current `SKILL.md`,
`agents/openai.yaml`, and linked resources before changing it.

When authoring:

1. Keep the `name` and `description` metadata present and accurate.
2. Make the description specific about both capability and trigger.
3. Put all "when to use" trigger guidance in the description, not in a long
   trigger section in the body.
4. Keep references one level deep from `SKILL.md` and link every reference from
   the body with clear read conditions.
5. Add scripts only for deterministic repeated work, validation, or fragile
   mechanics, and test added scripts directly.
6. Keep `agents/openai.yaml` aligned with the skill body. Re-open it after
   generation and confirm `default_prompt` names the skill with `$skill-name`.
7. Use portable paths and assumptions by default. Include local-only paths only
   when Compass intentionally owns that boundary.
8. Do not add auxiliary docs such as `README.md`, installation guides, quick
   references, changelogs, or process notes inside the skill folder.

## Portable Repo Wiring

When the skill should install into the user skill home, update all of these in
the same branch:

1. `codex/skills/<name>/`
2. `manifests/portable-files.toml`
3. the Claude mirror under `claude/skills/<name>/` when the behavior applies to
   both runtimes
4. the `[claude]` section of `manifests/portable-files.toml` when a Claude
   mirror is added

`scripts/common.ps1` reads the manifest for installed skill names. Change it
only when the install-map logic itself needs to change.

If the skill is intentionally repo-only, keep it out of the install manifest
and explain the boundary in the relevant repo docs instead.

When a skill belongs in the target repo rather than in the portable global
setup, do not wire it into `manifests/portable-files.toml` or
`scripts/common.ps1`.

Do not pull a project-specific skill into Compass just because you are
editing it from this repo. If the skill mainly exists to serve one repository,
its home should usually be that repository.

When promoting a live-only or branch-only skill, make the repo copy complete:
include the real `SKILL.md`, `agents/openai.yaml`, and any references or scripts
needed for a normal install.

## Verify Before Opening Or Updating A PR

Run the narrowest checks that prove the skill is well-formed and portable:

- PowerShell: `$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }; python (Join-Path $codexHome "skills\.system\skill-creator\scripts\quick_validate.py") <skill-folder>`
- Bash: `python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" <skill-folder>`
- `.\scripts\doctor.ps1`
- `git diff --check origin/main...HEAD`

Run `.\scripts\verify-live.ps1 -SkipCodexCommand` only when live drift matters.
Expected drift is fine for branch-only skills that are not meant to be
installed into `$HOME/.agents/skills` yet.

## Iterate And Review

Forward-test complex or fragile skills with fresh agents when that is practical.
Pass the skill and a realistic task, not the intended answer or your diagnosis.
Review raw artifacts, diffs, logs, and outputs before trusting the result.

Before calling the PR ready, check for nearby stale patterns:

- duplicated or overlapping skills that should route through one capability;
- false workflow splits in neighboring skills or docs;
- stale `openai.yaml` text after a skill rewrite;
- manifest or installer lists that forgot the new skill;
- references that exist on disk but are not linked from `SKILL.md`.
