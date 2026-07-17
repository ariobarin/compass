# Compass Revision, 2026-07-17

This revision turns the July 2026 skill review and design discussion into one
coherent Compass source tree. It preserves the capabilities that proved useful,
reduces repeated control doctrine, separates runtime-specific truth, and makes
long-running work resumable without treating conversation history as authority.

## Governing Decisions

- One logical user-facing principal owns the objective across finite contexts.
- The user or principal authors goals, plans, catalogs, assignments,
  checkpoints, and ledger structure.
- Delegates execute reviewed assignments and return artifacts plus evidence.
  They do not create parallel control state.
- Compaction, restart, and principal replacement are lossy handoffs. A fresh
  context reopens named anchors and verifies current state before continuing.
- Guidance leads with the desired role, state, and evidence. Prohibitions remain
  for crisp boundaries and unmistakable recurring failure shapes.
- Skills shape judgment before procedure. Exact steps protect fragile mechanics,
  authority boundaries, and handoff contracts.
- Planning-only authority permits inspection, research, planning, and scoped
  experiments. Production implementation begins after the named authority opens
  that phase.

## Runtime Sources And Routing

- `codex/AGENTS.md` and `claude/CLAUDE.md` are separately authored global
  sources.
- Codex uses Sol for the user-facing principal and Luna for fresh delegated work.
  Terra has no default role in the current coding profile.
- Claude Code treats GLM-5.2 as the only available delegated model identity in
  the current installation.
- `apps/compass-mcp/profile.md` gives the ChatGPT MCP surface its own
  runtime-neutral profile instead of importing Codex-specific routing.
- A new `progress-monitor` agent handles narrow judgment-based observation.
  `monitor-to-completion` remains the route for pure waiting.

## Skill Set Changes

Added globally:

- `run-a-micro-experiment`;
- `using-goals`;
- `write-a-compass-skill`;
- a general, runtime-oriented `write-a-skill`.

Moved out of global installation:

- `benchmark-run-operator` now lives in `carried/benchmark/` with its specialist
  reviewer sources.

Retired from global installation:

- `input-token-economy`; its useful behavior now lives in context architecture,
  monitoring, assignment, and continuity guidance.
- `using-codex-goals`; replaced by runtime-neutral `using-goals`.

Reshaped:

- `grill-me` maps and ranks the full question space before asking one question at
  a time.
- `orchestration-controller` owns principal control, reviewed assignments,
  evidence reconciliation, and drift correction.
- `subagent-driven-development` owns bounded implementation delegation under an
  already approved plan.
- `root-cause-not-symptom` supports multiple interacting causes and requires a
  subtractive review after repair.
- `action-items-to-prs` owns source-ledger creation and PR grouping rather than
  duplicating the full review loop.
- `behavior-validator` has a stronger source-blind workspace boundary and report
  contract.
- `workspace-steward` distinguishes production worktrees, integration spikes,
  disposable micro-experiments, control documents, evidence, scratch, and
  archives.

The frontend design skill, branch resolver, specialist review, PRD, update, and
other proven focused skills remain present.

## Durable Work Surfaces

Added or expanded:

- `glossary.md`;
- `workflows/long-running-work.md`;
- principal-authored goal, catalog, assignment, and checkpoint templates;
- schema version 4 of the local orchestration ledger;
- a richer copyable workspace with separate Codex and Claude guidance,
  lifecycle READMEs, control-document templates, timestamps, micro-experiment
  rules, PR worktrees, and integration spikes.

The orchestration ledger is now a compact mechanical index. It links to reviewed
Markdown control documents, records phase and current routing, stores
principal-verified evidence with provenance and timestamps, and enforces one
logical principal through optimistic revisions. Delegated edit grants were
removed.

## Isolation And Safety

The behavior-validator packager now:

- rejects source-control material, symlink traversal, sensitive names and path
  segments, credential-like file types, and common secret content patterns;
- scans the contract and fixtures;
- normalizes fixture destinations without duplicate `fixtures/fixtures` paths;
- writes both Codex and Claude local instruction files;
- records exact allowed local paths and content hashes in schema version 2 of the
  workspace manifest.

The validator reports target identity, tested time, manifest hash, allowed-path
verification, clause-level observations, anti-cheat probes, contamination, and
remaining proof gaps.

## Installation And Retirement

The portable manifest, source catalog, installers, Claude derivation, doctor
checks, MCP catalog, and install round-trip expectations were updated together.
Explicit retirement paths remove prior global copies of:

- `benchmark-run-operator`;
- `input-token-economy`;
- `using-codex-goals`;
- `benchmark-infra-reviewer.md` from the Claude agent home.

Carried benchmark resources remain in the repository for explicit project
adoption.

## Validation

The final archive is validated through repository Python tests, direct manifest
and policy validators, JSON and TOML parsing, Markdown-link inspection, text and
line-ending checks, Python compilation, MCP TypeScript build, local MCP smoke,
Cloudflare Worker catalog generation and smoke, Git diff checks, archive content
inspection, and a clean extraction test.

PowerShell is not installed in the packaging environment. The Windows doctor and
install round-trip scripts were updated and are wired into GitHub Actions, but
they could not be executed locally while producing this archive.
