# Compass Glossary

These terms exist because confusing them changes behavior. Keep the vocabulary
small and use each term consistently.

## Principal

The user-facing logical owner of an objective. The underlying model context may
change after compaction or restart, but the principal role resumes the same
intention from durable control documents.

Confusing the principal with every temporary worker distributes authorship and
lets the objective drift.

## Context

One finite model working state, including instructions, conversation, reads,
and tool results currently available to it.

A context is temporary. The objective must survive without it.

## Compaction

A continuity event that reduces or replaces accumulated context. Treat it as a
lossy handoff and recover from authoritative anchors plus a current checkpoint.

## Anchor

An authoritative source for meaning or truth, such as a user-approved brief,
PRD, issue, contract, repository file, current branch, or observable runtime
surface.

A summary may point to an anchor. It does not silently replace one.

## Goal

The stable achieved state, required evidence, constraints, exclusions, and
amendment authority for a long-running objective.

A goal says what finished means. It does not narrate current progress.

## Plan

The current intended route from observed state to the goal. A plan may change as
evidence changes while the goal remains stable.

## Control Document

A principal-authored document that preserves goal, plan, assignments, current
state, or checkpoints across contexts.

Delegates return evidence for these documents. They do not invent parallel
control documents.

## Catalog

A compact index of active workstreams, workers, branches, worktrees, monitors,
artifacts, and their authoritative locations.

A catalog locates state. It does not duplicate every state entry.

## Ledger

A structured mechanical control record with defined fields, one writer,
revision protection, and explicit mutation rules. Compass's JSON orchestration
ledger is the canonical example.

Use a tracker for an ordinary list of items and statuses. Use a decision log for
a chronological decision history. Reserve ledger for records whose structure
and control semantics matter.

## Checkpoint

A principal-authored resume packet written before compaction, interruption, or
handoff. It names the goal revision, anchors, observed state, accepted evidence,
remaining gap, active work, and next decision.

## Assignment

A reviewed delegation packet with a bounded outcome, relevant anchors, allowed
actions, evidence target, and return channel.

An assignment advances the goal. It does not amend the goal.

## Worker

A delegate that owns one assigned artifact, investigation, review, or monitored
workstream until its return condition is satisfied.

## Controller

The principal role above delegated execution. It authors control state,
prepares assignments, reconciles evidence, corrects routes, and judges parent
completion.

## Return Channel

The stable locator a delegate uses to return evidence or request a material
decision. It may be a thread ID, parent agent handle, message channel, or named
control location supported by the runtime.

## Evidence

A current observation or durable artifact that supports or falsifies a claim.
Examples include a commit SHA, command result, review, screenshot, benchmark row
set, runtime query, or persisted file.

A worker's confidence is a claim, not evidence.

## Mechanical Wait

One bounded command that waits for a stable observable condition and returns a
compact terminal result.

Repeated model turns are not a mechanical wait.

## Monitor

A narrow observer for a named workstream or condition. A monitor reports state
and escalates anomalies. It does not own the parent objective.

## Worktree

A real repository checkout attached to a branch. Work in a PR worktree may enter
production through review and merge.

## Micro-Experiment

A tiny disposable program that answers one technical uncertainty outside the
production implementation. The finding may graduate. The experimental code does
not.

## Integration Spike

Disposable investigation against the real repository when the uncertainty
cannot be tested in isolation. It belongs in a clearly labeled disposable
worktree, not in the micro-experiment directory.

## Artifact

A generated output retained as evidence or as a deliverable, such as a report,
export, manifest, benchmark result, screenshot, or archive.

## Amendment

An authorized change to the stable goal or its required assertions. Route
changes and implementation discoveries are not amendments by themselves.

## Completion

The state in which current evidence satisfies every required part of the goal,
or the authorized owner explicitly amends the goal to accept a different end
state.
