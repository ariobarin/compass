# Addition Intake Workflow

Use this workflow to decide whether a new Compass rule, workflow, skill, agent,
hook, script, manifest entry, config fragment, or carried pack deserves a durable
place in the repository.

Compass is an allowlist. Every addition must earn its recurring context,
retrieval, install, validation, and maintenance cost.

## Start With The Reduction Case

State the repeated problem and the cost the addition removes or prevents:

- recurring context or explanation;
- duplicate sources or decisions;
- generated state mistaken for reviewed source;
- drift that should become mechanically detectable;
- repeated judgment that needs a durable stance;
- a distinct capability worth its continuing cost.

Name what the addition replaces, narrows, derives, mechanizes, or makes
obsolete. When it creates net-new behavior, say why that behavior belongs in
every intended runtime instead of one project, one experiment, or one machine.

Generated state, auth, sessions, logs, browser profiles, caches, machine paths,
and live trust settings remain local.

## Choose The Narrowest Durable Surface

Route the behavior to the reader that needs it:

- session-wide Codex defaults: `codex/AGENTS.md`;
- session-wide Claude defaults: `claude/CLAUDE.md`;
- reusable runtime judgment: `codex/skills/`;
- reusable reviewer, explorer, monitor, or worker persona: `codex/agents/`;
- Claude-specific agent contract that cannot derive safely: `claude/agents/`;
- project-specific capability: the target project repository;
- useful portable pack outside every global session: `carried/`;
- Compass maintainer process: `workflows/`;
- maintainer reasoning and dated evidence: `local-docs/`;
- deterministic or fragile mechanics: `scripts/`;
- install, portability, schema, and policy truth: `manifests/`;
- stable reviewed Codex configuration: `codex/config.review.toml`.

Codex and Claude share skills and many agents when the runtime contract is truly
portable. Their global instruction files remain separately authored because the
runtimes, models, and delegation surfaces differ.

## Shape Runtime Guidance

Installed guidance points toward a desired state. Front-load:

- the role being adopted;
- the result it should create;
- the repeated failure the role corrects;
- the evidence that proves success;
- the authority boundary that preserves trust.

Use decisive positive direction for judgment. Reserve prohibitions for crisp,
observable boundaries and recurring failure shapes. Put exact procedures only
where sequence protects a fragile operation or handoff contract.

Runtime files carry action. Maintainer history, model calibration, provenance,
and packaging rationale belong in maintainer documentation or references that
normal work does not load.

## Prove The Addition Before Promotion

A durable addition follows this path:

1. Observe a repeated failure or distinct recurring need.
2. Test the smallest candidate behavior in the lowest-risk appropriate surface.
3. Record the reduction case and evidence.
4. Choose the narrowest durable artifact.
5. Remove or update the surface the addition supersedes.
6. Wire the reviewed files into the exact install and derivation maps.
7. Add mechanical checks for properties that should not drift.
8. Forward-test judgment guidance with a fresh realistic agent when behavior is
   the product.
9. Review the complete change as one PR before treating it as accepted.

Imported setup is candidate material, not reviewed source. Preserve only the
portable behavior Compass intentionally adopts.

## Skills And Agents

A global skill or agent must remain useful across repositories and ordinary
workflows. Project lore, benchmark families, and temporary experiments belong
in the target repository or a carried pack.

For an installed skill:

- keep `SKILL.md` lean and put optional depth one level under `references/`;
- put deterministic mechanics under `scripts/`;
- put output resources under `assets/`;
- keep the description concise enough to route invocation correctly;
- list it in `[agents].skills`;
- list it in `[claude].derived_skills` only when the runtime contract is shared;
- add its reviewed source record to `manifests/skill-sources.json`;
- update required-file and policy checks that bind to it.

For a shared agent, maintain the reviewed Codex source and derive Claude only
when the transform preserves its tools, model-independent role, and isolation
contract. Maintain a direct Claude agent when the platform-specific contract is
material.

Model and effort routing should reflect the current dated profile, not inherited
habit. Runtime role files state their effective route where the platform
supports it.

## Retirement Is Part Of The Change

Removing or renaming an installed capability requires explicit retirement for
every live location Compass previously owned:

- legacy Codex-home skill copies;
- user skill-home copies;
- derived Claude skill copies;
- direct or derived agent copies;
- stale manifest, source catalog, doctor, MCP, and documentation references.

Preserve useful specialized material in its authorized carried or project route
before retiring the global copy.

## Memory-Only Material

Treat live memory skills as historical evidence. Promote them only when fresh
examples prove a repeated portable capability. Fold overlapping behavior into
an existing skill, route maintainer lessons to `local-docs/`, and retire stale
experiments instead of converting history directly into global context.

## Stale-Guidance Sweep

Every addition or retirement checks the nearby system:

- root and workflow indexes;
- Codex and Claude global guidance;
- install and derivation maps;
- source provenance;
- retired-path maps;
- required-file and policy checks;
- MCP catalogs and smoke tests;
- copyable workspace guidance;
- model calibration when routing changed.

Fix directly related stale guidance in the same change. The accepted repository
should describe one current route.
