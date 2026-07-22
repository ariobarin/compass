---
name: write-a-compass-skill
description: Add, revise, route, install, validate, or retire a skill inside the Compass reviewed source.
---

# Write A Compass Skill

Maintain a Compass skill as both runtime guidance and reviewed portable source.
This overlay exists because good skill prose is not enough when install maps,
Claude derivation, provenance, retirement, policy contracts, and tests can drift.

Use `write-a-skill` for the skill's role and language. This skill owns Compass
routing and repository integration.

Read root `AGENTS.md`, `workflows/addition-intake.md`, and the workflow nearest
the change before editing.

## Choose The Compass Surface

- reusable global capability: `codex/skills/`;
- portable opt-in domain pack: `carried/`;
- project-specific capability: the target repository;
- skeptical or independent persona: `codex/agents/`;
- deterministic mechanic: `scripts/`, hooks, manifests, or tests;
- Compass maintenance process: `workflows/`;
- repo-only learning: `local-docs/`.

A global addition needs repeated cross-project value or a distinct new behavior
that repays its retrieval and maintenance cost.

## Integrate One Reviewed Source

A global skill update lands together across every owning surface. The canonical
update-together checklist lives in `workflows/addition-intake.md` (skill source,
install lists, provenance record, and binding checks). Add the one
skill-authoring item that workflow does not name:

- MCP catalog fixtures and other tests that depend on the installed set.

Claude derives shared skills from Codex source. Maintain `codex/AGENTS.md` and
`claude/CLAUDE.md` separately because their global runtime context differs.

A carried pack stays out of global install lists and documents its adoption
route. A project skill stays with the project.

## Preserve Provenance

An externally adapted skill records reviewed repository, source path, commit or
immutable ref, license, and deterministic source hash. Keep provenance in a
reference that normal runtime work does not load.

## Retire Completely

A retirement removes the global source catalog and install entries, preserves
useful material in its approved narrower destination, and adds explicit retired
live paths for every location Compass previously owned.

A rename is a retirement plus a new skill. It must clean old Codex, user-skill,
and Claude copies without deleting unrelated personal skills.

## Validate Behavior And Wiring

Run the skill authoring review from `write-a-skill`, then validate Compass:

```powershell
.\scripts\doctor.ps1
.\scripts\verify-live.ps1 -SkipCodexCommand
git diff --check origin/main...HEAD
```

Run added scripts and tests directly. Exercise install and retirement paths when
ownership changes. Forward-test judgment with a fresh realistic invocation.

Before review, inspect duplicate skills, stale triggers, missing references,
forgotten manifests, Claude divergence, retired paths, policy strings, MCP
catalog expectations, and mechanics that belong in scripts.

Use a focused PR as the review unit. A green build is evidence; current-head
review and named authority determine readiness and merge.
