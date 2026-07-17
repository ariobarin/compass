---
name: compass
description: Maintain Compass source, runtime boundaries, install wiring, retirement, and validation. Invoke manually for Compass repository changes.
---

# Compass

Maintain Compass as reviewed source for portable Codex and Claude behavior. This
skill exists because a strong runtime change can still fail when source routing,
derivation, retirement, policy, and verification disagree.

Use it only when changing Compass itself.

## Preserve The Source Boundaries

- Codex global guidance belongs in `codex/AGENTS.md`.
- Claude global guidance belongs in `claude/CLAUDE.md`.
- Runtime-neutral shared skills and agents belong under `codex/` and derive only
  where the manifest says so.
- Claude-specific agent contracts belong under `claude/agents/`.
- Portable opt-in domain packs belong under `carried/` and stay out of global
  install lists.
- Compass maintainer reasoning belongs in `workflows/` and `local-docs/`.
- Deterministic truth belongs in scripts, hooks, manifests, schemas, and tests.

Read root `AGENTS.md`, `philosophy.md`, `workflows/addition-intake.md`,
`local-docs/maintenance-learnings.md`, and the workflow nearest the change.

## Change The Whole Ownership Contract

When behavior or ownership moves, update the complete route in one change:

- reviewed source;
- Codex and Claude install or derivation maps;
- source provenance;
- explicit retirement paths;
- policy and required-file checks;
- MCP catalog expectations;
- narrow tests and install round-trip coverage;
- directly related documentation.

Make Compass-owned capability exact. A fallback paragraph is not a substitute
for correct wiring.

## Validate The Result

Run narrow tests first, then:

```powershell
.\scripts\doctor.ps1
.\scripts\verify-live.ps1 -SkipCodexCommand
git diff --check
```

Exercise install and retirement paths when ownership changes. Forward-test
judgment changes with a fresh realistic invocation. Use a focused PR as the
review unit and keep public mutation behind named authority.
