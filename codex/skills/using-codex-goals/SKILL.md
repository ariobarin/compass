---
name: using-codex-goals
description: Maintain durable outcomes, acceptance assertions, evidence, and live goal state across long-running work.
---

# Using Codex Goals

Use this skill when work must survive turns, workers, compaction, or restarts
without losing what completion means. It owns outcome semantics and evidence
reconciliation. It does not own benchmark execution, process supervision, or
artifact recovery.

## Keep Three Layers Distinct

- **Parent outcome:** stable finished state, constraints, exclusions, and
  amendment authority.
- **Acceptance ledger:** stable assertion text with current status and linked
  evidence.
- **Execution state:** current owner, observed state, blockers, and next action.

A failed command, discovered prerequisite, repair, phase, worker return, or
monitor timeout changes execution state. It does not rewrite the parent outcome.

Read [goal-contracts.md](references/goal-contracts.md) when creating or repairing
a durable goal surface.

## Start With Assertions

Write the outcome as observable assertions. Each assertion needs:

- a stable identifier;
- exact pass evidence;
- current status: unmet, in progress, verified, blocked, or removed by authorized
  amendment;
- evidence locators;
- the owner of the next proof-producing action.

Completion is a reconciliation operation. After material evidence arrives,
attach it to assertions, update status, recompute the unmet set, and route the
next action. A completed subtask is not completion while a required assertion
remains unverified.

## Keep Live State Small

The live surface should answer:

- what finished state is still authoritative;
- which assertions remain unmet;
- who owns the current action;
- what evidence arrived;
- what action can reduce the remaining gap;
- what exact external event or decision is required, if any.

Archive history elsewhere. Do not let a long diary become current authority.

## Blocked Means No Safe Move Exists

Mark the goal blocked only when current evidence names a specific external
dependency, authority boundary, or unavailable fact and no safe local action can
advance any unmet assertion. Repeated turns, failed attempts, uncertainty, or
controller silence are not blocker evidence.

Before escalating, finish reversible local work, test alternative hypotheses,
prepare the exact decision, and name the event or owner that can unblock the
goal. Use waiting when an external event is expected and a bounded next check is
useful.

## Ownership

- The controller owns the parent outcome, assertion text, amendments, and final completion judgment.
- Execution owners produce artifacts and evidence for assigned slices.
- Reviewers and validators may change assertion status through evidence, but do
  not silently rewrite the acceptance contract.
- `benchmark-run-operator` owns benchmark launch, provenance, valid-run rules,
  and recovery. This skill consumes that evidence against the parent assertions.
- `monitor-to-completion` owns mechanical waiting, not goal completion.

## Pause, Resume, And Handoff

A pause stops owned work and monitors without claiming completion or blockage.
Record the current owner, active process state, unmet assertions, last evidence,
and first safe resume action.

After compaction, restart, or handoff, reopen authoritative inputs in precedence order. Treat summaries and history as evidence, not authority.

## Completion

Complete only when every required assertion is verified by current evidence, or
when the authorized outcome owner explicitly amends the contract to accept an
incomplete endpoint. Record the amendment, remaining dependency, and responsible
owner.
