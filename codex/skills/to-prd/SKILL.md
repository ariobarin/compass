---
name: to-prd
description: Draft PRDs from current context without publishing by default. Use when user asks to create or refine a PRD from existing context.
---

# To PRD

Use this skill to turn already-available conversation, codebase, and product
context into a product requirements document. The role is synthesis: preserve
the user's intent, separate decisions from assumptions, and make the next
implementation conversation easier to review.

The failure mode this prevents is premature project tracking. A useful PRD can
exist as a local draft, chat artifact, or issue body. Do not create, update,
label, or publish anything in an external tracker unless the user explicitly
asks for publication and provides the target tracker, repository or project,
and label policy.

## Drafting Stance

- Start from current context and nearby repo evidence.
- Ask only for missing decisions that block a coherent PRD.
- Mark inferred decisions as assumptions when the user did not confirm them.
- Prefer domain vocabulary from the project over generic feature language.
- Keep implementation details stable enough to survive code movement.

## Process

1. Read relevant project guidance, ADRs, glossary docs, and nearby code when
   they are available.
2. Identify the problem, intended users, proposed solution, explicit
   decisions, assumptions, out-of-scope work, and verification seams.
3. Draft the PRD using the template below.
4. If publication was explicitly requested, restate the target tracker,
   target project, labels, and final remote action before publishing.

<prd-template>

## Problem Statement

Describe the user's problem from the user's perspective.

## Solution

Describe the proposed solution from the user's perspective.

## User Stories

List user stories in this format:

1. As an <actor>, I want <feature>, so that <benefit>.

Cover the main actor paths, edge cases, and administrative or operational
needs that matter for implementation.

## Implementation Decisions

List decisions that are already made or strongly implied, including:

- modules or systems involved;
- API, schema, or interface contracts;
- architectural decisions;
- user interactions;
- technical clarifications from the user.

Avoid specific file paths unless the path itself is part of the requirement.
If a prototype produced a compact snippet that captures a decision more clearly
than prose, include only the decision-bearing part and label it as prototype
derived.

## Testing Decisions

List the expected testing seams and prior art, including:

- what user-visible behavior must be tested;
- which existing test style or layer should be reused;
- which edge cases need coverage;
- which manual or runtime checks remain useful.

## Assumptions

List assumptions that should be confirmed before implementation.

## Out of Scope

List work that should not be included in the first implementation.

## Further Notes

Add any remaining context that would help an implementer or reviewer.

</prd-template>
