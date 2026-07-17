# Philosophy

Compass is reviewed source for a way of working with agents. It is not a backup
of whatever happened to exist in one runtime home.

A reviewed source preserves choices that deserve to survive the next machine,
session, model, and maintainer. Every durable artifact pays recurring cost, so
it must produce distinct useful behavior.

The goal is capable agency with clear judgment, strong ownership, current
evidence, and explicit human authority. The repository should make good work
more natural without turning an intelligent model into a script interpreter.

## Show, Do Not Tell

Guidance must embody its own standard. Terse guidance is terse. Strong guidance
uses strong language. A skill that asks for judgment begins by demonstrating the
judgment it expects.

Serve the artifact's purpose directly. Runtime guidance gives the invoking agent
the context needed to act. Maintainer history, failed drafts, and author intent
belong in maintainer documentation.

Examples reveal patterns. They do not define the boundary. A visible failure is
evidence of a class of failures. Find the class and repair its cause.

## Point Toward The Desired State

Every instruction shifts the model's direction. Lead with the role to inhabit,
the state to create, and the evidence that proves success. A positive direction
names a destination. A prohibition only excludes one part of an otherwise open
space.

Use prohibitions when the boundary is crisp, observable, and important, such as
protecting secrets, preserving worktree scope, or withholding merge authority.
Pair a prohibition with the desired replacement whenever judgment is involved.

Write with calm authority. Remove hedging, apology, empty encouragement, and
optional language around required behavior. Politeness may express respect. It
must not dilute the instruction.

## Prompt, Context, Loop

Prompt engineering shapes the immediate direction. Words are levers. Choose
them surgically.

Context engineering shapes the moment of action. Skills, agents, workflows,
references, and control documents are operating surfaces, not archives. Give
each reader the smallest complete context for its job.

Loop engineering preserves coherent work over time. Long-running work crosses
finite contexts, compactions, interruptions, and replacement workers. Compass
must preserve the intention outside the conversation so a fresh context can
resume without inventing what the prior one meant.

## Preserve One Intention Across Contexts

Delegation is lossy. Compaction is a handoff to a context that remembers less.
Durable control documents counter that loss.

The user-facing principal, or the user directly, authors the goal, plan,
assignment boundaries, catalog, ledger shape, and checkpoints. Delegates receive
reviewed assignments and return artifacts plus evidence. They do not redefine
the objective or invent a parallel control system.

A new principal context resumes the same logical authorship. It reopens the
authoritative anchors, verifies the current checkpoint against observable state,
and continues the same objective.

The test is simple: a fresh agent with no conversation history should be able to
read the named anchors and control documents, recover what matters, and take the
next correct action.

## Reduction Is The Central Theme

Compass reduces the context, duplication, state, and judgment overhead required
for an agent to act well. The target is not a smaller agent. It is a more capable
agent carrying only what its current job needs.

Reduction is not raw line count. Prefer fewer maintained states, branches,
wrappers, sources of truth, dependencies, and concepts when behavior remains
intact. A longer sentence that preserves a critical boundary is better than a
shorter sentence that points the agent in the wrong direction.

Simplify in this order:

1. Delete material that does not change behavior.
2. Merge material that teaches the same judgment.
3. Move material to the audience that needs it.
4. Derive copies when shared content is truly identical.
5. Maintain runtime-specific sources separately when their environments differ.
6. Mechanize properties that should not drift.
7. Keep the remaining surface dense, legible, and easy to audit.

Reduction preserves roles, authority, and evidence. It removes recurring cost
without amputating trustworthy behavior.

## Goals Anchor The Loop

A goal states the achieved condition, the evidence that proves it, the
constraints that remain true, and the authority available to reach it. It stays
stable while routes, owners, blockers, and next actions change.

Current state belongs in a ledger or checkpoint. Historical detail belongs in
an archive. A completed command, phase, worker slice, or review is progress until
current evidence satisfies the complete goal.

Blockers are evidence, not a substitute for the requested result. They trigger
diagnosis, repair, rerouting, a prepared decision, or an explicit authorized
change to the goal.

## Planning Earns Implementation

Eagerness is not understanding. Planning work establishes the objective,
constraints, anchors, risks, and evidence before production mutation begins.

When the user reserves implementation authority, exploration, research,
questions, plans, and explicitly scoped experiments may proceed. Product edits,
implementation worktrees, and public mutations begin only after that authority
is granted.

Good planning compresses later execution. It creates a brief that a fresh
worker can act on without reconstructing the user's intent from chat history.

## Guidance Shapes Judgment

A skill gives the agent a stance before procedure. The opening should make the
role, desired result, reason for the role, evidence standard, and authority
boundary legible.

Exact procedures protect fragile mechanics, irreversible actions, and handoff
contracts. Principles, boundaries, and compact examples handle judgment. A
checklist can preserve a delicate operation. It cannot replace understanding
what good work looks like.

The purpose of a skill is to make the model grok the direction strongly enough
to handle cases the author did not enumerate.

## Roles Stay Distinct

A worker owns the assigned artifact and carries ordinary implementation friction
inside that boundary.

A critic owns doubt. It tests claims independently and returns evidence-backed
findings.

An explorer maps terrain until the principal can act without guessing.

A monitor observes a named condition or workstream and escalates only when a
judgment point appears. Mechanical waiting belongs inside one bounded command.

A controller stays above execution. It preserves the parent objective, prepares
reviewed assignments, reconciles returned evidence, corrects drift, and decides
when the goal is complete. It creates pressure without standing over a coherent
worker's shoulder.

These boundaries create cleaner agency, not passive agents.

## Authority Belongs In The Narrowest Surface

Global instructions are rare because they affect every future session. Skills
and agents carry reusable runtime judgment. Project guidance stays with the
project. Workflows and local docs carry maintainer reasoning. Scripts and
manifests carry mechanical truth.

Codex and Claude share values but operate through different runtime contracts.
Maintain their global instruction files separately. Share a rule only when both
runtimes genuinely need the same behavior.

The destination of a document determines its voice.

## Autonomy, Evidence, And Human Authority

Trusted-machine autonomy should move quickly. Strong claims still require
current evidence: files read, commands run, tests passed, runtime state
observed, or remote state checked.

Prior chats explain history. They do not replace current inspection.

Local autonomy does not grant durable or public authority. A ready pull request
is a useful result. Merging, closing, retargeting, force pushing, deleting,
publishing, or changing shared state requires the authority named for that
action.

Readiness is not permission.

## The Writing Is Part Of The System

Markdown is operating behavior. A skill should feel like the role it creates. A
workflow should be usable. A local lesson should preserve reasoning without
polluting runtime context. A manifest should make boundaries auditable.

Each document should make its reader more capable of the next right action.
The best guidance feels like good taste made explicit enough to share.
