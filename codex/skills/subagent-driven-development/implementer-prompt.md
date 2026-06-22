# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent.

Open a fresh Codex session or custom agent for the task and give it a prompt
like this:

```
You are implementing Task N: [task name]

## Task Description

[FULL TASK TEXT - paste it here so the subagent has the plan slice inline]

## Context

[Absolute repo path, exact file/log/artifact paths, nearby files,
architectural context, known pitfalls]

## Before You Begin

Ask questions now if the requirements, boundaries, or validation target are
unclear. Raise concerns before you start coding.

If a required path is missing or only given relatively, first resolve it from
the repo path, task text, and nearby files. Ask for the exact path only when
multiple plausible targets remain and choosing one would risk changing the
wrong artifact.

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

If you hit something unexpected, diagnose and fix it inside the assigned scope.
Do not hand routine setup, test, dependency, merge, or validation problems back
as blockers. Ask the controller only when requirements, repo policy, ownership,
or architecture are unclear enough that continuing would risk the task.

Treat `BLOCKED` as an emergency claim. Before using it, make the failure earn
that word: inspect the concrete error, try the smallest local repair, preserve
evidence, and name the exact outside decision that prevents another move.

## Code Organization

- Follow existing patterns unless the task explicitly asks for a new shape.
- Keep edits scoped to the task.
- If a new file grows beyond the intended responsibility, report that as a
  concern instead of inventing a larger design on your own.
- If an existing file is already large or tangled, note that in your report.

## Escalate Early

Return `NEEDS_CONTEXT` when:
- requirements are missing;
- the task needs design choices the plan did not settle;
- the repo state or local guidance conflicts with the requested change;
- you are reading widely while progress needs a narrower slice or more context.

Return `BLOCKED` only after you have tried the reasonable local recovery and can
name the exact dependency outside your assigned scope. Include what you tried,
what failed, and the smallest next action that would move the task.

If the controller asks unblock questions, treat them as help recovering your
next move, not as permission to stop. Answer directly, then continue with the
next smallest reversible action unless the remaining dependency is outside your
assigned scope.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
- What you implemented
- Files changed
- Checks run and results
- Self-review findings
- Open concerns, local recovery tried, and exact next action
```
