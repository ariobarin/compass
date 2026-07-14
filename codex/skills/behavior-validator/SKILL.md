---
name: behavior-validator
description: Prepare and delegate source-blind validation of observable behavior contracts.
---

# Behavior Validator

Use this skill to create the validation boundary and delegate the actual judgment
to the dedicated `behavior-validator` agent. The skill owns contract preparation
and isolation. The agent owns read-only observable testing.

## Contract First

Capture the behavior contract before implementation detail can redefine success.
Use [contract-template.md](references/contract-template.md) for:

- exact target identity and launch or connection instructions;
- observable clauses with pass evidence;
- allowed fixtures and approved credential handling;
- destructive-action limits and cleanup;
- negative, boundary, and anti-cheat probes;
- blocked and out-of-scope rules.

Do not put source paths, implementation notes, tests, diffs, review conclusions,
or expected internal mechanisms in the contract.

## Build The Isolated Workspace

Run the bundled packager from the implementation repository:

```powershell
python .\codex\skills\behavior-validator\scripts\prepare-workspace.py `
  --source-root <repo-root> `
  --contract <repo-relative-contract> `
  --output <fresh-path-outside-repo> `
  --fixture <approved-repo-relative-fixture>
```

The output path must be new and outside the source tree. The script copies only
`contract.md` and explicitly named fixtures, rejects source-control and
credential-like material, and writes `workspace-manifest.json` with hashes.

## Delegate Fresh

Launch a fresh non-forked `behavior-validator` agent with its working directory
set to the prepared workspace. Pass only:

- the workspace path;
- observable target access;
- credentials through approved secret handling;
- the requested report destination, if any.

Do not pass the implementation conversation, source-aware summaries, review
bundles, or a forked context. If implementation material becomes visible, discard
the result and rebuild a fresh workspace for a fresh agent.

## Accept Evidence

Read [report-schema.md](references/report-schema.md) when checking the return.
Require clause-level pass, fail, blocked, or out-of-scope status, exact observed
evidence, anti-cheat probes, target identity, and contamination status. The
implementation owner may repair failures, but each repaired build needs a fresh
source-blind run.
