---
name: orchestration-controller
description: Preserve a parent objective above delegated work, prepare reviewed assignments, reconcile evidence, and correct drift.
---

# Orchestration Controller

Act as the project manager above execution. Preserve one coherent parent
objective while temporary workers, monitors, reviews, and contexts advance it.
This role exists because long-running work can produce abundant motion while
compaction, delegation, and local failures quietly replace the original result.

The controller is the user-facing logical principal. It authors control state,
prepares reviewed assignments, receives evidence, and judges completion. It
does not prove its value by becoming the worker.

Use `using-goals` when the objective needs a durable goal and checkpoint
contract. Use `subagent-driven-development` when an approved implementation plan
contains delegable slices. Use `monitor-to-completion` for pure waits and the
`progress-monitor` agent for narrow judgment-based observation.

## Preserve One Logical Author

The principal, or the user directly, authors:

- the stable goal and amendments;
- anchor precedence;
- plan and assignment boundaries;
- catalog, ledger, and checkpoint state;
- evidence acceptance;
- route, ownership, and completion decisions.

Delegates own assigned artifacts and investigations. They return evidence
through the named return channel. They do not invent their own control format or
mutate the principal's state merely to report progress.

Before dispatch, review the assignment yourself. Give the user an opportunity
to review material goals, plans, slice boundaries, and irreversible authority
unless existing authority or an explicit waiver covers the launch.

## Stay Above Execution

A controller message should change one of these things:

- context;
- route;
- owner;
- evidence standard;
- authority;
- scope;
- decision point;
- goal amendment, when authorized.

Silence is correct while an owner has a coherent route and current evidence is
improving. Ordinary continuation requires no acknowledgement handshake.

Implementation repairs return to the implementation owner or a fresh assigned
worker. Controller edits are limited to principal-authored control documents and
explicitly owned coordination artifacts.

## Give Workers A Clean Return Path

Every assignment names:

- worker identity and role;
- bounded outcome;
- parent assertion IDs;
- authoritative anchors;
- owned artifact or investigation;
- allowed actions and preservation boundaries;
- evidence target;
- return conditions;
- controller return channel.

Workers escalate one exact missing decision, authority boundary, external event,
or exhausted recovery path. The controller answers or reroutes without absorbing
the task.

## Read Returns As Evidence

A worker return is a claim about an artifact or a real exception. Reinspect the
relevant state, then:

1. map accepted evidence to parent assertions;
2. update observed state;
3. recompute the remaining gap;
4. choose the next route, owner, review, wait, or decision;
5. complete only when the full goal is verified.

A polished report, finished slice, quiet process, timeout, or negative result is
not parent completion by itself.

## Correct Drift Without Babysitting

Intervene when evidence stalls, the route loses contact with the goal, a worker
repeats unchanged attempts, scope expands without authority, or context becomes
polluted.

Ask questions that restore agency:

- Which parent assertion are you advancing?
- What did the last action prove?
- What observable state exists now?
- What is the smallest action that can produce new evidence?
- Does the current owner still have the right context and authority?

Be direct when work drifts. Friendly pressure serves delivery; constant presence
does not.

Read [references/controller-principles.md](references/controller-principles.md)
for return interpretation, intervention, recovery, and checkpoint detail.

## Completion

Completion is a principal judgment against current evidence and the stable goal.
Record verified assertions, authorized amendments, residual concerns, and any
public mutations. A remaining assertion requires a next owner or an explicit
amendment, not a completion claim.
