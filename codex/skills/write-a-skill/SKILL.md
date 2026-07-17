---
name: write-a-skill
description: Create or revise a Compass skill and its install wiring. Invoke manually for skill work.
---

# Write A Skill

Use the system Skill Creator for general skill design when it is available. This
skill is the Compass overlay for routing, source layout, install wiring,
retirement, and repository review boundaries. Read the repo-root `AGENTS.md` and
`workflows/addition-intake.md` before editing.

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

For a retirement, remove installed and derived manifest entries, remove the
source catalog record, and add explicit retired paths for every live location
Compass previously owned. Preserve useful project-specific material in its
authorized destination or a documented carried route before removing the global
copy.

## Validate

Run:

```powershell
.\scripts\doctor.ps1
git diff --check origin/main...HEAD
```

Run `.\scripts\verify-live.ps1 -SkipCodexCommand` when install or retirement
drift matters. Run added scripts and tests directly. Forward-test fragile
judgment with a fresh agent and realistic task. Before review, check for
duplicated skills, stale triggers, missing references, forgotten manifests, and
mechanics that should move to scripts. Keep a focused PR draft until current-head
review and required checks are complete.
