# Subagent Pruning Audit

This audit compares `subagent-driven-development` with
`orchestration-controller` before pruning either skill. It follows the Queue 2
recommendation in `local-docs/loop-governance-skills-audit.md`.

No runtime skill text changes in this audit. The job is to define the next
runtime edit precisely enough that pruning strengthens behavior instead of
flattening the two skills into one vague controller surface.

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
- `orchestration-controller/references/controller-principles.md`: 164
- `subagent-driven-development/SKILL.md`: 145
- `subagent-driven-development/implementer-prompt.md`: 69
- `subagent-driven-development/spec-reviewer-prompt.md`: 30
- `subagent-driven-development/code-quality-reviewer-prompt.md`: 28

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

Recommended edit:

- Keep a short first-screen statement that the controller owns sequencing,
  review, and integration while implementers own execution.
- Keep direct pressure that `DONE` and `BLOCKED` are not endpoints until
  evidence is checked.

### S2: Preserve the prompt templates

The three prompt templates are not bloat. They carry executable contracts:

- implementer owns ambiguity before asking;
- implementer reports one status with evidence;
- spec review happens before quality review;
- reviewers treat reports as hints, not evidence;
- diff locators and repo paths are required before review.

This is the part of the skill that prevents hand-rolled dispatch text from
weakening the loop.

Recommended edit:

- Leave the template files in place.
- Do not fold them into `SKILL.md`.

### S3: Prune repeated blocker questions only where they stop adding force

`subagent-driven-development` repeats the same blocker pressure in three places:

- task dispatch status requirements;
- worker signal handling;
- implementer prompt escalation rules.

The repetition is partly useful because each location is a different boundary:
controller dispatch, controller interpretation, and worker report. The risky
part is not repetition itself. The risky part is adding words after the point is
already clear.

Recommended edit:

- Keep the strict `BLOCKED` contract in the implementer prompt.
- Keep the task dispatch rule that requires concrete status and evidence.
- Compress `Worker Signals` so it routes statuses without restating the whole
  blocker investigation.

### S4: Replace fallback-shaped wording

The phrase `review fallback` appears in `Wait Discipline` and `Useful Pairings`.
The problem is not that exact word by itself. The problem is that the phrase
makes orchestration sound like a backup path after same-session implementation
fails.

That is the wrong model. When the work becomes routing, monitoring, review, or
completion-gate enforcement, the system has changed levels. It should route to
`orchestration-controller` because that is the primary owner for that level.

Recommended edit:

- Replace `review fallback` with level language such as `review routing` or
  plain `review`.
- Say the controller should route to `orchestration-controller` when the work
  stops being same-session implementation sequencing.

### S5: Keep checkout-safety wait rules in the subagent skill

Some wait rules overlap the controller skill, but the checkout-safety rules are
specific to same-session subagents:

- keep parent work read-only while an active child may touch the shared
  checkout;
- edit shared files only after accounting for the child;
- hold a reviewed diff at its gate while a long reviewer is still running.

Those are not generic orchestration rules. They belong in the subagent skill.

Recommended edit:

- Preserve shared-checkout safety.
- Prune only generic passive-waiting language that `orchestration-controller`
  already owns more directly.

### S6: Keep the Claude mirror paired with the Codex source

The Claude mirror differs from the Codex source only in the useful-pairings
section: it generalizes the Codex-only `using-codex-goals` reference into a
durable goal contract.

Recommended edit:

- Apply future pruning to both `codex/skills/subagent-driven-development` and
  `claude/skills/subagent-driven-development`.
- Preserve the one runtime-specific difference around goal wording.

## Next PR Boundary

Make one runtime pruning PR:

- edit `codex/skills/subagent-driven-development/SKILL.md`;
- edit `claude/skills/subagent-driven-development/SKILL.md` in step;
- do not edit prompt templates unless the pruning exposes a concrete contract
  problem;
- do not edit `orchestration-controller` unless the subagent edit reveals a
  missing route;
- run skill validation for both skill dirs and `.\scripts\doctor.ps1`.

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
git diff --no-index -- codex\skills\subagent-driven-development\SKILL.md claude\skills\subagent-driven-development\SKILL.md
rg -n -i "control plane|worker|BLOCKED|DONE|review fallback|fallback|restore agency|runner|same-session|implementation fan-out|fresh|controller|status claims" codex\skills\orchestration-controller codex\skills\subagent-driven-development
```
