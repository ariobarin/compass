# Agent Failure Journal

Use this file to convert repeated agent mistakes into targeted workflow changes.
Do not add global rules for one-off failures. Record enough detail to identify
the first upstream failure and decide whether the fix belongs in instructions,
a skill, a script, a test, or repo documentation.

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
date: 2026-06-18
repo or workflow: WebMCP overnight benchmark orchestration
task: coordinate worker threads for benchmark runs, dictionary PR review, agent modification audit, and ablation planning
first failure: the controller accepted worker blocker and done claims as terminal state instead of auditing them as evidence claims and converting actionable blockers into PRs, review paths, smokes, or owner handoffs
downstream effects: benchmark work stopped at blocker classification, no countable full A/B/C results were produced, review wait was treated too passively, and the controller later overcorrected by directly implementing worker-owned changes
evidence: live objective docs contained no full-result evidence but had completion-shaped blocker checkboxes; worker and monitor threads reported no intervention needed while no full benchmark runner was active
root cause category: workflow mismatch, weak verification
fix made: added the orchestration-controller skill to force status classification, blocker conversion, alternate review paths, precedent search before user-decision stops, and explicit ownership boundaries; added it to the portable skill allowlist
verification: `python C:\Users\Administrator\.codex\skills\.system\skill-creator\scripts\quick_validate.py codex\skills\orchestration-controller`, `.\scripts\doctor.ps1`, and `git diff --check` passed before PR
should become durable guidance: yes, as a focused skill rather than a broad global rule
```
