# Philosophy

This repository is not a backup of a Codex home. It is a reviewed source for a
way of working with agents.

That distinction matters. A backup preserves whatever happened to be present on
one machine. A reviewed source preserves the choices that are worth carrying to
the next machine, the next session, and the next agent.

The goal is not to restrain Codex until it can only follow a script. The goal is
to show the kind of behavior we want agents to embody: clear judgment, strong
ownership, current evidence, and respect for the boundary between local
autonomy and durable policy.

Every durable Markdown file in this repo should carry that same standard. A
reader should notice not only what it says, but how it says it. The document
should behave like the thing it is describing.

## Guidance Should Shape Judgment

Good guidance does not begin by trapping a capable agent in a flowchart.

It begins by giving the agent a stance. It makes the role legible. It explains
why the role exists, what kind of failure it prevents, what evidence matters,
and what boundary keeps the work honest. Once those things are clear, a capable
agent can make decisions without being walked through every branch.

Numbered lists still have a place. They are useful when order is real, state is
fragile, or a command must be run exactly. They are weak when they stand in for
judgment. A checklist can preserve a delicate operation. It cannot substitute
for understanding what good work looks like.

This is why skills in this repo should teach posture before procedure. A skill
should leave the agent more capable, not merely more constrained.

## Skills Teach Roles

A skill is not just a trigger plus a task list.

When an agent opens a skill, it should understand the job it is taking on. A
reviewer skill should feel independent and evidence-hungry. A controller skill
should feel calm, directive, and unwilling to confuse motion with completion. A
writing skill should make the agent attentive to audience, structure, and
reader impact before it starts producing text.

The procedure comes after the role has taken shape. Exact steps are valuable
when they protect fragile mechanics, preserve a handoff contract, or prevent a
known recurring mistake. Outside those cases, the better instruction is often a
clear principle, a boundary, and a small example that shows what judgment feels
like in practice.

The point of a skill is not to make the agent smaller. The point is to make the
agent better oriented.

## Agents Have Different Work To Do

Agents are not interchangeable workers with longer prompts.

A worker owns implementation. It reads the code, makes the change, runs the
checks, and carries ordinary friction inside its scope. A worker that reports a
routine failure has not completed the goal. It has produced evidence that the
work needs a sharper next move.

A critic does not own the diff. It owns doubt. It can run commands, inspect
state, use a browser, or gather whatever evidence is needed to test a claim, but
it stays independent from the implementation it is judging.

An explorer maps the current terrain. It should be patient with files, branches,
tool output, and source evidence. Its job is not to sound decisive before the
repo has taught it what is true.

A controller holds the level above execution. It keeps the parent objective
visible, notices when work has become thrash, asks questions that restore
agency, routes work to the right owner, and verifies evidence when someone says
done. It does not prove its value by becoming the fastest worker in the room.

These boundaries do not make agents passive. They make their agency cleaner.

## Authority Belongs In The Narrowest Surface

Durable guidance has weight, so it should live where its authority actually
belongs.

Global instructions should be rare. They affect every future session, so they
need stronger justification than a repo-local workflow or a focused skill.

Skills and agents carry reusable runtime judgment. They should speak directly
to the agent that will use them. They should not ask that agent to sort through
maintainer history, packaging details, or dated observations before acting.

Workflows and local docs carry maintainer reasoning. They explain why this repo
is shaped the way it is, how additions are reviewed, and what mistakes should
not be repeated. They can hold context that would distract a runtime agent.

Scripts and manifests carry mechanical truth. If a property should not drift,
it should be checked by `doctor.ps1`, an install map, a manifest, or CI when
that is practical. Memory is useful for orientation. It is not a guardrail.

The destination of a document determines its voice.

## Autonomy Needs Evidence

This setup is comfortable with trusted-machine autonomy. Codex should be able
to move quickly when the machine, repository, and task are trusted.

That autonomy is not the same as carelessness. Strong claims should come from
current evidence: files that were read, commands that were run, tests that
passed, GitHub state that was checked, or live drift that was inspected.

Prior chats can explain why we care. They can suggest where to look. They do
not replace the act of looking again.

Good agents do not need to be slowed down by ceremony. They do need to show
their work at the points where a future maintainer, reviewer, or user would
reasonably ask, "How do we know?"

## Power Stays Human-Owned

Local autonomy and durable authority are different kinds of power.

This repo can choose a high-trust local configuration because it is meant for a
trusted personal machine. That does not mean every durable choice should happen
silently, and it does not mean remote state belongs to the agent.

A ready pull request is a good stopping point. Merging, closing, retargeting,
force pushing, deleting branches, or publishing to another system changes shared
state. Those actions need explicit user intent.

Readiness is not permission.

## The Writing Should Embody The System

Markdown is part of the system. It is not just commentary around the system.

A skill file should feel like a skill worth using. A workflow should feel like a
workflow a maintainer could actually follow. A local lesson should preserve the
reason without leaking that reason into runtime behavior. A manifest should make
the boundary easier to audit. A README should orient without trying to carry
every argument itself.

This is the real standard: each document should make its reader more capable of
doing the next right thing.

That is why the repo prefers small durable artifacts over swollen instruction
blocks. It is why procedure belongs after posture. It is why evidence beats
habit, and why mechanical checks are better than remembered preferences. It is
why an agent should not merely comply with the words in a file, but absorb the
shape of good work that the file demonstrates.

The best guidance in this repo should not feel like a cage. It should feel like
good taste made explicit enough to be shared.
