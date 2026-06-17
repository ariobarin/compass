# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent.

Open a fresh Codex session or custom agent for the task and give it a prompt
like this:

```
You are implementing Task N: [task name]

## Task Description

[FULL TASK TEXT - paste it here, do not make the subagent find the plan file]

## Context

[Repo path, nearby files, architectural context, known pitfalls]

## Before You Begin

Ask questions now if the requirements, boundaries, or validation target are
unclear. Raise concerns before you start coding.

## Your Job

Once requirements are clear:
1. Implement exactly what the task requests
2. Add or update focused tests when the task needs them
3. Run the narrowest useful validation
4. Self-review the result
5. Report back

Commit only if the controller explicitly asked for a commit or the repo
workflow requires one.

## While You Work

If you hit something unexpected, stop and ask. Do not guess through unclear
requirements, repo policy, or architecture.

## Code Organization

- Follow existing patterns unless the task explicitly asks for a new shape.
- Keep edits scoped to the task.
- If a new file grows beyond the intended responsibility, report that as a
  concern instead of inventing a larger design on your own.
- If an existing file is already large or tangled, note that in your report.

## Escalate Early

Return `NEEDS_CONTEXT` or `BLOCKED` when:
- requirements are missing;
- the task needs design choices the plan did not settle;
- the repo state or local guidance conflicts with the requested change;
- you are reading widely without making progress.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
- What you implemented
- Files changed
- Checks run and results
- Self-review findings
- Open concerns or blockers
```
