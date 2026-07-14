---
name: to-prd
description: Draft decision-bearing product requirements from current context without publishing by default.
---

# To PRD

Use this skill to turn available product, conversation, and repository context
into an implementation-ready requirements document. The PRD should carry
decisions, outcomes, evidence, risks, dependencies, and unresolved choices. It
should not be a filled template for its own sake.

Do not create or update an external tracker unless the user explicitly requests
publication and names the target, project, and label policy.

## Build From Evidence

Read relevant guidance, ADRs, glossary material, existing behavior, and nearby
interfaces. Separate:

- confirmed decisions;
- evidence-backed inferences;
- assumptions that need confirmation;
- unresolved decisions that affect scope or implementation.

Use project vocabulary. Avoid fragile file paths unless the path itself is a
requirement.

## Required Content

Every PRD should make these clear, using only sections that carry useful content:

### Outcome

Describe the user or operator state that should exist when the work is complete.

### Success Evidence

Name observable acceptance evidence: behavior, metrics, artifacts, runtime
checks, or user outcomes. Avoid vague "works as expected" language.

### Users And Scenarios

Identify primary actors, important flows, edge cases, and operational needs.
User stories are optional. Use them only when they clarify behavior.

### Scope And Non-Goals

State what the first delivery includes and excludes.

### Decisions And Constraints

Record product, architecture, API, schema, interaction, compatibility, security,
budget, or policy decisions already made.

### Dependencies

Name systems, teams, data, migrations, permissions, sequencing, or external
conditions required for delivery.

### Risks And Mitigations

Cover credible product, technical, rollout, evidence, and operational risks.
Pair each material risk with prevention, detection, or fallback.

### Unresolved Decisions

List only choices that materially change outcome, scope, interface, or risk.
For each, name the decision owner and impact of delay.

### Delivery And Validation

Describe sequencing, rollout, testing seams, prior art to reuse, and remaining
manual or runtime proof.

## Avoid Template Theater

- Omit empty sections.
- Do not invent personas, metrics, deadlines, or implementation decisions.
- Do not duplicate the same requirement as prose, story, and checklist.
- Prefer one precise acceptance statement over several aspirational bullets.
- Mark prototype-derived decisions and include only the decision-bearing part.
- Keep historical discussion out unless it changes a current decision.

## Publication Boundary

When publication is requested, restate the exact destination and remote action
before writing. Otherwise return a local or chat draft only.
