# Repository Guidance

Compass is reviewed source for portable Codex and Claude Code behavior. It is
not a raw runtime-home backup.

## Source Boundaries

- `codex/AGENTS.md` is the separately authored Codex global instruction source.
- `claude/CLAUDE.md` is the separately authored Claude global instruction
  source.
- Maintain those two files separately. Share values, not runtime fiction.
- Reusable runtime-neutral skills live under `codex/skills/` and may derive into
  Claude when listed in `manifests/portable-files.toml`.
- Shared agent roles live under `codex/agents/`. Direct Claude agents live under
  `claude/agents/` only when their platform contract cannot be derived.
- Installed hook behavior lives under `codex/hooks.json` and `codex/hooks/`.
- Portable opt-in domain packs live under `carried/` and stay out of global
  install lists.
- Compass-only maintenance belongs in this file, `workflows/`, `local-docs/`,
  `manifests/`, or `scripts/`.
- Project-specific capability belongs in the target project.

Keep `codex/AGENTS.md` and `claude/CLAUDE.md` short and session-wide. Put focused
runtime judgment in the narrowest skill or agent. Put deterministic truth in a
script, hook, manifest, schema, or test.

## Maintenance Posture

Read [philosophy.md](philosophy.md), [glossary.md](glossary.md),
[local-docs/maintenance-learnings.md](local-docs/maintenance-learnings.md), and
the workflow nearest the change before a nontrivial edit.

Understand first. Reduce second. Preserve behavior while reducing repeated
context, duplicate sources, mutable states, weak choices, and maintenance cost.

Lead documentation with the desired role and state. Use a prohibition when the
forbidden boundary is crisp or when a recurring failure has an unmistakable
shape. Pair judgment-heavy prohibitions with the positive replacement.

For long-running work, preserve one logical principal across contexts. The
principal or user authors the goal, plan, catalog, assignments, and checkpoints.
Delegates execute reviewed assignments and return artifacts plus evidence. Do
not distribute control authorship across worker-written ledgers.

Material plans and assignments should be reviewable before dispatch unless the
user has already granted or explicitly waived that review boundary.

## Exact Repository Rules

- Treat every manifest-listed skill and agent as one reviewed portable bundle.
- Fix Compass-owned wiring in source, transforms, manifests, policy contracts,
  and tests. Avoid alternate-path prose where Compass can make the route exact.
- Update source, install maps, retirement maps, required-file checks, policy
  contracts, MCP catalog expectations, and tests together when ownership moves.
- Preserve external provenance and license evidence for imported skills.
- Keep `AGENTS.override.md`, auth, sessions, logs, caches, browser state,
  database files, generated plugin state, and machine-only values untracked.
- Respect `CODEX_HOME`, `-AgentsHome`, and `-ClaudeHome` instead of hardcoding
  default runtime paths.
- Review `codex/config.review.toml` before changing its authority. Install
  overlays reviewed keys and preserves unrelated live keys.
- Use a focused pull request as the review unit.
- Run `git diff --check` and the narrow tests for every changed mechanism.
- Run `.\scripts\doctor.ps1` before committing.
- Run `.\scripts\verify-live.ps1 -SkipCodexCommand` when install or retirement
  drift matters.

## Skill Authoring

Use `write-a-skill` for general skill design and `write-a-compass-skill` for
Compass routing, install, derivation, provenance, retirement, and validation.

A skill should make the reader absorb, in its first screen:

- the role;
- the desired terminal result;
- why the role exists at runtime;
- the recurring failure it corrects;
- the evidence that matters;
- the authority boundary.

Shape judgment before prescribing steps. Use procedures only when order is real
or mechanics are fragile. Keep maintainer history and model anecdotes out of
installed runtime text.

## Review Focus

Flag:

- accidental expansion of the portable boundary;
- project-specific material promoted globally;
- duplicated Codex and Claude global guidance that should remain separate;
- soft language around required behavior;
- negative-only guidance with no desired replacement;
- distributed control authorship in long-running work;
- premature implementation while authority remains in planning;
- worker claims accepted without current evidence;
- model routing that conflicts with the dated current profile;
- stale skill names, install maps, retirement paths, policy strings, or tests;
- generated mechanics expressed only as remembered prose.
