# Compass Review Program

Use this workflow to audit Compass runtime guidance, agents, skills, hooks,
maintainer documentation, carried packs, manifests, scripts, reviewed config,
and install behavior.

Review one coherent surface family at a time. Understand first. Reduce recurring
cost without weakening capability.

## Purpose

Compass is configuration for agent judgment. A fresh runtime begins without the
user's lived context or implicit taste. The reviewed source must establish the
right direction quickly, preserve it across finite contexts, and make drift
visible.

Review asks:

- who reads this surface;
- what state the reader is in;
- what behavior the surface must create;
- what evidence proves that behavior;
- what authority belongs here;
- what material can move, merge, mechanize, or disappear.

## Inventory The Current System

Classify each item:

- Codex runtime global: `codex/AGENTS.md`;
- Claude runtime global: `claude/CLAUDE.md`;
- shared installed runtime capability: `codex/agents/` or `codex/skills/` with an
  explicit Claude derivation decision;
- Claude-specific runtime capability: `claude/agents/`;
- carried capability: `carried/`;
- maintainer context: root `AGENTS.md`, `workflows/`, or `local-docs/`;
- mechanical truth: `scripts/`, `manifests/`, hooks, and reviewed config;
- stale or removal candidate.

Record only what changes a decision:

```text
Path:
Audience:
Purpose:
Desired behavior:
Must preserve:
Recurring cost:
Overlap or stale route:
Reduction move or net-new justification:
Evidence to inspect:
Verification:
```

## Review Runtime Guidance

Runtime guidance should establish a direction before procedure. The first screen
should reveal:

- role;
- desired result;
- reason the role exists;
- evidence standard;
- authority boundary.

Prefer desired-state-first language. Keep prohibitions when the forbidden shape
is crisp, observable, and materially safer. Replace soft modal language around
required behavior with calm direct instruction.

Move dated observations, author history, packaging rationale, and maintainer
debates out of runtime context. Keep exact procedures only where order protects
a fragile mechanic, public mutation, isolation boundary, or handoff contract.

For long-running guidance, verify that:

- one logical principal authors control documents across contexts;
- delegates receive reviewed assignments and return evidence;
- compaction and restart can resume from anchors plus a checkpoint;
- current route never replaces the stable goal;
- planning authority is explicit before production mutation.

## Review Model Routing

Compare every role file with `local-docs/model-calibration.md` and current
runtime support.

For the current profile:

- Sol owns the Codex principal and work that justifies frontier capacity;
- Luna is the default Codex delegated route;
- Terra has no default coding role;
- Claude delegates use the configured GLM-5.2 route;
- effort matches the persistence and verification needed by the assignment;
- mechanical waits use `monitor-to-completion` rather than a model loop.

Treat this as dated policy. Update the calibration and runtime files together
when evidence changes.

## Review Skills And Agents

Every installed capability pays retrieval and maintenance cost. Ask:

- Is the behavior reusable across repositories?
- Does ordinary runtime work benefit from retrieving it?
- Is its description specific enough for natural invocation?
- Does it shape judgment rather than prescribe every thought?
- Does it overlap another role or merely compose with it?
- Would a carried or project-local route preserve value at lower global cost?
- Does the Claude derivation remain truthful?
- Do install maps, source records, retirements, policy checks, and MCP catalogs
  agree?

Useful specialized material moves to `carried/` before its global copy retires.

## Review Control And Ledger Surfaces

Control documents preserve one principal intention. Verify:

- principal-only authorship of goal, plan, catalog, assignments, and checkpoint;
- evidence provenance for delegated returns;
- absolute timestamps with time zones;
- compact mutable state rather than narrative history;
- optimistic revision protection for mechanical ledgers;
- recovery that requires changed evidence before another equivalent attempt;
- a fresh-context resume path.

A ledger supports the work. It never becomes the product.

## Review Hooks And Mechanics

Hooks and scripts enforce exact properties. Ask:

- what event or command invokes the mechanic;
- what it permits, adds, denies, or validates;
- whether failure behavior matches the risk;
- which test proves the reviewed copy works;
- whether broad judgment has leaked into code;
- whether prose describes a property that should be mechanized.

## Reduction Standard

Good reduction removes:

- duplicate doctrine;
- distributed state and alternate sources of truth;
- audience mismatch;
- project lore from global context;
- model routes preserved by habit;
- soft wording that weakens required behavior;
- lists that replace judgment without protecting a fragile operation;
- wrappers, branches, fallbacks, and compatibility paths made obsolete by the
  accepted design.

Measure maintained surface, concepts, states, dependencies, and sources of truth.
Raw line count is supporting evidence, not the target.

## Review And Verification

Use a focused PR as the review unit. Record:

- surface and audience;
- behavior preserved or changed;
- files moved, merged, added, retired, or mechanized;
- recurring cost reduced;
- verification performed;
- remaining risk or dated assumption.

Run the narrow checks, then the repository doctor and install round trip when the
changed surface affects portability. Forward-test judgment changes with a fresh
agent. Inspect current-head checks, reviews, inline threads, and behavior proof
before calling the PR ready.

A green build is evidence. Readiness still requires the current review contract.
Public mutation still requires authority.

## Taste Boundary

Bring the user a prepared decision when a change alters Compass philosophy,
removes a valued capability, materially narrows ordinary behavior, or chooses
between plausible value systems. Apply routine stale-guidance repair and exact
mechanical reconciliation without turning every cleanup into a taste question.
