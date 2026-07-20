# Assignment: <name>

Assignment ID: <stable-id>
Prepared by: <principal>
Prepared at: <ISO-8601 timestamp with timezone>
Review state: draft | approved | user-waived
Parent goal: <goal-id>
Parent assertions advanced: <ids>
Return channel: <thread, agent handle, or named location>

## Slice Outcome

<One observable postcondition for this assignment.>

## Integration Target

<How the returned artifact or evidence advances the parent goal.>

## Authoritative Anchors

Read in this order:

1. <anchor>
2. <anchor>

## Scope And Authority

- Owned artifact or investigation: <boundary>
- Allowed edits or actions: <exact grant>
- Production mutation authority: yes | no | exact paths
- Public mutation authority: none | exact action
- State to preserve: <unrelated work, services, branches, or data>

## Evidence Required

- <command, artifact, review, observation, or result>

## Return Conditions

Return once when the slice outcome is verified or one exact missing decision,
authority boundary, external event, or exhausted recovery path prevents further
safe useful work.

If the user or principal explicitly holds, cancels, or revokes the assignment,
stop further mutation, preserve current artifacts and evidence, and return
`held` or `cancelled` without completing extra scope.

## Return Record

- Result: completed | needs decision | waiting external | failed | held | cancelled
- Slice outcome claimed:
- Artifact or files changed:
- Preserved artifact and evidence locators:
- Process or delegate state still requiring verification:
- Checks and observations:
- Evidence mapped to parent assertions:
- Remaining slice gap:
- Recovery attempted:
- Exact next action and owner:
- Residual concerns, separate from completion:

For `held` or `cancelled`, leave the slice outcome unclaimed, name the authority
that ended, and provide the preservation evidence needed for the principal to
verify inactive state independently.
