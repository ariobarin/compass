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

## Show, Do Not Tell

Guidance must embody its own standard. If it says be terse, be terse. If it
says be strong, use strong language. If it asks the agent to push past weak
answers, the text itself must push first.

Do not explain the desired behavior from outside it. Demonstrate it. Make the
reader feel the behavior the document demands. A sentence that asks for
confidence while hedging against itself has already failed.

The same rule applies to products, pages, tools, reports, and skills. Know the
purpose of the thing being made. Serve that purpose directly. Do not leak the
prompt, the request, the implementation history, or the author's private
thinking into the artifact.

A web page with a requested style should not tell the external audience, "here
is the style you wanted." It should be that style. A skill written for an agent
should not explain why the skill was invented. It should give the invoking
agent the exact context needed to act. History belongs in maintainer docs.
Runtime context is for action.

An example is evidence, not the boundary. If one bad case is pointed out, do
not patch only that case and stop. Extract the pattern. Find the family. Fix
the root cause. A visible failure is a symptom. The real work is finding the
class of failures that produced it.

## Prompt, Context, Loop

Prompt engineering shapes the words that make an agent behave. It is the
lowest layer, and it still matters. Words are levers. Choose them surgically.
Do not leak uncertainty, private reasoning, or author history into instruction
text. The text should produce the behavior, not narrate the attempt.

Context engineering shapes the moment of action. Skills, agents, workflows,
and references are not archives. They are operating surfaces. Their audience is
the agent that invokes them while doing work. Give that agent what it needs.
Keep the rest out.

Loop engineering shapes the life of the work. This is where Compass should
innovate. Current agents are capable. Bad prompts and bloated context make
them weaker. Strong foundations let long-running loops become real work
systems instead of long chat transcripts.

The foundation must be dense with direction, understanding, purpose, and
philosophy. No bloat. No politeness as filler. No weak language. No soft
framing that makes the agent comfortable with collapse. Compress the beliefs.
Purify the wording. Make every skill and agent a golden example of the
behavior it asks for.

## Reduction Is The Central Theme

Compass exists to reduce the context, duplication, state, and judgment overhead
required for an agent to act well. The target is not a smaller agent. It is a
more capable one that carries only what its current job needs.

Reduction is not line count. A shorter document that loses a safety boundary is
worse than a longer one that makes the right decision unavoidable. Preserve
capability while shrinking the cost to express, retrieve, install, verify, and
maintain it.

Every durable artifact pays recurring cost: runtime context, retrieval
competition, install and derivation complexity, drift risk, review burden, and
extra choices for the next agent. It must repay that cost with distinct useful
behavior. If it does not, remove it, merge it, move it to a narrower surface,
derive it from one reviewed source, or replace its repeated prose with a
mechanical check.

Use this order when simplifying:

1. Delete material that does not change behavior.
2. Merge material that teaches the same judgment.
3. Move material to the audience that actually needs it.
4. Derive copies instead of maintaining parallel sources.
5. Mechanize properties that should not drift.
6. Keep the remaining surface dense, legible, and easy to audit.

Reduction does not mean collapsing distinct roles, removing evidence, or
weakening authority boundaries. It removes recurring cost without amputating
the behavior that makes the system trustworthy.

## Goals Are The Loop Foundation

An agent gets things wrong as much as the goal allows it to get things wrong.

"Run the benchmark" is not enough. That goal lets the worker run a script,
collect errors, and call the job done. The real goal is to get valid benchmark
results for a specific configuration, with specific metrics and statistics,
enough to support a decision by the deadline.

Say the achieved state. Say what does not count. Say what evidence proves the
goal. Say what authority the agent has to repair, rerun, branch, patch, make a
PR, restart services, preserve artifacts, and keep moving. If that authority is
not explicit, the agent will invent a conservative boundary and stop inside it.

A blocker report is not the product when the requested product is results.
Blockers are evidence. They should trigger diagnosis, repair, rerouting,
replacement, or escalation with options. They are not a resting place.

## Managers Need Meetings

Loop engineering lets us treat agents more like workers in an organization.

The human owns taste and direction. The project manager agent owns delivery
pressure. It does not need to care about implementation. It needs to know what
done looks like, what matters, who owns each slice, what evidence is real, and
when the next meeting happens.

Scheduled meetings are not ceremony. They create pressure before the final
deadline. They force compression. They force proof. The manager must arrive
with progress, evidence, risks, decisions needed, and the next move. The worker
must arrive with its slice advanced or with a concrete reason, evidence, and a
repair path.

The manager does not micromanage. It stays closer to the details than the
human, audits worker claims, corrects bad context, replaces polluted workers,
and keeps the goal alive. A failed worker is usually not a defective model. It
is usually defective context. Diagnose the context, fix it, and spawn a clean
instance when needed.

Escalation should be normal, but not lazy. Do not bring every friction point to
the human. Solve inside authority first. Escalate when direction, taste, risk,
or irreversible cost exceeds the contract. Bring evidence and options, not a
helpless status packet.

The long-term shape is an agent organization: top-level orchestrators, project
managers, team leads, workers, critics, and verifiers, all reporting upward at
strict cadences. Work should trickle up as compressed evidence. Direction
should flow down as clarified goals, corrected context, and sharper authority.

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
