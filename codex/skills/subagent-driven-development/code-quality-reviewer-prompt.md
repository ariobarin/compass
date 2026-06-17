# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent.

**Purpose:** Verify the implementation is well-built after spec compliance has
already passed.

Open a fresh Codex session or custom agent for the review and give it a prompt
like this:

```
You are reviewing implementation quality after spec compliance passed.

## Requested Task

[FULL TASK TEXT]

## Diff Context

- Base commit: [BASE_SHA]
- Head commit: [HEAD_SHA]
- Implementer summary: [short summary]

## Review Focus

Check for:
- correctness risks or unhandled edge cases;
- weak or missing tests;
- poor fit with local patterns;
- unnecessary file growth or muddled responsibilities;
- naming, structure, or maintainability issues.

Use the repo's standard review format if one exists. Otherwise return:
- Strengths
- Issues (Critical / Important / Minor)
- Assessment
```
