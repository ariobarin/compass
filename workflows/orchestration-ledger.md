# Orchestration Ledger

Use this workflow when a controller needs durable local control state across
sessions, workers, checks, or decision points. The ledger records authority, current state, evidence, and recovery gates. It does not execute work or replace
the worker that owns delivery.

This is repo-maintainer state. It is not installed into a Codex home, user skill
home, or Claude home.

## Local Boundary

The supported location is under `.local/`, with
`.local/orchestration-ledger.json` as the default. The directory is ignored and
listed as local-only. Do not copy the ledger into commits, prompts, PR bodies,
MCP responses, or installed guidance.

The ledger may contain compact goal labels, worker labels, evidence locators,
and prepared decisions. It must not contain credentials, tokens, cookies,
private message content, raw logs, or copied source artifacts.

## Control Record

Each goal records:

- the outcome to pursue;
- execution owner and worker identity;
- current state and next action;
- compact completion evidence;
- public-mutation authority and the exact named action;
- one prepared human decision, when needed;
- one control writer and optimistic revision;
- exact delegated mutation grants;
- per-slice recovery circuits.

A recovery circuit records whether a successor is unclaimed, claimed, or open,
plus the latest failure evidence and the evidence that permits another attempt.
It does not count retries. A failed successor must declare one of two states:

- new discriminating evidence changed the diagnosis, inputs, or runtime path, so
  another bounded successor may be claimed;
- no new discriminating evidence exists, so the circuit opens and another
  symptom-level successor is refused.

Resetting an open circuit is control-writer-only and requires root-cause
evidence.

Schema version 3 replaces the successor failure counter with evidence fields.
The runtime reads schema versions 1 and 2 and migrates them on the next
successful write. A version 2 count becomes a compact migration evidence
locator, while its prior open or closed state is preserved.

## Authority

Every mutation of an existing goal declares the actor and expected control
revision. The control writer may perform any mutation. Another actor needs a
grant naming the exact mutation. A successful mutation increments the revision.
A stale revision or missing grant fails before any write.

The public-mutation gate records authority that already exists:

- `closed`: no public mutation is authorized;
- `authorized`: the user or repository workflow granted the recorded action;
- `in_flight`: the authorized public sequence started;
- `complete`: the authorized sequence finished and was verified.

Changing the field does not grant permission.

## Commands

Read the ledger:

```powershell
.\scripts\compass.ps1 orchestration
.\scripts\compass.ps1 orchestration -GoalId release-42 -Json
```

Initialize a goal:

```powershell
.\scripts\orchestration-ledger.ps1 init `
  -GoalId release-42 `
  -Goal "Ship the reviewed release" `
  -ExecutionOwner release-worker `
  -ControlWriter controller `
  -WorkerId thread-123 `
  -State active
```

Grant a recovery worker only the mutations it needs:

```powershell
.\scripts\orchestration-ledger.ps1 set-grant `
  -GoalId release-42 `
  -Actor controller `
  -ExpectedRevision 1 `
  -GrantActor recovery-worker `
  -Mutation claim-successor `
  -Mutation record-successor-failure `
  -Mutation record-successor-success
```

Claim a slice as the atomic prelaunch gate:

```powershell
.\scripts\orchestration-ledger.ps1 claim-successor `
  -GoalId release-42 `
  -Actor recovery-worker `
  -ExpectedRevision 2 `
  -SliceLabel magento-checkout
```

Record a failed attempt that produced new discriminating evidence:

```powershell
.\scripts\orchestration-ledger.ps1 record-successor-failure `
  -GoalId release-42 `
  -Actor recovery-worker `
  -ExpectedRevision 3 `
  -SliceLabel magento-checkout `
  -FailureEvidence run:842 `
  -DiscriminatingEvidence "trace isolates provider startup"
```

The slice closes and may be claimed again because the next attempt has a changed
basis.

Record a failed attempt that did not improve the diagnosis:

```powershell
.\scripts\orchestration-ledger.ps1 record-successor-failure `
  -GoalId release-42 `
  -Actor recovery-worker `
  -ExpectedRevision 5 `
  -SliceLabel magento-checkout `
  -FailureEvidence run:843 `
  -NoNewEvidence
```

The slice opens. `check-recovery` and `claim-successor` then fail for that slice.

Reset after root-cause evidence changes the route:

```powershell
.\scripts\orchestration-ledger.ps1 reset-recovery `
  -GoalId release-42 `
  -Actor controller `
  -ExpectedRevision 6 `
  -SliceLabel magento-checkout `
  -RootCauseEvidence review:runtime-child-path
```

Record success only from the actor that owns the claim:

```powershell
.\scripts\orchestration-ledger.ps1 record-successor-success `
  -GoalId release-42 `
  -Actor recovery-worker `
  -ExpectedRevision 8 `
  -SliceLabel magento-checkout
```

Record a next action only when a future wake needs judgment:

```powershell
.\scripts\orchestration-ledger.ps1 set-next `
  -GoalId release-42 `
  -Actor controller `
  -ExpectedRevision 9 `
  -NextAction "Inspect hosted checks and current-head review" `
  -NextCheckAt "2026-07-12T12:00:00Z"
```

Append compact evidence:

```powershell
.\scripts\orchestration-ledger.ps1 add-evidence `
  -GoalId release-42 `
  -Actor controller `
  -ExpectedRevision 10 `
  -EvidenceKind test `
  -EvidenceSummary "Portable checks passed on the current head" `
  -EvidenceLocator "run:835"
```

Validate the stored shape:

```powershell
.\scripts\orchestration-ledger.ps1 validate
```

## Operating Discipline

- Keep one execution owner per goal.
- Use the ledger for control state, not narrative history.
- Put mechanical waits inside one bounded command.
- Append evidence that can support or falsify completion.
- Open recovery when another unchanged attempt would repeat motion without
  learning.
- Resume only when a changed hypothesis, input, runtime path, or root-cause
  finding is named.
- Mark a goal complete only when evidence matches the outcome or the user
  explicitly accepts an incomplete endpoint.

## Verification

`manifests/orchestration-ledger.schema.json` documents the stored shape.
`scripts/orchestration-ledger.py` validates it without an external schema
dependency, writes atomically, and restricts paths to `.local/`.
`scripts/test-orchestration-ledger.py` covers lifecycle, authority, migration,
and evidence-based recovery behavior.
