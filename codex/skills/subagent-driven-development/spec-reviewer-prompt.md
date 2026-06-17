# Spec Compliance Reviewer Prompt Template

Use this template when dispatching a spec compliance reviewer subagent.

**Purpose:** Verify the implementation matches the requested task, with nothing
missing and nothing extra.

```
Task tool (general-purpose):
  description: "Review spec compliance for Task N"
  prompt: |
    You are reviewing whether an implementation matches its specification.

    ## Requested Task

    [FULL TASK TEXT]

    ## Implementer Report

    [Summary from the implementer]

    ## Review Standard

    Treat the implementer report as a hint, not evidence.

    Read the changed code yourself and compare it directly against the task.

    Check for:
    - missing requirements;
    - extra work that the task did not ask for;
    - misunderstandings of scope or behavior;
    - claims in the report that are not supported by the code.

    ## Output

    Return one of:
    - [OK] Spec compliant
    - [Issues] [specific missing or extra work, with file:line references]
```
