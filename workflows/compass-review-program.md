# Compass Review Program

Use this workflow when auditing Compass itself: installed skills, agents, hooks,
maintainer docs, workflows, manifests, scripts, and reviewed config. The work is
slow by design. Do not one-shot the repo.

This is repo-maintainer guidance. It is not installed into a live Codex home,
user skill home, or Claude home.

## Purpose

Compass is the configuration of the configuration. If agents are led astray
while maintaining this repo, the first suspect is Compass itself.

The job is to make the setup night and day better than vanilla Codex, not a
little better. That starts with understanding. A fresh agent begins with no
project memory, no lived history, and no implicit taste. The repo must implant
the right ideas quickly, without bloat, weak language, or distracting context.

Review is not cleanup theater. Review asks what each surface is for, who reads
it, what they need at that moment, and what can be cut or moved without behavior
loss. If pruning preserves behavior or improves behavior, the removed text was
probably for the wrong audience or carried weak signal.

## Review Stance

Understand first. Cut second.

Do not begin by rewriting. Read the target surface, name its runtime or
maintainer audience, and state the job it must perform. Then decide what
belongs, what distracts, what should move, and what should disappear.

Examples are symptoms. If one skill leaks history, look for history leakage in
nearby skills. If one workflow dilly-dallies around its point, look for the
same weakness in related docs. If one global skill looks project-specific, check
the installed set, the manifest, the Claude mirror, and the retirement path.

## Inventory Pass

Before editing a family of files, create a compact inventory. Use current files
as authority. Start from `local-docs/compass-surface-inventory.md` when it is
present, and read `local-docs/compass-review-state.md` when continuing the
existing review program. Update the inventory only when the map changes.

Classify each item as one of:

- runtime context: installed agentic behavior under `codex/AGENTS.md`,
  `codex/agents/`, or `codex/skills/` (the Claude surface derives from these);
- maintainer context: repo-only guidance under `AGENTS.md`, `workflows/`,
  `local-docs/`, `manifests/`, or `scripts/`;
- mechanical truth: scripts, manifests, checks, and reviewed config fragments;
- historical evidence: failure journals and maintenance learnings;
- carried but not global candidate: useful material that should travel in this
  repo but should not be installed for every session;
- stale or removal candidate: text or files that no longer justify their cost.

For each item, record:

```text
Path:
Audience:
Purpose:
Must preserve:
Possible cuts:
Move candidates:
Global-install justification:
Evidence to inspect:
Recommended PR:
```

Keep the inventory short. It is a decision tool, not a second repo.

## Runtime Surface Audit

Installed runtime context must speak to the agent using it while doing work.

Ask:

- Who invokes this, and in what state?
- What must the agent understand in the first screen?
- What exact behavior should the text produce?
- What authority does the agent have?
- What must not be decided by this agent?
- What evidence proves done?
- What text explains history instead of producing action?
- What phrasing makes failure, waiting, fallback, or drift feel acceptable?
- What could be moved to maintainer docs with no runtime loss?

Cut provenance, dated observations, packaging explanation, stale caveats, owner
intent, and maintainer reasoning from runtime context. Keep the role, stance,
non-negotiables, boundaries, evidence standard, and fragile procedure.

## Hook Surface Audit

Hooks are installed runtime behavior, not agent prose. Audit them as mechanical
guards.

Ask:

- What event invokes this hook?
- What does the hook add, deny, or block?
- Does it fail open or fail closed, and is that correct for the event?
- What exact guard module handles the behavior?
- What doctor test proves the portable copy works?
- Does hook-local documentation explain trust review and disablement?
- Is this better as a hook than a skill, agent, script, or local workflow?

Keep hook behavior narrow. Put broad judgment in skills, agents, or workflows.
Hook PRs should include the hook definition, guard module, hook-local docs, and
doctor tests.

## Maintainer Surface Audit

Maintainer docs should make Compass easier to change without bloating runtime
context.

Ask:

- Does this help a future maintainer understand why the repo is shaped this way?
- Does it route a decision to the right surface?
- Does it preserve history that would distract a runtime agent?
- Does it explain a mechanical check, install boundary, or promotion path?
- Does it make the next PR smaller and safer?

Maintainer docs may hold history. They should not become dumping grounds. Keep
history only when it changes a future maintenance decision.

## Skill Set Audit

Every installed skill pays rent. Being useful once is not enough.

For each global skill, ask:

- Is this reusable across repos or workflows?
- Does it need to be retrieved during ordinary Codex work?
- Is it project-specific, benchmark-specific, or temporary?
- Could it live as repo-carried but not globally installed material?
- Does it overlap another skill enough to fold?
- Does its Claude mirror still match the intended behavior?
- Do manifests, installer logic, retired maps, and docs agree?

Do not delete useful material just because it is not global. Move it to a
carried-but-not-global area only after the route exists and the install map,
docs, and retirement behavior are clear.

## Pruning Standard

Cut text when cutting it does not weaken the behavior. Cut harder when cutting
it strengthens the behavior.

Good pruning removes:

- audience mismatch;
- author history in runtime context;
- alternate paths for Compass-owned capabilities;
- compatibility prose without a current compatibility need;
- repeated explanation that hides the first action;
- soft wording that makes collapse acceptable;
- examples that became the boundary instead of teaching the pattern;
- lists that replace judgment without preserving a fragile operation.

Do not equate shorter with better. Dense is better. Exact is better. A small
sentence that points the agent the wrong way is worse than a longer sentence
that makes the right behavior unavoidable.

## PR Rhythm

Use focused PRs. The review program should create pressure and evidence, not
one giant rewrite.

Good PR boundaries:

- add or revise the audit rubric;
- inventory one family;
- prune one skill or one closely related skill family;
- move one project-specific capability out of global install;
- add a check that prevents a repeated drift;
- update maintainer docs after a runtime cleanup.

The review artifact should say:

- what surface was reviewed;
- what audience it serves;
- what was cut, moved, or preserved;
- what behavior should change;
- what commands or source inspection verified the change.

Keep the PR body consistent with repo convention: short, motivation-first, and
without headers or checklists. Put detailed evidence in the audit packet, local
doc, final report, or review comment that travels with the PR.

Run `.\scripts\doctor.ps1` before committing. Run skill validation for skill
edits when available. Run `.\scripts\verify-live.ps1 -SkipCodexCommand` when
live drift matters.

## Review Gate

Green draft PRs are build evidence. They are not readiness.

Before calling a Compass review-program PR ready, inspect the live PR state:
base branch, head branch, head SHA, check results, review status, and open
comments. For stacked PRs, verify every base points at the intended previous
head and name the merge order.

Use `pr-review-loop` for the final review path. Local checks and GitHub checks
support readiness, but they do not replace current-head review gates. After any
material push, re-read the head SHA and make sure required reviewers are looking
at that SHA before marking the PR ready.

If the current session lacks authority to invoke a required reviewer, stop at
that gate and name it as unsatisfied. Do not self-review, count a local check as
review, or keep stacking PRs as if review happened. Ask for the authority or an
explicit approved reviewer route.

## Stop Conditions

Stop and ask for user taste when the decision changes the system's philosophy,
removes a valued capability, narrows global behavior in a way that may affect
ordinary work, or chooses between two plausible directions with different
values.

Do not stop for routine cuts, stale wording, missing links, or obvious audience
mismatch. Make the narrow PR and preserve evidence.
