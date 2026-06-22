# Read-Only Research Workflow

Use this workflow when the next best step is understanding rather than editing:
large repo orientation, unclear bug ownership, unfamiliar runtime paths, branch
reviews, API discovery, or workflow tracing.

This is repo-maintainer guidance. It is not installed into a live Codex home or
user skill home.
Use installed agents or skills when the behavior should travel with live Codex
sessions.

## When To Use

- The task crosses several modules or repos.
- The likely fix is unclear.
- A live behavior needs to be tied back to source.
- The parent context is already noisy and needs a compact evidence packet.
- A second perspective would reduce risk before implementation.

## How To Run

Ask Codex to use the `repo-explorer` agent, or ask directly for read-only
research:

```text
Spawn repo-explorer to map the affected code path. It should not edit files.
Return files inspected, confirmed execution path, risks, and recommended next
step.
```

## Research Rules

- Read first, edit later.
- Prefer `rg`, targeted file reads, and small command outputs.
- Cite exact files and symbols.
- Separate facts from inferences.
- Do not start services unless the user asked for runtime validation.
- Do not mutate git state.

## Output Shape

- Question answered:
- Evidence:
- Execution path:
- Risks:
- Unknowns:
- Recommended next step:

The parent agent should use the report to plan or implement, not paste the whole
research transcript into future context.
