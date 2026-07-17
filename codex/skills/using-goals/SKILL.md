---
name: using-goals
description: Preserve stable outcomes, anchors, evidence, authority, and resumable control state across long-running work.
---

# Using Goals

Use a goal when work must survive turns, compaction, restarts, or delegated
assignments without losing what completion means. This skill exists to keep the
finish line stable while plans, workers, failures, and next actions change.

The principal authors the goal and control packet. Delegates return artifacts
and evidence. They do not rewrite the objective or maintain parallel ledgers.

## Stable Goal

A durable goal names:

- a stable ID and revision;
- the finished state;
- independently observable assertions;
- exact pass evidence for each assertion;
- constraints and exclusions;
- authoritative anchors in precedence order;
- planning and implementation authority;
- public mutation authority;
- amendment authority.

The goal remains stable until its named authority records an amendment. A failed
command, new prerequisite, implementation choice, worker return, review,
timeout, or discovered repair changes the route or observed state. It does not
change what finished means.

Read [references/goal-contracts.md](references/goal-contracts.md) when creating or
repairing the control packet.

## Principal-Authored Control

Keep one logical author across finite contexts. The user-facing principal, or
the user directly, prepares and reviews goals, plans, catalogs, assignments, and
checkpoints.

Delegation is lossy. Give each delegate a reviewed assignment with the smallest
complete set of anchors, scope, authority, evidence, and return conditions. The
delegate owns its assigned artifact and returns evidence through the named
channel. The principal verifies that evidence and updates current state.

## Separate Stable Meaning From Current State

Keep current state compact and replace it as evidence changes. It should answer:

- which goal revision is authoritative;
- what observable state exists now;
- which assertions remain unmet;
- what work is active and where;
- what evidence arrived;
- what decision or next proof can reduce the gap;
- when the state was last verified.

Historical narrative belongs in an archive. The current ledger is not a diary.

## Preserve Planning Authority

Record whether the objective is in planning or implementation. Planning may
include inspection, research, questions, plans, and explicitly scoped
experiments. Production mutation begins when the named authority opens that
phase.

Material assignments should be reviewable before dispatch. User review may be
covered by previously granted authority or explicitly waived.

## Reconcile Evidence

After each material result:

1. identify which assertion it supports or falsifies;
2. record an exact evidence locator and observation time;
3. distinguish direct observation from inference;
4. update current status;
5. recompute the remaining assertion set;
6. choose the smallest proof-producing next action.

A completed task, phase, review, process, or wait is progress until the whole
required assertion set is verified.

## Survive Context Change

Before compaction, restart, pause, or deliberate handoff, write a checkpoint
that names the goal revision, anchors, observed state, accepted evidence,
remaining gap, active work, and next verification.

A successor principal reopens authoritative anchors in order and verifies
changeable state before continuing. The fresh-context test passes when that
successor can resume correctly without private conversation history.

## Completion

Complete only when current evidence verifies every required assertion, or the
amendment authority explicitly records an accepted different endpoint. Keep
residual concerns separate from assertion status.
