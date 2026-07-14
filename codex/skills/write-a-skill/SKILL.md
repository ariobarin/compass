---
name: write-a-skill
description: Create or revise a Compass skill and its install wiring. Invoke manually for skill work.
---

# Write A Skill

Use this skill as the Compass overlay for creating or revising reusable skills.

## Choose The Right Surface

- reusable global agent capability: `codex/skills/`;
- carried but not global pack: `carried/`;
- project-specific capability: the target repository's skill folder;
- skeptical or independent reviewer persona: `codex/agents/`;
- deterministic or fragile mechanic: `scripts/`;
- repo-maintainer process: `workflows/`;
- portability boundary: `manifests/`;
- repo-only lesson: `local-docs/`.

Do not promote a project-specific pack into global context without repeated
cross-repository evidence.

## Author The Skill

A normal skill contains:

```text
skill-name/
  SKILL.md
  references/
  scripts/
  assets/
```

Use only needed folders. Frontmatter contains `name` and `description`. The
description states capability and trigger in no more than 160 characters.

Front-load role, non-negotiables, failure mode, and next decision. Keep
`SKILL.md` lean. Put detailed reference material one level under `references/`,
deterministic mechanics under `scripts/`, and output resources under `assets/`.

Do not add auxiliary README, changelog, quick-reference, or installation files
inside an installed skill.

## Install Wiring

For a global skill, update together:

1. `codex/skills/<name>/`;
2. `[agents].skills` in `manifests/portable-files.toml`;
3. `[claude].derived_skills` when Claude should derive it;
4. `manifests/skill-sources.json`;
5. policy or required-file checks that bind to the skill.

For a carried pack, create the real `carried/` path, keep it out of installed
skill lists, and document the opt-in route. For a project-local skill, edit the
target repository instead.

## Validate

Run:

```powershell
.\scripts\doctor.ps1
git diff --check origin/main...HEAD
```

Run added scripts and tests directly. Forward-test fragile judgment with a fresh
agent and realistic task. Before review, check for duplicated skills, stale
triggers, missing references, forgotten manifests, and mechanics that should
move to scripts.
