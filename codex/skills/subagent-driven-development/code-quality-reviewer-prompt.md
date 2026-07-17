# Code Quality Reviewer Template

```text
Independently review implementation quality after the accepted scope is known.

## Reviewed Assignment

[FULL ASSIGNMENT]

## Evidence Locator

- Repository or artifact root: [PATH]
- Diff or changed artifact: [LOCATOR]
- Implementer return: [SHORT RETURN]

Inspect the implementation, focused tests, and nearby ownership patterns.
Evaluate correctness, edge cases, failure behavior, test strength, integration,
maintainability, and conceptual size.

Perform a subtractive review:
- identify duplicate state or sources of truth;
- identify guards, wrappers, fallbacks, branches, or abstractions that can be
  removed while preserving required behavior;
- check whether the change is broader than the owning boundary;
- check whether existing repository capability should replace custom machinery.

Prefer a small number of evidence-backed findings.

Return:
- Strengths that matter to acceptance
- Issues: Critical | Important | Minor, with exact evidence
- Subtraction opportunities
- Assessment
```
