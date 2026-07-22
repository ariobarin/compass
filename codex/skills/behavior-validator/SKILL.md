---
name: behavior-validator
description: Prepare and delegate fresh source-blind validation of an observable behavior contract.
---

# Behavior Validator

Create a clean boundary between implementation knowledge and observable product
judgment. This skill exists because source, tests, diffs, and confident review
claims can teach a validator what it is expected to see before it tests the real
surface.

The terminal result is clause-level evidence from a fresh validator that had
only the approved contract, fixtures, target access, and observable surfaces.

The skill owns contract preparation, workspace isolation, and acceptance of the
returned report. The dedicated `behavior-validator` agent owns read-only testing.

## Establish The Observable Contract

Capture success before implementation detail can redefine it. Use
[contract-template.md](references/contract-template.md) to name:

- exact target identity and launch or connection instructions;
- user posture and permissions;
- observable clauses with pass evidence;
- exact synthetic fixture paths, schemas, and environment preparation;
- approved credential route and source precedence;
- negative, boundary, persistence, and anti-cheat probes;
- destructive-action and cleanup authority;
- blocked and out-of-scope conditions.

Write clauses as externally testable states. Keep source paths, internal
mechanisms, tests, diffs, review conclusions, and desired verdicts outside the
contract.

## Build The Isolated Workspace

Run the bundled packager from the implementation repository:

```powershell
python .\codex\skills\behavior-validator\scripts\prepare-workspace.py `
  --source-root <repo-root> `
  --contract <repo-relative-contract> `
  --output <fresh-path-outside-repo> `
  --fixture <approved-repo-relative-fixture>
```

The output path is new and outside the source tree. The packager copies the
contract, runtime-specific local isolation instructions, and only explicitly
approved fixtures. It rejects source-control material, symlinks, sensitive path
shapes, and high-confidence secret content. `workspace-manifest.json` records
hashes and the complete allowed local path set.

## Delegate Fresh

Launch a fresh non-forked `behavior-validator` agent in the prepared workspace.
Pass only:

- workspace path;
- exact observable target identity and access;
- credentials through approved secret handling;
- report destination, when needed.

Implementation conversation, source-aware summaries, review bundles, and parent
context remain outside the validator. Exposure to implementation material marks
the run contaminated and requires a fresh workspace plus fresh validator.

## Accept Evidence

Read [report-schema.md](references/report-schema.md) when consuming the return.
Require:

- target and tested build identity;
- source-blind and contamination status;
- pass, fail, blocked, or out-of-scope status for every clause;
- exact actions and observations;
- negative, boundary, and anti-cheat results;
- evidence locators and remaining proof gaps.

The implementation owner repairs failures. Every repaired build receives a new
source-blind run before the behavior gate closes.
