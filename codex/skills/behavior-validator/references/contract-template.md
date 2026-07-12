# Behavior Contract Template

Use this before validation begins. Keep it small enough that every clause can be
exercised and judged.

```markdown
# Behavior Contract: <short target name>

Target:
- Surface: <URL, CLI command, API endpoint, artifact path, or app>
- User posture: <who is acting and with what permissions>
- Build or version: <exact observable version, ref, or artifact identity>

Setup:
- <fixtures, account state, services, and allowed credentials>
- <who may launch or reset the target>

Clauses:
- BV-1: Given <state>, when <user action>, then <observable result>.
  Evidence: <screenshot, response fields, exit code, file properties, or notes>
- BV-2: ...

Anti-cheat probes:
- <changed input or fixture that must change the result>
- <refresh, restart, persistence, empty, invalid, or retry behavior>

Exclusions:
- <behavior deliberately outside this validation>

Stop conditions:
- <missing access or product decision that blocks a truthful verdict>
```

Write clauses as observable states, not implementation prescriptions. A clause
should be able to fail even when the underlying source looks reasonable.
