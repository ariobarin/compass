# Agent Failure Journal

Use this file to convert repeated agent mistakes into targeted workflow changes.
Do not add global rules for one-off failures. Record enough detail to identify
the first upstream failure and decide whether the fix belongs in instructions,
a skill, a script, a test, or repo documentation.

This is repo-maintainer guidance and is not installed into a live Codex home,
user skill home, or Claude home.
When a failure should change future agent behavior, route the fix into
installed Codex guidance under `codex/AGENTS.md`, `codex/agents/`, or
`codex/skills/`, or installed Claude guidance under `claude/agents/` or
`claude/skills/`.

## Entry Template

```text
date:
repo or workflow:
task:
first failure:
downstream effects:
evidence:
root cause category:
fix made:
verification:
should become durable guidance:
```

## Categories

- missing context: the agent did not inspect required files, docs, logs, or
  runtime state;
- incorrect context: the agent relied on stale, guessed, or irrelevant facts;
- noisy context: useful evidence was buried under low-value output;
- weak verification: completion was claimed without a check that covered the
  changed behavior;
- unsafe mutation: files, branches, services, or external state changed outside
  the intended scope;
- workflow mismatch: the task needed planning, research, browser validation,
  or PR handling but ran as a simple edit;
- tool-surface risk: a plugin, MCP server, browser, shell, or network tool had
  broader capability than the task required.

## Review Loop

1. Record the first failure, not every downstream symptom.
2. Group similar entries after several traces.
3. Add durable guidance only when the same category repeats.
4. Prefer a script or focused workflow over a broad global rule.
5. Remove stale guidance when the underlying failure no longer appears.

## Entries

```text
date: 2026-07-02
repo or workflow: specialist-review coordination
task: run coordinated specialist review against Compass
first failure: the parent skill searched tool discovery with a narrow phrase,
  found no subagent tools, then shell-launched `codex exec` runs instead of
  using Codex subagents for specialist review.
downstream effects: the CLI child runs re-triggered routing behavior, polluted
  specialist boundaries, and risked reporting non-specialist output as a
  completed specialist review.
evidence: thread 019f23f1-fc61-7a80-bcfa-25eb143304e2 logged zero
  `multi_agent_v1.spawn_agent` calls, repeated `codex exec` launches, and a
  later correction that the CLI output was not coordinated specialist review.
root cause category: workflow mismatch, tool-surface risk
fix made: strengthened the installed `specialist-review` skill to launch the
  `reviewer` coordinator, made `reviewer` require direct specialist subagents,
  made missing delegation fail coordinated specialist review instead of using
  CLI or shell runs, made any clean specialist prompts only a labeled manual
  fallback outside coordinated review, and kept exact tool namespaces as
  session evidence rather than portable runtime law.
verification: `py -3 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" codex\skills\specialist-review`
  and `.\scripts\doctor.ps1` passed before PR
should become durable guidance: yes, as focused installed runtime guidance for
  the specialist-review route.
```

```text
date: 2026-06-12
repo or workflow: multi-thread audit coordination
task: launch several audit threads with their own worktrees and PR workflow
first failure: workers were given both local tracking work and public PR
  authority, so public branches started to carry tracker notes, partial
  findings, and mixed coordination content.
downstream effects: the repository accumulated draft PRs with unclear review
  order, overlapping fixes, and scratch content that was not useful upstream.
evidence: audit tracker PRs had to be folded, closed, or rebuilt into focused
  reviewable changes.
root cause category: workflow mismatch
fix made: added workflows/multi-thread-pr-coordination.md, ignored root .local
  scratch tracking while keeping tracked .local files blocked by doctor, and
  added the Compass review-program gate so green draft PRs do not count as
  readiness without live PR state, stacked-base checks, merge order, and
  current-head review gates.
verification: run .\scripts\doctor.ps1 and verify .local scratch files stay
  ignored while forced-tracked .local files fail; for review-program changes,
  run .\scripts\doctor.ps1 and check the PR's current-head status.
should become durable guidance: yes, as repo-maintainer workflow guidance and
  a local scratch check, not as a global rule for every PR.
```

```text
date: 2026-06-18
repo or workflow: WebMCP overnight benchmark orchestration
task: coordinate worker threads for benchmark runs, dictionary PR review, agent modification audit, and ablation planning
first failure: the controller accepted worker blocker and done claims as terminal state instead of auditing them as evidence claims and converting actionable blockers into PRs, review paths, smokes, or owner handoffs
downstream effects: work stopped at blocker classification, no countable full A/B/C results were produced, review wait was treated too passively, and the controller later overcorrected by directly implementing worker-owned changes
evidence: live objective docs contained no full-result evidence but had completion-shaped blocker checkboxes; worker and monitor threads reported no intervention needed while no full benchmark runner was active
root cause category: workflow mismatch, weak verification
fix made: added a role-forming orchestration-controller skill for control-plane oversight, question-led unblock, thrash detection, slow monitor cadence, independent review, parent-goal evidence, and strict no worker-owned edits; added it to the portable skill allowlist
verification: `py -3 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" codex\skills\orchestration-controller`, `.\scripts\doctor.ps1`, and `git diff --check` passed before PR
should become durable guidance: yes, as a focused skill rather than a broad global rule
```

```text
date: 2026-06-22
repo or workflow: WebMCP weekend benchmark controller
task: oversee a benchmark worker through hosted and DGX A3/CUGA/WebOperator runs, recovery, reporting, and pause
first failure: controller guidance was structurally correct but emotionally weak, so worker blocker and waiting claims still felt like acceptable resting states until the controller adopted a stronger refusal-to-collapse posture
downstream effects: benchmark work repeatedly drifted toward tidy blocker packets, idle waiting, partial-run acceptance, and controller uncertainty before stronger steering converted those states into concrete repair, rerun, pause, or evidence-preservation actions
evidence: stronger controller language produced better behavior: the controller challenged weak blockers, directed partitioning and recovery, stopped active runs cleanly when the user paused, and preserved artifacts instead of accepting "blocked" as the final state
root cause category: workflow mismatch, weak verification
fix made: strengthened installed controller, goal, subagent, PR-ledger, and benchmark-run guidance so `BLOCKED` and passive waiting are treated as pressure claims rather than endpoints
verification: skill validation, `git diff --check`, and targeted source review before PR
should become durable guidance: yes, in runtime skills that shape controller and worker stance
```

```text
date: 2026-06-23
repo or workflow: WebOperator qwen3.6 Flash Verified Hard benchmark operation
task: continue a strict two-arm WebOperator qwen3.6 Flash A/B run and recover partial or invalid rows into usable results
first failure: benchmark guidance made invalid rows and documented blockers feel like acceptable stop points, and key priorities were not front-loaded strongly enough, so a timeout row and provider rejection were treated as a run-ending blocker instead of as result artifacts, recovery candidates, or a reason to keep unaffected slices moving
downstream effects: the orchestrator absorbed the runner role instead of creating a separate runner thread, the active runner was stopped after task 29 timed out, task 31 was killed mid-run, the heartbeat was paused, critical context was too easy to miss behind evidence and caveats, and no naive-arm rows or paired results were produced before the user corrected the priority
evidence: q36r3 monitor showed only 5 valid no-arm rows, 2 invalid no-arm rows, 251 no-arm missing rows, 258 naive missing rows, and no paired-valid results while safe work was still available
root cause category: workflow mismatch, weak verification
fix made: strengthened benchmark-run, artifact-validation, stack-operations, eval-triage, goal, and controller guidance so result production is the sacred priority, invalid rows are a recovery queue, alleged blockers are suspect, healthy comparable slices keep moving, monitor errors are alarms rather than verdicts, long benchmark execution gets a named runner owner while the orchestrator stays in the control plane, and critical context is front-loaded before background
verification: skill validation, doctor check, and diff review before PR
should become durable guidance: yes, in installed runtime skills and the maintenance failure journal
```
