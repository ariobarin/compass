---
name: write-a-skill
description: Create, revise, prune, or retire an agent skill. Use when a recurring capability or behavior needs selective triggering, high-signal guidance, reusable resources, composition with other Compass skills, or proof on realistic work.
---

# Write A Skill

Design the state of mind the skill should put the agent into. A skill is not a
container for everything known about the task.

## Grok

- Name the capability, the recurring failure, and the decision the skill must
  change. A useful one-off does not automatically deserve a skill.
- Read neighboring Compass skills. Preserve their ownership boundaries.
- Use `$ground-in-sources` to inherit hard-won doctrine before writing durable
  guidance.

## Write

- Make the frontmatter description selective: say what the skill does and the
  concrete situations that should trigger it.
- Draft only a single-screen core: the decisive lens and the few strongest
  principles that transfer judgment. Add no sections for completeness or
  imagined edge cases. A skill steers; it is not a handbook.
- Write the philosophy, not the domain checklist. The model already knows the
  routine cases. Keep only surprising distinctions, hard-won failure modes, and
  decision rules it is likely to miss.
- Delete inventories of steps, surfaces, outputs, and concerns. Keep an item
  only when omitting it caused a real behavioral failure.
- Do not transplant research into `SKILL.md`. Extract only what changes a
  decision. Put provenance in `references/sources.md` and keep it out of normal
  execution. Leave target-specific facts to source grounding at use time.
- Treat Compass as one installed system. Call sibling skills by exact name.
  Never duplicate their guidance or hedge that they may be unavailable.
- Add references, scripts, or assets only when they carry depth or mechanics
  that the core skill should not repeat.

## Prove And Prune

Challenge the core on realistic work. Observe what the agent selects, decides,
and produces. When a failure exposes missing judgment, add the smallest causal
instruction and run it again. Never expand against an imagined failure.

Make the pull request carry the challenge and observed result so reviewers can
judge the behavioral claim.

Fix the causal language, then delete every line that merely makes the skill more
complete. Run the structural validator and the repository's current checks.

Source provenance lives in [references/sources.md](references/sources.md). Do not
load it during normal skill authoring.
