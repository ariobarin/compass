---
name: compass
description: Maintain Compass source, install boundaries, and validation. Invoke manually for Compass repository changes.
---

# Compass

Use this skill only when changing Compass itself.

## Boundaries

- Reviewed source lives in this repository, not in live config homes.
- Installed agent behavior belongs under `codex/`.
- Repo-maintainer process belongs under `workflows/`, `local-docs/`,
  `manifests/`, and `scripts/`.
- Carried opt-in packs belong under `carried/` and stay out of global manifests.
- Claude surfaces derive from Codex sources where the manifest says so.
- Deterministic mechanics belong in scripts; reviewer personas belong in agents.

## Read First

Read root `AGENTS.md`, `local-docs/maintenance-learnings.md`,
`workflows/addition-intake.md`, and the workflow nearest the change.

## Change Exactly

Update source, install maps, policy contracts, required-file checks, and tests in
the same branch when ownership changes. Do not add fallback guidance for a
capability Compass can make exact.

## Validate

Run `.\scripts\doctor.ps1`, narrow script tests, and `git diff --check`. Use
`.\scripts\verify-live.ps1 -SkipCodexCommand` only when live drift matters. Use a
PR as the review unit.
