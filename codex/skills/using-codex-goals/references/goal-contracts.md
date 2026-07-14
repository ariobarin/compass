# Goal Contracts

Use this reference when work needs a durable outcome and a small live control
surface.

## Outcome Contract

Write the stable layer first:

```markdown
# Outcome

## Finished State
Describe what exists when the work is done.

## Required Assertions
- A1: Observable assertion.
  - Pass evidence:
  - Status: unmet
  - Evidence:
- A2: Observable assertion.
  - Pass evidence:
  - Status: unmet
  - Evidence:

## Constraints
- Safety, scope, compatibility, budget, and authority limits.

## Exclusions
- Work intentionally outside this outcome.

## Amendment Authority
- Who may change finished state or assertion text.
```

Assertions should be independently checkable. Prefer product behavior, runtime
state, persisted artifacts, current-head checks, and attributable rows over
completion prose.

## Live Execution State

Keep mutable state compact and replace it rather than appending history:

```markdown
# Live State

Outcome revision: 3
Control writer: controller
Execution owner: worker-7
Observed state:
- ...

Unmet assertions:
- A2
- A4

Current action:
- ...

Next proof:
- ...

External wait or decision:
- none

Last evidence:
- A1 verified by run:835
```

The outcome revision changes only after an authorized amendment. Ordinary
progress changes observed state, assertion status, and next action.

## Evidence Rules

For each material result:

1. identify which assertion it supports or falsifies;
2. record an exact locator;
3. distinguish direct observation from inference;
4. update status;
5. recompute the remaining assertion set;
6. route the smallest proof-producing action.

Evidence locators can be a commit SHA, current-head check, test command, artifact
path, benchmark row set, screenshot, runtime query, or reviewer result. Do not
use "worker says done" as a locator.

## Assignment Shape

A delegated slice should include:

```text
Parent outcome, read-only:
Parent assertions advanced:
Slice postcondition:
Allowed edits or actions:
Authoritative inputs:
Evidence required:
Return conditions:
```

The worker returns when the slice postcondition is verified or a real exception
exists. A turn boundary or progress update does not transfer ownership.

## Exception Diagnosis

A useful exception report answers:

```text
Which parent assertion remains unmet?
What exact condition prevents the next safe action?
What did the last attempt prove?
What state exists now?
What changed since the prior attempt?
What smallest action could produce new evidence?
Who owns that action?
```

Do not route another identical attempt when failure signature, inputs, and
runtime path are unchanged and no new discriminating evidence exists.

## Blocked And Waiting

Use `blocked` only when:

- a specific external dependency, missing authority, or unavailable fact is
  named;
- no safe local action can advance any unmet assertion;
- reversible preparation and alternative hypotheses are exhausted;
- the unblocking owner or event is identified.

Use `waiting` when an external event is expected and the next useful judgment
can be scheduled or triggered. Put mechanical polling inside one bounded command
rather than spending model turns.

No fixed number of turns or attempts proves blockage. Evidence about available
actions does.

## Human Decision Packet

When authority is required, prepare:

```markdown
## Decision
Exact question:

## Why It Is Required
Assertion or constraint affected:

## Options
1. Option with consequence.
2. Option with consequence.

## Safe Work Already Completed
- ...

## Recommendation
- ...
```

Do not ask the user to solve routine diagnosis.

## Pause Packet

```markdown
## Paused Goal
Outcome revision:
Execution owner:
Active processes stopped:
Monitors stopped:
Unmet assertions:
Last evidence:
First safe resume action:
External conditions to recheck:
```

Pause is not complete, blocked, or cancelled.

## Completion Packet

```markdown
## Completion
Outcome revision:
Verified assertions:
- A1: evidence locator
- A2: evidence locator

Authorized amendments:
- none

Residual concerns:
- ...

Public mutations:
- authorized action and verification, or none
```

Residual concerns do not erase verified completion, but they must remain
separate from assertion status.

## Benchmark Boundary

For benchmark work:

- this goal contract owns final assertions, evidence mapping, and completion;
- `benchmark-run-operator` owns launch contracts, worker and stack execution,
  provenance, valid-row rules, recovery, and aggregate rebuilds;
- benchmark evidence returns here as attributable artifacts and row sets.

Do not duplicate benchmark process doctrine in the goal surface.
