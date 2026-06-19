---
name: write-a-skill
description: Create or revise portable Codex skills with metadata, install wiring, and validation. Use when adding or refreshing a skill in codex-portable.
---

# Write A Skill

Use this skill for the codex-portable maintenance path, not as a replacement
for generic skill-design guidance. The job here is to turn a repeated Codex
workflow into a portable, reviewable skill that fits the current repo
conventions and install surface.

## Decide Whether It Should Be A Skill

Before creating or expanding a skill, check whether the problem is actually:

- a repeated agent capability: skill;
- a repo-local human process: `workflows/`;
- a mechanical check: `scripts/`;
- a portability boundary: `manifests/`;
- a repo-only lesson: `local-docs/`.

Choose a repo-local workflow or script when that surface carries the behavior
more cleanly.

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

For codex-portable skills, the normal installable shape is:

```text
skill-name/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
```

Use only the folders that the skill actually needs. Keep frontmatter to
`name` and `description` only.

## Author The Skill

1. Keep the description specific about both capability and trigger.
2. Keep `SKILL.md` lean. Put detailed workflows, variants, or domain reference
   material in one-level-deep files under `references/`.
3. Keep "when to use" guidance in the description, not in a long trigger
   section in the body.
4. Add `agents/openai.yaml` and keep it aligned with the skill body.
5. Re-open `agents/openai.yaml` after generating it and confirm
   `default_prompt` still names the skill with `$skill-name`.
6. Add scripts only for deterministic repeated work, validation, or fragile
   mechanics.
7. Use portable paths and assumptions by default. Include local-only paths or
   machine-specific assumptions only when the repo intentionally owns that
   boundary.

## Portable Repo Wiring

When the skill should install into a live Codex home, update all of these in
the same branch:

1. `codex/skills/<name>/`
2. `manifests/portable-files.toml`
3. `scripts/common.ps1`

If the skill is intentionally repo-only, keep it out of the install manifest
and explain the boundary in the relevant repo docs instead.

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
installed yet.

## Review Pass

Before calling the PR ready, check for nearby stale patterns:

- duplicated or overlapping skills that should route through one capability;
- false workflow splits in neighboring skills or docs;
- stale `openai.yaml` text after a skill rewrite;
- manifest or installer lists that forgot the new skill;
- references that exist on disk but are not linked from `SKILL.md`.
