# Compass

Compass is my collection of agent skills and working preferences. It captures
the judgment I want agents to reuse: settle consequential decisions, work
independently, prove the result, and make the next human visit useful.

The collection draws on [Matt Pocock's skills](https://github.com/mattpocock/skills),
[Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack), and
[Theo Browne's workflows](https://www.youtube.com/watch?v=D8PikZ1KhUo&t=2723),
adapted to [my preference for simplicity](philosophy.md). Each adapted skill
records its sources and the decisions behind the adaptation.

## Choose The Skill For The Job

| Need | Skills |
| --- | --- |
| Settle an important decision | [grilling](codex/skills/grilling/SKILL.md), [ground-in-sources](codex/skills/ground-in-sources/SKILL.md) |
| Explore an uncertain idea | [micro-experiment](codex/skills/micro-experiment/SKILL.md), [design-prototype](codex/skills/design-prototype/SKILL.md) |
| Break down and deliver substantial work | [to-tickets](codex/skills/to-tickets/SKILL.md), [implement-spec](codex/skills/implement-spec/SKILL.md) |
| Diagnose and prove behavior | [diagnosing-bugs](codex/skills/diagnosing-bugs/SKILL.md), [test-for-risk](codex/skills/test-for-risk/SKILL.md), [blast-radius](codex/skills/blast-radius/SKILL.md) |
| Make project verification repeatable | [create-verification-skill](codex/skills/create-verification-skill/SKILL.md) |
| Carry work through checks and review | [babysit-pr](codex/skills/babysit-pr/SKILL.md), [monitor](codex/skills/monitor/SKILL.md) |
| Improve the next session | [retro](codex/skills/retro/SKILL.md), [write-a-skill](codex/skills/write-a-skill/SKILL.md), [handoff](codex/skills/handoff/SKILL.md) |
| Refine prose and comments | [unslop](codex/skills/unslop/SKILL.md), [no-comments](codex/skills/no-comments/SKILL.md) |
| Change this collection | [compass](codex/skills/compass/SKILL.md) |

These are tools to select, not stages every task must pass through. A small fix
can go straight to implementation. A larger change might use grilling to
settle its decisions, to-tickets to expose dependencies, implement-spec to
deliver independent slices, and babysit-pr to follow the review.

## Use What Helps

Read a skill and copy its folder into the skill directory your agent uses.
Keep its references and license notices with it. Global preferences are in
[codex/AGENTS.md](codex/AGENTS.md); the optional Codex role is in
[codex/agents](codex/agents/README.md). Review personal preferences before
adopting them.

Compass MCP consumes `codex/AGENTS.md`, `codex/skills/`, and the skill catalog in
`manifests/portable-files.json`. Those paths remain its source interface; the
manifest now only lists skills. Model selection and runtime setup belong to
the environment running the agent.

## Maintain The Collection

Add instructions for an observed gap. Prefer a structural fix when the project
can make the mistake impossible. Remove scaffolding that newer models no
longer need. [Source Grounding](source-grounding.md) explains how evidence
becomes guidance; [Contributing](CONTRIBUTING.md) covers review and validation.

Run the read-only source checks with Python 3.11 or newer:

```sh
python3 scripts/check.py
git diff --check
```
