# Compass Review Program State

This is repo-local handoff state for continuing the Compass review program. It
is not installed runtime guidance, not a second inventory, and not proof of
current GitHub state. Verify the current branch, open PR stack, and source
files before deriving new work.

## Current Posture

- Every first audit queue in `local-docs/compass-surface-inventory.md` has an
  audit packet.
- The open review-program stack has converted the obvious gaps into focused
  PRs: review routing, hook coverage, carried capability routing, Claude mirror
  handling, mechanical gates, and skill-authoring validation.
- Most current packets now say no immediate runtime cut is justified. Treat
  those decisions as pressure against invented edits, not as permission to stop
  reading.
- The carried-but-not-global route exists and is mechanically checked. No skill
  has moved there yet. Do not demote a skill until current source evidence
  proves it fails the global-install test.
- Retired Claude cleanup is a future gate, not current work. Add it in the same
  PR that removes or demotes a Claude-installed surface.

## Picking The Next PR

Use this order:

1. Inspect current files and open PR state. Old packet verification commands are
   audit history, not current proof.
2. Read the packet for the surface under review, then read the source files it
   names.
3. If the packet says no immediate cut and current source confirms it, do not
   manufacture a runtime edit. Look for stale state, a missing mechanical gate,
   or real use evidence instead.
4. If current source contradicts a packet, refresh the packet first. Do not
   build a runtime PR on stale audit state.
5. If a runtime edit is justified, keep the PR narrow: one skill family, one
   hook, one workflow, one manifest boundary, or one mechanical gate.

## State Classes

- Completed or no immediate cut: orientation, loop governance, PR and review
  surfaces, domain-shaped skills, creation and writing skills, maintainer
  workflows, mechanical truth, and hooks.
- Waiting for future evidence: first carried demotion, retired Claude cleanup,
  and any retrieval-noise or stale-procedure finding from real use.
- External current state: draft PRs, check results, review status, and branch
  bases. Inspect those through Git and GitHub each time.

## Maintenance Rule

Update this file only when the review program's state class changes: a new
audit queue appears, a route is added, a first demotion happens, a future gate
is retired, or the stack shape changes enough to affect how the next agent
should choose work. Do not update it for routine wording cleanup.
