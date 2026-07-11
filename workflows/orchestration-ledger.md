# Local Orchestration Ledger

Use this workflow when a controller needs compact state across turns, workers,
or repository lanes. The ledger records the goal, execution owner, worker,
state, next action, evidence, public-mutation gate, and prepared human decision.
It is local coordination state, not durable policy and not a replacement for
live GitHub, process, or runtime inspection.

The default file is `.local/orchestration-ledger.json`. Compass ignores and
classifies `.local/` as local-only. Do not commit the ledger, raw logs, session
content, credentials, or generated worker state.

## Start A Lane

Create one item per independently owned delivery lane:

```powershell
.\scripts\orchestration-ledger.ps1 -Action Init `
  -Id compass-audit `
  -Goal "Land the measured skill-routing audit" `
  -Repository "ariobarin/compass" `
  -ExecutionOwner "Codex app thread 123" `
  -WorkerId "thread-123" `
  -CompletionEvidence "focused tests pass" `
  -CompletionEvidence "current-head review gates pass"
```

An item starts `planned` with its public-mutation gate `closed`. Move it to
`active` only after an execution owner exists:

```powershell
.\scripts\orchestration-ledger.ps1 -Action SetState -Id compass-audit -State active
```

## Keep The Next Move Explicit

Record the smallest next action and an optional UTC check time:

```powershell
.\scripts\orchestration-ledger.ps1 -Action SetNext `
  -Id compass-audit `
  -NextAction "Inspect the newest CI and review evidence" `
  -NextCheckAt "2026-07-11T18:00:00Z"
```

Use `ClearNext` when the action is complete or ownership changes. Do not use the
ledger as a polling loop. Mechanical waits belong in one bounded command or a
watcher. A scheduled check earns its turn only when the controller will make a
real judgment from new evidence.

## Record Evidence, Not Transcripts

Store compact claims with durable locators:

```powershell
.\scripts\orchestration-ledger.ps1 -Action AddEvidence `
  -Id compass-audit `
  -EvidenceKind check `
  -EvidenceSummary "Portable matrix passed on Windows and Linux" `
  -EvidenceLocator "GitHub run 123456"
```

Evidence entries are summaries, not raw logs. The ledger caps each item at 100
entries. When that limit is near, compress the lane into a final artifact or a
new item rather than turning local coordination state into an archive.

## Public Mutation Gate

The gate records whether a public sequence is admitted, held, or blocked:

```powershell
.\scripts\orchestration-ledger.ps1 -Action SetGate `
  -Id compass-audit `
  -GateState open `
  -GateReason "User authorized the exact branch push and draft PR"
```

An open ledger gate is not permission. It records the controller's current
coordination decision and supporting reason. Actual push, PR mutation, merge,
release, deployment, or publication authority still comes from the user and
repository workflow at the moment of action. Recheck live state before acting.

Use `closed` when no public action is admitted. Use `blocked` with the concrete
external dependency when the sequence cannot proceed.

## Prepare Decisions

Escalate one exact decision with evidence and real options:

```powershell
.\scripts\orchestration-ledger.ps1 -Action SetDecision `
  -Id compass-audit `
  -DecisionQuestion "Which PR should merge first?" `
  -DecisionOption "Merge the audit before the ledger" `
  -DecisionOption "Hold both for a combined review" `
  -DecisionEvidence "Both are green; the ledger depends on the audit dispatcher"
```

Use `ClearDecision` after the user decides. Do not store vague questions or raw
blocker packets. Finish every safe reversible step first, then present the exact
choice that remains.

## State Model

Normal transitions are:

```text
planned -> active -> waiting | blocked | review | complete | cancelled
waiting -> active | blocked | cancelled
blocked -> active | waiting | cancelled
review -> active | blocked | complete | cancelled
```

Reopening `complete` or `cancelled`, or taking another nonstandard transition,
requires `-Force`. The flag makes the exception explicit; it does not change the
underlying authority boundary.

## Inspect And Close

Use the stable Compass entry point for read-only status:

```powershell
.\scripts\compass.ps1 orchestration
.\scripts\compass.ps1 orchestration -Plain
.\scripts\compass.ps1 orchestration -Json
```

Use the focused script for one item or mutation:

```powershell
.\scripts\orchestration-ledger.ps1 -Action Status -Id compass-audit
.\scripts\orchestration-ledger.ps1 -Action Validate
.\scripts\orchestration-ledger.ps1 -Action Remove -Id compass-audit
```

Removal normally requires `complete` or `cancelled`. The ledger uses an
exclusive lock and atomic replacement for writes. If a lock remains after a
crashed process, inspect the lock file and active writers before removing it.

Do not expose the live ledger through the unauthenticated Compass MCP app. A
future read-only summary may be appropriate only with an explicit local or
authenticated boundary that cannot leak private repositories, worker IDs,
decisions, or operational evidence.
