# Subagent Pruning Audit

This audit packet compares `subagent-driven-development` with
`orchestration-controller`. It follows the loop-governance recommendation in
`local-docs/loop-governance-skills-audit.md` and records the runtime pruning
that followed.

Packet status:

- Refreshed after the subagent runtime pruning follow-up landed.
- Use current subagent skill sources, orchestration-controller sources, Claude
  mirrors, manifest state, and open PR stack state before deriving new work
  from this packet.
- Treat verification commands as audit history, not current proof.

The job is to keep the pruning decision reviewable: pruning should strengthen
behavior instead of flattening the two skills into one vague controller surface.

## Surfaces Reviewed

Codex source:

- `codex/skills/orchestration-controller/SKILL.md`
- `codex/skills/orchestration-controller/references/controller-principles.md`
- `codex/skills/subagent-driven-development/SKILL.md`
- `codex/skills/subagent-driven-development/implementer-prompt.md`
- `codex/skills/subagent-driven-development/spec-reviewer-prompt.md`
- `codex/skills/subagent-driven-development/code-quality-reviewer-prompt.md`

Claude mirror:

- `claude/skills/subagent-driven-development/SKILL.md`

Line counts inspected:

- `orchestration-controller/SKILL.md`: 80
- `orchestration-controller/references/controller-principles.md`: 210
- `subagent-driven-development/SKILL.md`: 182
- `subagent-driven-development/implementer-prompt.md`: 94
- `subagent-driven-development/spec-reviewer-prompt.md`: 46
- `subagent-driven-development/code-quality-reviewer-prompt.md`: 40
- `claude/skills/subagent-driven-development/SKILL.md`: 182

## Audience Split

`orchestration-controller` speaks to a controller overseeing workers, threads,
monitors, reviews, and long-running work. Its job is to preserve level: the
controller owns contract, cadence, routing, evidence checks, and completion
judgment.

`subagent-driven-development` speaks to the same controller only when a plan
already exists and same-session implementation fan-out is the right shape. Its
job is narrower: dispatch implementers, preserve task boundaries, sequence
review, and integrate results without becoming the worker.

That split is valid. The subagent skill should not be demoted, and it should not
be collapsed into generic orchestration. It earns global context because it
turns a common plan-to-implementation workflow into a repeatable loop with
fresh workers and staged review.

## Findings

### S1: Keep the first-screen control pressure

Both skills say the controller should make workers effective without becoming a
worker, and both treat `DONE` and `BLOCKED` as claims to verify. This overlap is
intentional in the first screen of `subagent-driven-development`: an agent that
retrieves that skill needs the controller stance before it dispatches workers.

Do not prune that pressure just because `orchestration-controller` also says
it. The subagent skill would get weaker if its first screen became only task
mechanics.

Current state:

- The first screen says this is a controller skill for implementation fan-out.
- It keeps direct pressure that `DONE` and `BLOCKED` are not endpoints until
  evidence is checked.
- It preserves the split: the controller owns sequencing, review, and
  integration while implementers own execution.

### S2: Preserve the prompt templates

The three prompt templates are not bloat. They carry executable contracts:

- implementer owns ambiguity before asking;
- implementer reports one status with evidence;
- spec review happens before quality review;
- reviewers treat reports as hints, not evidence;
- diff locators and repo paths are required before review.

This is the part of the skill that prevents hand-rolled dispatch text from
weakening the loop.

Current state:

- The template files remain in place.
- They were not folded into `SKILL.md`.

### S3: Prune repeated blocker questions only where they stop adding force

`subagent-driven-development` repeats the same blocker pressure in three places:

- task dispatch status requirements;
- worker signal handling;
- implementer prompt escalation rules.

The repetition is partly useful because each location is a different boundary:
controller dispatch, controller interpretation, and worker report. The risky
part is not repetition itself. The risky part is adding words after the point is
already clear.

Current state:

- Keep the strict `BLOCKED` contract in the implementer prompt.
- Keep the task dispatch rule that requires concrete status and evidence.
- `Worker Signals` routes statuses directly and sends `BLOCKED` through
  diagnosis instead of treating it as a normal lane.

### S4: Level routing replaced fallback-shaped wording

The old phrase made orchestration sound like a backup path after same-session
implementation failed.

That is the wrong model. The current text routes to
`orchestration-controller` when the work changes level and becomes routing,
monitoring, review, or completion-gate enforcement.

Current state:

- Codex and Claude route level changes to `orchestration-controller`.
- The old backup-path wording is absent from both runtime skills.

### S5: Keep checkout-safety wait rules in the subagent skill

Some wait rules overlap the controller skill, but the checkout-safety rules are
specific to same-session subagents:

- keep parent work read-only while an active child may touch the shared
  checkout;
- edit shared files only after accounting for the child;
- hold a reviewed diff at its gate while a long reviewer is still running.

Those are not generic orchestration rules. They belong in the subagent skill.

Current state:

- Preserve shared-checkout safety.
- Keep parent work read-only while a still-active child may touch the shared
  checkout.
- Move the parent only when it can still move without corrupting the shared
  checkout.

### S6: Keep the Claude mirror paired with the Codex source

The Claude mirror differs from the Codex source only in the useful-pairings
section: it generalizes the Codex-only `using-codex-goals` reference into a
durable goal contract.

Current state:

- Codex and Claude `subagent-driven-development` were pruned in step.
- The runtime-specific difference around goal wording remains: Codex names
  `using-codex-goals`; Claude uses durable goal contract wording.

## Completed PR Boundary

Follow-up status:

- Completed by the runtime pruning PR. Codex and Claude
  `subagent-driven-development` were pruned in step, prompt templates stayed in
  place, and fallback-shaped routing was replaced with level language.

The completed runtime pruning PR changed these files:

- `codex/skills/subagent-driven-development/SKILL.md`;
- `claude/skills/subagent-driven-development/SKILL.md`.

It left prompt templates and `orchestration-controller` unchanged.

Expected behavior change:

- agents should still retrieve `subagent-driven-development` for same-session
  implementation fan-out;
- agents should reach the dispatch and review contract faster;
- agents should route to `orchestration-controller` as the primary owner when
  the work changes level, not as a fallback.

## Verification

Commands used while preparing this audit:

```powershell
Get-Content -Raw codex\skills\orchestration-controller\SKILL.md
Get-Content -Raw codex\skills\orchestration-controller\references\controller-principles.md
Get-Content -Raw codex\skills\subagent-driven-development\SKILL.md
Get-Content -Raw codex\skills\subagent-driven-development\implementer-prompt.md
Get-Content -Raw codex\skills\subagent-driven-development\spec-reviewer-prompt.md
Get-Content -Raw codex\skills\subagent-driven-development\code-quality-reviewer-prompt.md
Get-Content -Raw claude\skills\subagent-driven-development\SKILL.md
(Get-Content codex\skills\orchestration-controller\SKILL.md).Count
(Get-Content codex\skills\orchestration-controller\references\controller-principles.md).Count
(Get-Content codex\skills\subagent-driven-development\SKILL.md).Count
(Get-Content codex\skills\subagent-driven-development\implementer-prompt.md).Count
(Get-Content codex\skills\subagent-driven-development\spec-reviewer-prompt.md).Count
(Get-Content codex\skills\subagent-driven-development\code-quality-reviewer-prompt.md).Count
(Get-Content claude\skills\subagent-driven-development\SKILL.md).Count
rg -n -i "review fallback|fallback|review routing|orchestration-controller|Worker Signals|BLOCKED|DONE|same-session|implementation fan-out|shared checkout|goal contract|using-codex-goals" codex\skills\subagent-driven-development claude\skills\subagent-driven-development codex\skills\orchestration-controller
```
