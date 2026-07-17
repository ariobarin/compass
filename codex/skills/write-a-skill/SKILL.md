---
name: write-a-skill
description: Create or revise a reusable agent skill that strongly orients judgment, stays lean, and proves its behavior.
---

# Write A Skill

Create a direction vector strong enough to change how a capable model judges new
cases. This skill exists because weak skills become trigger phrases plus
checklists, while bloated skills compete for context and still fail to establish
the role.

The terminal result is a lean reusable skill whose purpose, trigger, stance,
evidence, and authority are clear before its procedure.

## Establish The Role

Front-load what the invoking agent must absorb:

- role;
- desired terminal result;
- why the role exists at runtime;
- recurring failure it corrects;
- evidence that matters;
- authority boundary.

Give only enough explanation of purpose to orient action. Preserve discovery
history, model anecdotes, and maintenance rationale outside the installed skill.

## Point Positively

Lead with the behavior and state to create. Use prohibitions for crisp,
observable boundaries and recurring failure shapes with an unambiguous forbidden
form. Pair a prohibition with the desired replacement when judgment is involved.

Write decisively. Remove hedging, filler politeness, apology, and optional
language around required behavior.

## Teach Judgment Before Procedure

Use principles, boundaries, and compact examples for decisions that vary by
context. Use ordered steps when sequence is real, mechanics are fragile, or a
handoff contract must remain exact.

A skill should help the model handle cases the author did not enumerate. A long
branching flowchart usually means the skill has not yet expressed the underlying
judgment.

## Keep The Runtime Surface Lean

A normal skill may contain:

```text
skill-name/
  SKILL.md
  references/
  scripts/
  assets/
  agents/openai.yaml
```

Use only needed folders.

- `SKILL.md` carries the role and action-critical guidance.
- `references/` carries detail loaded only when needed.
- `scripts/` carries deterministic or fragile mechanics.
- `assets/` carries output resources.
- `agents/openai.yaml` carries Codex discovery metadata when that runtime uses
  it.

Frontmatter contains a kebab-case `name` and a concise capability plus trigger
description. Avoid auxiliary installation notes, changelogs, and duplicate quick
references inside an installed skill.

## Separate Scope Correctly

Choose the narrowest durable surface:

- reusable cross-project judgment: global skill;
- project-specific capability: project skill;
- reviewer persona: agent;
- repeated human maintenance process: workflow;
- deterministic guard: script, hook, manifest, or test;
- portable but opt-in domain pack: carried resource.

A useful one-off does not automatically earn global retrieval cost.

## Prove The Skill

Review the skill as behavior, not prose alone:

- Can the right trigger be distinguished from neighboring skills?
- Does the first screen establish role, result, failure, evidence, and boundary?
- Does the language point toward the desired state?
- Can detailed material move to a reference or mechanic?
- Does any rule make a decision that should remain contextual?
- Does a fresh agent behave differently on a realistic task?
- Can the skill be shortened without losing behavior?

Forward-test fragile judgment with realistic prompts and inspect failure cases.
Revise the cause of weak behavior rather than adding another isolated warning.

## Output

Return the authored skill, resources, trigger rationale, behavior evidence,
known boundaries, and the durable surface that owns its installation.
