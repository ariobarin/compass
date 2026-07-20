# Goal Contracts

Use this reference to create a compact principal-authored control packet for
long-running work.

## Stable Goal

```markdown
# Goal: <name>

Goal ID: <stable-id>
Revision: 1
Created at: <timestamp with timezone>
Principal: <logical principal>
Amendment authority: <identity>

## Finished State

<Achieved condition.>

## Required Assertions

- A1: <observable assertion>
  - Pass evidence: <exact surface>
- A2: <observable assertion>
  - Pass evidence: <exact surface>

## Constraints

- <scope, safety, compatibility, budget, and authority limits>

## Exclusions

- <work deliberately outside the goal>

## Authoritative Anchors

1. <user-approved brief, PRD, issue, or contract>
2. <repository or runtime source of truth>

## Implementation Authority

Phase: planning | implementation
Production edits authorized by: <identity or none>
Public mutations authorized: <exact actions or none>

## Live State

See `<catalog>` and `<checkpoint>`.
```

Assertions should be independently checkable. Prefer product behavior, runtime
state, persisted artifacts, current-head checks, and attributable result rows
over completion prose.

## Runtime Goal Payload

When the runtime provides an active goal field, keep its payload compact. Include
the finished state, controlling constraints and authority, plus versioned or
revision-bound locators for the durable goal and current checkpoint. Keep the
full assertion set, settings, ledger, evidence history, and active-work table in
those anchors.

The runtime payload is a stable activation contract, not a copy of every control
document. It must remain complete enough to recover the anchors when surrounding
conversation is lost.

## Current Catalog

```markdown
# Work Catalog

Goal: <id> revision <n>
Control author: <principal>
Updated at: <timestamp>
Last verified at: <timestamp>
Applies to commit or runtime identity: <locator>

## Observed State

...

## Unmet Assertions

- A2

## Active Work

| ID | Assignment | Worker or process | Worktree or artifact root | State | Return channel | Last evidence |
| --- | --- | --- | --- | --- | --- | --- |

## Current Decision

...

## Next Proof

...
```

The principal updates this document from verified returns. A worker report is
an evidence locator, not automatic acceptance.

## Assignment

```text
Assignment ID:
Prepared by:
Review state: draft | approved | user-waived
Parent goal and assertion IDs:
Slice outcome:
Integration target:
Authoritative anchors, in order:
Allowed edits or actions:
Production mutation authority:
Public mutation authority:
State to preserve:
Evidence required:
Return channel:
Return conditions:
```

The assignment advances the goal and cannot amend it.

## Checkpoint

```text
Goal and revision:
Principal role:
Written at:
Last verified at:
Reason for checkpoint:
Anchors to reopen, in order:
Observed state:
Accepted evidence mapped to assertions:
Remaining gap:
Active delegates, processes, and worktrees:
Risks and decisions:
Next proof-producing action:
Successor verification:
```

Write the checkpoint before context loss, not after the successor discovers the
missing state.

## Blocked, Waiting, And Decisions

Use `blocked` when a named external dependency, missing authority, or unavailable
fact prevents every safe local action that could advance any unmet assertion.

A control document may record that observed state immediately. Changing an
active runtime goal to a terminal blocked status follows that runtime's own
transition contract. Do not treat the catalog label as authority to bypass a
required persistence audit or resumed-goal reset.

Use `waiting` when a named external event is expected and the next useful check
can be scheduled. Put pure polling inside one bounded command.

When human authority is required, prepare the exact question, affected
assertion, options and consequences, safe work already completed, and a
recommendation.

## Completion Packet

```markdown
## Completion

Goal revision:
Verified assertions:
- A1: <evidence locator>
- A2: <evidence locator>

Authorized amendments:
- none

Residual concerns:
- ...

Public mutations:
- <authorized action and verification, or none>
```
