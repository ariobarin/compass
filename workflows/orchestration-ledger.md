# Orchestration Ledger

Use this workflow when a controller needs durable local control state across
several sessions, workers, checks, or decision points. The ledger records the
contract and current evidence. It does not execute work, create authority, or
replace the worker that owns delivery.

This is repo-maintainer state. It is not installed into a Codex home, user skill
home, or Claude home.

## Local Boundary

The only supported location is under `.local/`, with
`.local/orchestration-ledger.json` as the default. The directory is ignored and
listed as local-only. Do not copy the ledger into commits, prompts, PR bodies,
MCP responses, or installed agent guidance.

The ledger may contain goal and worker labels, evidence locators, and prepared
decisions. It must not contain credentials, tokens, cookies, private message
content, raw logs, or copied source artifacts. Use compact locators such as a
commit SHA, PR number, workflow run, test command, or local artifact name.

Compass MCP is intentionally unauthenticated and read-only. Do not expose this
local ledger through it without a separate authenticated design and an explicit
review of what becomes remotely visible.

## Control Record

Each goal records:

- achieved state to pursue;
- execution owner and worker identity;
- current state;
- next action and optional next check time;
- compact completion evidence;
- public-mutation gate and the exact named action it covers;
- one prepared human decision, when needed.

The public-mutation gate records authority that already exists:

- `closed`: no public mutation is authorized;
- `authorized`: the user or repository workflow granted the recorded action;
- `in_flight`: the authorized public sequence has started;
- `complete`: the authorized public sequence finished and was verified.

Changing the field does not grant permission. Set `authorized` only after the
real user or repository contract authorizes the corresponding public action.

## Commands

Read all goals or one goal:

```powershell
.\scripts\compass.ps1 orchestration
.\scripts\compass.ps1 orchestration -GoalId release-42 -Json
```

Initialize a goal and name its execution owner:

```powershell
.\scripts\orchestration-ledger.ps1 init `
  -GoalId release-42 `
  -Goal "Ship the reviewed release" `
  -ExecutionOwner release-worker `
  -WorkerId thread-123 `
  -State active
```

Reroute execution ownership without recreating the goal:

```powershell
.\scripts\orchestration-ledger.ps1 set-owner `
  -GoalId release-42 `
  -ExecutionOwner recovery-worker `
  -WorkerId thread-456
```

Record the next action and the time when fresh judgment is useful:

```powershell
.\scripts\orchestration-ledger.ps1 set-next `
  -GoalId release-42 `
  -NextAction "Inspect hosted checks and current-head review" `
  -NextCheckAt "2026-07-12T12:00:00Z"
```

Record an already-authorized public action before it starts:

```powershell
.\scripts\orchestration-ledger.ps1 set-gate `
  -GoalId release-42 `
  -Gate authorized `
  -GateAction "merge PR 42"
```

Append compact evidence:

```powershell
.\scripts\orchestration-ledger.ps1 add-evidence `
  -GoalId release-42 `
  -EvidenceKind test `
  -EvidenceSummary "Portable checks passed on the current head" `
  -EvidenceLocator "run:835"
```

Prepare the exact decision that exceeds controller authority:

```powershell
.\scripts\orchestration-ledger.ps1 set-decision `
  -GoalId release-42 `
  -DecisionQuestion "Which release channel should receive this build?" `
  -DecisionOption @("stable", "beta")
```

Validate the stored shape:

```powershell
.\scripts\orchestration-ledger.ps1 validate
```

## Operating Discipline

- Keep one execution owner per goal. The controller records and verifies; the
  worker owns implementation, processes, logs, and immediate recovery.
- Update the next action when the current one completes or stops being the
  smallest executable move.
- Put mechanical waits inside one bounded command. Use a next-check time only
  when the next wake requires model judgment.
- Append evidence that can support or falsify completion. Do not use tidy status
  prose as proof.
- Prepare a decision only after safe reversible work is complete. Include real
  options rather than a helpless blocker report.
- Mark a goal complete only when its evidence matches the achieved state or the
  user explicitly accepts an incomplete endpoint.

## Schema And Verification

`manifests/orchestration-ledger.schema.json` documents the stored shape.
`scripts/orchestration-ledger.py` performs the runtime validation without an
external JSON Schema dependency, writes atomically, and restricts paths to the
repo's `.local/` directory. `scripts/test-orchestration-ledger.py` covers the
control lifecycle, invalid state, path escape, symlink, and validation cases.
