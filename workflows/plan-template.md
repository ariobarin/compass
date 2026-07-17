# Durable Plan Template

Use this template when a plan must survive review, compaction, delegation, or a
fresh principal context. The user-facing principal, or the user directly,
authors and maintains it.

This is maintainer guidance. It is not installed into runtime homes.

A plan is the current route, not the stable goal. Link the authoritative goal
and update the plan when evidence changes. Keep implementation authority
explicit so planning cannot silently become production mutation.

```markdown
# Plan: <name>

Created at: <ISO 8601 timestamp with timezone>
Last verified at: <ISO 8601 timestamp with timezone>
Principal: <logical principal identity>
Status: draft | reviewed | approved | superseded | complete
Implementation authority: withheld | granted
Authority source: <user statement, issue, workflow, or none>

## Goal Anchor

- Goal document:
- Goal revision:
- Other authoritative sources, in precedence order:

## Desired Result

State what this route is intended to produce. Keep completion meaning in the
goal document rather than rewriting it here.

## Observed State

Record current facts with evidence locators. Separate direct observation from
inference.

## Decisions

Record decisions already made, why they matter, and who had authority.

## Route

Describe the smallest coherent route from observed state to the goal. Use
numbered steps only when order is real. For each material step, name the evidence
it should produce.

## Assignments

List reviewed delegate packets by locator. The principal owns this index;
delegates return artifacts and evidence.

## Verification

- Required checks:
- Runtime or browser evidence:
- Independent review:
- Evidence that closes each goal assertion:

## Risks And Recovery

Name credible failure modes, preservation boundaries, and the smallest
reversible recovery action.

## Open Decisions

List only choices that materially change outcome, scope, interface, authority,
or risk. Include options and a recommendation.

## Next Principal Action

Name the next judgment-bearing action. Put pure waiting in a bounded command or
monitor.
```

Before implementation begins, verify that the plan is reviewed, the goal is
anchored, the mutation boundary is explicit, and a fresh context can understand
the route without the conversation that produced it.
