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
