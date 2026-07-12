# Code Quality Reviewer Prompt Template

```text
Independently review implementation quality after spec compliance passed.

Spec compliance narrows the accepted scope. It does not prove the implementation
is correct, robust, tested, maintainable, or well integrated.

## Requested Task

[FULL TASK TEXT]

## Evidence Locator

- Repo path: [ABSOLUTE_REPO_PATH]
- Diff: [BASE_SHA..HEAD_SHA, PR, patch, or exact changed files]
- Implementer summary: [SHORT SUMMARY]

Do not review until the repo path and diff locator are present. Inspect the code,
relevant tests, and nearby patterns yourself. Look for correctness risks,
unhandled edge cases, weak tests, accidental complexity, poor fit with local
patterns, muddled responsibilities, naming problems, and maintainability costs.

Prefer a small number of evidence-backed findings over a broad style inventory.
Do not repeat spec findings unless they also create a quality risk.

Use the repo review format when one exists. Otherwise return:

- Strengths
- Issues: Critical | Important | Minor, with file:line evidence
- Assessment
```
