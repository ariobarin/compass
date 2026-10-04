# Repository Guidance

Compass is Ario's collection of agent skills and working preferences. Its job
is to improve how work gets done: clear decisions, independent execution,
observable results, and fewer unnecessary human handoffs.

## Philosophy

Compass defines durable outcomes and true boundaries. It leaves routine
judgment, execution paths, tool use, and self-checking to current models.

Every Compass instruction must earn its place. Use decisive words that change
behavior. Delete noise.

Add prompts, skills, or agents only for a demonstrated
current-model gap. Re-evaluate them after material model changes, and remove
scaffolding that duplicates or distorts native behavior. Use absolute rules
only for true invariants.

Compass research starts with the official record. For product behavior,
corroborated field reports from matching versions and environments outrank
official posting. Official sources retain authority over contracts and policy.

Read `philosophy.md` for simplicity and `source-grounding.md` for research.

## Boundaries

- `codex/AGENTS.md` holds global user preferences.
- Skills live in `codex/skills/<name>/`. Keep the catalog in
  `manifests/portable-files.json` aligned with those directories.
- Compass MCP reads these paths and `agents.skills` directly. Preserve that
  interface and single-line skill names and descriptions in frontmatter.
- Optional Codex roles live in `codex/agents/`. Put a skill's required
  specialist prompt inside that skill so it can supply the prompt itself.
- Project-specific behavior belongs in the project that uses it.
- Models, runtime settings, and installation choices belong to the environment
  running the agent.
- Auth, sessions, logs, caches, databases, browser state, generated plugin
  state, and machine-only values stay untracked.

Adapt upstream skills deliberately. Preserve attribution and license notices,
record the inspected revision, and explain consequential departures in the
skill's source notes. Keep provenance out of the normal execution path.

Use a focused pull request as the review unit. Run `git diff --check` and
`python3 scripts/check.py` before committing. For behavioral changes, exercise
the decision the skill should improve with a fresh agent and realistic inputs;
include a nearby task where it should stay out of the way. Structural checks
alone do not establish that a skill helps.
