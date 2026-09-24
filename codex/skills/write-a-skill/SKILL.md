---
name: write-a-skill
description: Create, revise, prune, or retire an agent skill. Use when a recurring capability or behavior needs selective triggering, high-signal guidance, reusable resources, composition with other Compass skills, or proof on realistic work.
---

# Write A Skill

Design the state of mind the skill should put the agent into. A skill is not a
container for everything known about the task.

## Grok

- Name the capability, the recurring current-model failure, and the exact
  decision the skill must change. Reproduce that default failure on realistic
  work before drafting. If there is no demonstrated gap, do not create a skill.
- Read neighboring Compass skills. Preserve their ownership boundaries.
- Use `$ground-in-sources` to inherit hard-won doctrine before writing durable
  guidance.
- When adapting a proven external skill, start from the actual upstream
  artifact. Preserve working language until evidence earns a change. Never
  rewrite merely to make the result original or Compass-shaped.

## Write

- Make the frontmatter description selective: say what the skill does and the
  concrete situations that should trigger it.
- Draft only a single-screen core: the decisive lens and the few strongest
  principles that transfer judgment. Add no sections for completeness or
  imagined edge cases. A skill steers; it is not a handbook.
- Write the philosophy, not the domain checklist. The model already knows the
  routine cases. Keep only surprising distinctions, hard-won failure modes, and
  decision rules it is likely to miss.
- Run the no-op test sentence by sentence: would the current model behave
  differently without this line? If not, delete it. Prefer a strong existing
  concept that recruits the right judgment over a paragraph of weak reminders.
- Delete inventories of steps, surfaces, outputs, and concerns. Keep an item
  only when omitting it caused a real behavioral failure.
- When a phase is vulnerable to premature completion, give it an observable
  completion criterion. Do not let later steps pull the agent past an unproven
  result.
- Do not transplant research into `SKILL.md`. Extract only what changes a
  decision. Put provenance in `references/sources.md` and keep it out of normal
  execution. Leave target-specific facts to source grounding at use time.
- Treat Compass as one installed system. Call sibling skills by exact name.
  Never duplicate their guidance or hedge that they may be unavailable.
- Add references, scripts, or assets only when they carry depth or mechanics
  that the core skill should not repeat.

## Prove And Prune

Challenge the core on blind, realistic work. Run an organic prompt against the
current model without the candidate first, then against the candidate under the
same conditions. Do not tell the candidate what behavior is being measured.
Judge what it actually decides and produces, not what it claims to have applied.

Make the pull request carry the challenge and observed result so reviewers can
judge the behavioral claim.

Test the description as prompt code too. Matching tasks must trigger the skill;
nearby tasks that do not need the correction must stay out.

Change one causal thing at a time. When a real failure exposes missing judgment,
add the smallest instruction that blocks it and run again. When a line does not
move behavior, delete it. Fix causal language before adding coverage. Run the
structural validator and the repository's current checks.

Source provenance lives in [references/sources.md](references/sources.md). Do not
load it during normal skill authoring.
