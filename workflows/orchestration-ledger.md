# Orchestration Ledger

Use this workflow when a long-running objective needs a compact mechanical index
across contexts, compactions, delegates, checks, or recovery decisions. The
principal authors the durable goal, plan, catalog, assignments, and checkpoints
in Markdown. The JSON ledger points to those control documents and records
principal-verified evidence, current routing, timestamps, and recovery gates.

This is repo-maintainer state. It is not installed into a Codex home, user skill
home, or Claude home.

## Purpose

A conversation is not a durable control surface. Contexts end, compactions lose
detail, and delegation changes the reader. The ledger makes the current control
state observable without asking every fresh context to reconstruct it from chat.

The ledger stays mechanical. The Markdown control documents carry meaning.

- **Goal document:** stable finished state, evidence standard, constraints, and
  amendment authority.
- **Plan and catalog:** approved route, active assignments, artifact locations,
  dependencies, and current decisions.
- **Assignment:** reviewed work packet given to a delegate.
- **Checkpoint:** principal-authored resume point before compaction or handoff.
- **JSON ledger:** links, phase, state, current owner, verified evidence,
  timestamps, mutation authority, and recovery circuits.

A delegate returns artifacts and evidence. The principal verifies that return and
records any resulting control-state change. Delegates do not invent ledger
formats or mutate the principal's control record.

## Local Boundary

The supported location is under `.local/`, with
`.local/orchestration-ledger.json` as the default. The directory is ignored and
listed as local-only. Keep durable project control documents in the project
location selected by its workspace guidance, usually under `local-docs/`.

The ledger may contain compact goal labels, file or URL locators, worker labels,
evidence summaries, and prepared decisions. Keep credentials, tokens, cookies,
private message content, raw logs, and copied source artifacts out of it.

## One Logical Principal

Every goal names one `control_writer`. That identity is the logical principal,
not a permanent process. A fresh context may assume the role only after reading
and verifying the named anchors and control documents.

Every mutation supplies:

- the principal identity;
- the expected control revision;
- the exact goal being changed.

A non-principal actor or stale revision fails before writing. The tool does not
support delegated edit grants. This preserves one reviewed interpretation of the
objective across finite contexts.

## Goal Record

Each goal records:

- the stable goal statement;
- authoritative anchors;
- principal-authored control documents;
- phase: `planning` or `implementation`;
- execution owner and current worker identity;
- current state and next judgment point;
- principal-verified evidence with producer and observation time;
- public-mutation authority and the exact named action;
- one prepared human decision, when needed;
- one principal writer and optimistic revision;
- per-slice recovery circuits;
- created, updated, and last-verified timestamps.

Changing `phase` to `implementation` records authority that already exists. It
does not create implementation authority by itself. The approved goal or plan
remains the source of that authority.

## Initialize A Goal

Create the Markdown control documents first, then initialize the index:

```powershell
.\scripts\orchestration-ledger.ps1 -Action init `
  -GoalId release-42 `
  -Goal "Ship the reviewed release" `
  -Anchor "product-requirements.md" `
  -ControlDocument "local-docs/control/goal.md" `
  -ControlDocument "local-docs/control/catalog.md" `
  -ExecutionOwner principal `
  -ControlWriter principal `
  -Phase planning `
  -State planned
```

The goal statement is not mutable through this CLI. Amend the authoritative goal
document under its declared authority, then create a new goal record or use the
project's explicit amendment procedure.

## Read And Validate

```powershell
.\scripts\compass.ps1 orchestration
.\scripts\compass.ps1 orchestration -GoalId release-42 -Json
.\scripts\orchestration-ledger.ps1 -Action validate
```

Before a fresh context continues work, it should be able to answer from the goal,
control documents, and current ledger:

- What finished state remains authoritative?
- Which source documents establish it?
- What phase is authorized?
- What evidence is current?
- What remains unresolved?
- What action can produce the next useful proof?

That is the fresh-context resume test.

## Record Phase And Routing

After an approved transition to implementation:

```powershell
.\scripts\orchestration-ledger.ps1 -Action set-phase `
  -GoalId release-42 `
  -Actor principal `
  -ExpectedRevision 1 `
  -Phase implementation
```

Record a current owner or worker without transferring control authorship:

```powershell
.\scripts\orchestration-ledger.ps1 -Action set-owner `
  -GoalId release-42 `
  -Actor principal `
  -ExpectedRevision 2 `
  -ExecutionOwner principal `
  -WorkerId implementation-auth-01
```

Update links when a reviewed control document supersedes an older one:

```powershell
.\scripts\orchestration-ledger.ps1 -Action set-links `
  -GoalId release-42 `
  -Actor principal `
  -ExpectedRevision 3 `
  -Anchor "product-requirements.md#revision-4" `
  -ControlDocument "local-docs/control/checkpoint.md"
```

Cancel the current assignment in one transition after issuing the runtime stop:

```powershell
.\scripts\orchestration-ledger.ps1 -Action set-state `
  -GoalId release-42 `
  -Actor principal `
  -ExpectedRevision 4 `
  -State cancelled
```

The cancelled transition clears `worker_id`, `next_action`, `next_check_at`, and
`decision_needed`; closes public mutation authority that is still authorized or
in flight; and closes active recovery ownership. A completed public mutation is
retained as completed history. Reinspect the runtime separately before treating
the delegate as inactive.

## Record Verified Evidence

A delegate may produce the observation. The principal inspects it and records
what it proves:

```powershell
.\scripts\orchestration-ledger.ps1 -Action add-evidence `
  -GoalId release-42 `
  -Actor principal `
  -ExpectedRevision 4 `
  -EvidenceKind test `
  -EvidenceSummary "Portable checks passed on the current head" `
  -EvidenceLocator "run:835" `
  -EvidenceProducer "implementation-auth-01" `
  -EvidenceObservedAt "2026-07-17T09:15:00-06:00"
```

The record distinguishes:

- who produced the evidence;
- when the state was observed;
- which principal verified and recorded it.

A worker's confident completion claim is a locator for inspection, not evidence
by itself.

## Recovery Circuits

A recovery circuit protects one slice from unchanged repeated attempts.

Begin an approved recovery assignment:

```powershell
.\scripts\orchestration-ledger.ps1 -Action begin-recovery `
  -GoalId release-42 `
  -Actor principal `
  -ExpectedRevision 5 `
  -SliceLabel checkout `
  -WorkerId recovery-01
```

Record a failure that changed the diagnosis or route:

```powershell
.\scripts\orchestration-ledger.ps1 -Action record-recovery-failure `
  -GoalId release-42 `
  -Actor principal `
  -ExpectedRevision 6 `
  -SliceLabel checkout `
  -FailureEvidence "run:842" `
  -DiscriminatingEvidence "trace isolates provider startup"
```

The circuit closes because another bounded attempt has a changed basis.

Record a failure that produced no new discriminating evidence:

```powershell
.\scripts\orchestration-ledger.ps1 -Action record-recovery-failure `
  -GoalId release-42 `
  -Actor principal `
  -ExpectedRevision 7 `
  -SliceLabel checkout `
  -FailureEvidence "run:843" `
  -NoNewEvidence
```

The circuit opens. Another attempt requires a changed hypothesis, input, runtime
path, or root-cause finding:

```powershell
.\scripts\orchestration-ledger.ps1 -Action reset-recovery `
  -GoalId release-42 `
  -Actor principal `
  -ExpectedRevision 8 `
  -SliceLabel checkout `
  -RootCauseEvidence "review:provider-startup"
```

`check-recovery` is an observation. It never claims or launches a worker.

## Public Mutation Gate

The gate records authority already granted by the user or repository workflow:

- `closed`: no public mutation is authorized;
- `authorized`: the exact recorded action is authorized;
- `in_flight`: that authorized sequence started;
- `complete`: that authorized sequence finished and was verified.

Changing the field does not grant permission.

## Operating Discipline

- Keep one logical principal writer per goal.
- Let delegates own assigned artifacts and return evidence.
- Keep objective meaning in reviewed Markdown control documents.
- Keep the JSON ledger compact and mechanical.
- Put pure waiting inside one bounded command.
- Use a monitor agent only when each observation requires limited judgment.
- Record absolute timestamps with time zones.
- Open recovery when another unchanged attempt would repeat motion without
  learning.
- Complete only when current evidence verifies the authoritative finished state,
  or the authorized owner amends that state.

## Verification

- `manifests/orchestration-ledger.schema.json` documents the current ledger
  schema version.
- `scripts/orchestration-ledger.py` validates and writes the ledger atomically.
- The path is restricted to `.local/` and rejects symlink traversal.
- `scripts/test-orchestration-ledger.py` covers principal authority, optimistic
  revision, evidence provenance, phase and link updates, recovery, migration,
  and path boundaries.
- `scripts/test-orchestration-ledger-lock.py` covers single-writer locking.
