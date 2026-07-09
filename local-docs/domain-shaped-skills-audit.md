# Domain-Shaped Skills Audit

This audit packet covers the domain-shaped skills listed in
`local-docs/compass-surface-inventory.md`. It reviews skills that are strong but
domain-shaped: benchmark operation, benchmark infrastructure review, WebMCP eval
and tool work, and workspace stewardship.

Packet status:

- Refreshed after the workspace-steward Claude derivation landed.
- Use current domain skill sources, manifest state, Claude mirrors, and open PR
  stack state before deriving new work from this packet.
- Treat verification commands as audit history, not current proof.

## Surfaces Reviewed

Codex skills:

- `codex/skills/benchmark-infra-reviewer/SKILL.md`
- `codex/skills/benchmark-infra-reviewer/references/review-checklist.md`
- `codex/skills/benchmark-run-operator/SKILL.md`
- `codex/skills/benchmark-run-operator/references/benchmark-protocol.md`
- `codex/skills/benchmark-run-operator/references/stack-operations.md`
- `codex/skills/benchmark-run-operator/references/artifact-validation.md`
- `codex/skills/benchmark-run-operator/references/report-rebuild.md`
- `codex/skills/webmcp-eval-triage/SKILL.md`
- `codex/skills/webmcp-eval-triage/references/failure-rubric.md`
- `codex/skills/webmcp-eval-triage/references/log-and-artifact-triage.md`
- `codex/skills/webmcp-tool-authoring/SKILL.md`
- `codex/skills/webmcp-tool-authoring/references/authoring-workflows.md`
- `codex/skills/webmcp-tool-authoring/references/tool-shape-contract.md`
- `codex/skills/webmcp-verify-tool/SKILL.md`
- `codex/skills/webmcp-verify-tool/references/live-verification.md`
- `codex/skills/webmcp-verify-tool/references/tool-contract-checklist.md`
- `codex/skills/workspace-steward/SKILL.md`
- `codex/skills/workspace-steward/references/project-template/README.md`

Claude direct mirrors:

- `claude/skills/benchmark-infra-reviewer/SKILL.md`
- `claude/skills/benchmark-infra-reviewer/references/review-checklist.md`
- `claude/skills/benchmark-run-operator/SKILL.md`
- `claude/skills/benchmark-run-operator/references/benchmark-protocol.md`
- `claude/skills/benchmark-run-operator/references/stack-operations.md`
- `claude/skills/benchmark-run-operator/references/artifact-validation.md`
- `claude/skills/benchmark-run-operator/references/report-rebuild.md`

Claude derived skills:

- `workspace-steward`, derived from `codex/skills/workspace-steward`

Manifest and workflow evidence:

- `manifests/portable-files.toml`
- `workflows/claude-config.md`

## Standard

A domain-shaped skill deserves global runtime context when it protects repeated
high-cost work from predictable failure. It does not need to apply to every
repo. It does need a sharp trigger, a clear audience, and a failure mode large
enough to justify carrying it.

A domain-shaped skill should move to carried material when it is useful but
project-specific, rare, or too dependent on a local repo path, private setup, or
one benchmark campaign.

## Findings

### D1: Benchmark skills should stay global

Evidence:

- `benchmark-run-operator` directly addresses the long-run failure mode this
  review program cares about: invalid rows are work, missing rows are recovery
  queues, and a status packet is not a substitute for a route decision.
- Its references define comparison design, stack ownership, invalid-row
  recovery, final aggregation, report rebuilds, and provenance.
- `benchmark-infra-reviewer` is compact and read-only by default. It reviews
  benchmark-management diffs without launching rows unless the user explicitly
  asks.
- Both benchmark skills are mirrored into Claude with matching references.

Decision:

- Keep both benchmark skills globally installed.
- Do not move them to carried material.

Rationale:

- Benchmark runs are expensive in time and machine state. The skill text
  prevents a high-cost collapse into a clean blocker report or invalid
  publication.

Recommended PR:

- None now.

### D2: WebMCP skills should stay Codex-only for now

Evidence:

- `webmcp-eval-triage` classifies failures before tools, evals, prompts, or
  benchmark operations are changed.
- `webmcp-tool-authoring` depends on WebMCP tool registration, return-shape,
  declarative forms, page scope, and live validation.
- `webmcp-verify-tool` depends on WebMCP-capable browser evidence, inspector
  state, registered tools, and live runtime invocation.
- `workflows/claude-config.md` explicitly says to skip `webmcp-*` skills until
  Claude has the matching runtime.

Decision:

- Keep the WebMCP skills globally installed for Codex.
- Keep them out of Claude until Claude has a matching WebMCP runtime path.
- Do not move them to carried material yet.

Rationale:

- These skills are narrow, but they govern a recurring tool surface where weak
  evidence is dangerous. Their descriptions are specific enough that ordinary
  non-WebMCP work should not retrieve them.

Recommended PR:

- None now.

### D3: WebMCP skill set boundaries are coherent

Evidence:

- `webmcp-eval-triage` answers "who owns the failure?"
- `webmcp-tool-authoring` answers "what should the tool surface be?"
- `webmcp-verify-tool` answers "what live evidence proves the tool works?"

Decision:

- Keep these as three skills instead of folding them.

Rationale:

- Combining triage, authoring, and verification would blur owner, phase, and
  evidence standard. The split makes the agent pick the correct stance.

Recommended PR:

- None now.

### D4: `workspace-steward` should stay global

Evidence:

- The skill applies outside one project. It governs multi-repo workspaces,
  clean main checkouts, PR worktrees, experiments, local docs, artifacts, tmp
  space, and evidence rules.
- It front-loads a deletion-first decision filter before creating layout,
  scripts, or automation.
- It protects active work before move, prune, or cleanup operations.
- It gives a reusable umbrella workspace template only after the decision
  filter leaves a full skeleton as the smallest useful shape.

Decision:

- Keep `workspace-steward` globally installed.
- Do not move it to carried material.

Rationale:

- Workspace mistakes can delete work, hide evidence, or make the wrong repo the
  command target. That risk is broad enough for global context.

Recommended PR:

- None now.

### D5: `workspace-steward` Claude derivation is complete

Evidence:

- The Codex skill includes a project-template route:
  `references/project-template/`.
- `workspace-steward` is listed under `[claude].derived_skills`.
- `claude/skills/workspace-steward/` is absent, so there is no stale direct
  mirror.
- The Claude installer derives `SKILL.md` and `references/` from the Codex
  source, including `references/project-template/`.

Decision:

- Keep `workspace-steward` as a Claude derived skill.
- Do not restore a direct Claude source unless Claude needs runtime-specific
  wording.

Recommended PR:

- None now.

Follow-up status:

- Completed by the workspace-steward Claude derivation PR.
  `workspace-steward` now derives from the Codex source for Claude.

### D6: No immediate pruning target in this family

Evidence:

- Benchmark references are long, but they are procedure for fragile operations,
  not loose rationale.
- WebMCP references are long, but they encode live-runtime contracts, return
  shape rules, and verification standards.
- `workspace-steward` is broad, but its breadth maps to real workspace
  lifecycles and destructive boundaries.

Decision:

- No pruning is needed now.
- Revisit pruning only after real use shows retrieval noise or stale procedure.

Recommended PR:

- None now.

## Next PR Boundaries

Recommended order:

1. Leave benchmark and WebMCP skills unchanged.
2. Revisit this domain-shaped family only after usage shows a concrete weak
   section, stale contract, or retrieval-cost problem.

Completed follow-ups:

- `workspace-steward` was converted to a Claude derived skill.

## Verification

Commands used while preparing this audit:

```powershell
git status --short --branch
git fetch origin
gh pr list --state open --json number,title,isDraft,baseRefName,headRefName,url --limit 40
Get-Content -Raw <reviewed skill, reference, manifest, and workflow files>
Get-ChildItem -Recurse -File codex\skills\benchmark-infra-reviewer,codex\skills\benchmark-run-operator,codex\skills\webmcp-eval-triage,codex\skills\webmcp-tool-authoring,codex\skills\webmcp-verify-tool,codex\skills\workspace-steward
Get-ChildItem -Recurse -File claude\skills\benchmark-infra-reviewer,claude\skills\benchmark-run-operator
Select-String -Path manifests\portable-files.toml -Pattern "derived_skills|workspace-steward"
Test-Path claude\skills\workspace-steward
Test-Path codex\skills\workspace-steward\references\project-template\README.md
rg -n -i "fallback|best-effort|if possible|maybe|hopefully|history|provenance|global|carry|carried|project-specific|WebMCP|benchmark|workspace|poison|invalid|blocked|verified|verify|live proof" codex\skills\benchmark-infra-reviewer codex\skills\benchmark-run-operator codex\skills\webmcp-eval-triage codex\skills\webmcp-tool-authoring codex\skills\webmcp-verify-tool codex\skills\workspace-steward claude\skills\benchmark-infra-reviewer claude\skills\benchmark-run-operator workflows\claude-config.md manifests\portable-files.toml
```
