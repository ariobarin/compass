# Hook Surfaces Audit

This audit packet covers Compass-owned Codex hooks.

Packet status:

- Refreshed after hook inventory follow-ups landed.
- Use current hook definitions, guard modules, hook-local docs, doctor checks,
  live drift, and open PR stack state before deriving new work from this
  packet.
- Treat the hook findings as completed audit context unless current source
  proves a new gap.

Scope:

- `codex/hooks.json`
- `codex/hooks/README.md`
- `codex/hooks/portable_guard.ps1`
- `codex/hooks/portable_guard.py`
- `codex/hooks/portable_guard.sh`
- `codex/hooks/guard/*.py`
- `codex/hooks/docs/*.md`
- `scripts/doctor/checks/hooks.ps1`
- `scripts/doctor/hooks/*.ps1`

Purpose: make hook behavior explicit in the review program. Hooks are installed
runtime behavior, but they are not agent prose. They should stay small,
mechanical, reviewed, and tested.

## Current Shape

`manifests/portable-files.toml` installs:

- `codex/hooks.json` into the live Codex home;
- `codex/hooks/` into the live Codex home.

Current hook:

- event: `UserPromptSubmit`;
- command: `portable_guard.sh` on POSIX and `portable_guard.ps1` on Windows;
- selected guard module: `understanding_check`;
- timeout: 30 seconds;
- status message: `Checking understanding prompt`.

Current guard modules:

- `runner.py`: dispatches named guard modules only. It does not auto-discover
  files from the guard directory.
- `understanding_check.py`: detects direct understanding-check prompts and adds
  focus context for the turn.
- `common.py`: shared JSON helpers for adding context, denying tool use, and
  blocking continuation.

## Findings

### Hooks Belong In The Installed Surface Map

The existing inventory listed Codex runtime context as:

- `codex/AGENTS.md`;
- `codex/agents/`;
- `codex/skills/`.

That was incomplete. Compass also installs `codex/hooks.json` and
`codex/hooks/`. A future maintainer reviewing installed behavior must see hooks
in the runtime map.

Decision: keep the inventory listing hooks as installed Codex runtime surfaces.

Follow-up status: completed. The inventory now lists `codex/hooks.json`,
`codex/hooks/`, hook doctor checks, and hook doctor test helpers.

### Keep Hook Behavior Mechanical

The understanding-check hook does not replace a skill. It adds context at the
moment a direct user prompt asks whether the agent understands.

That is the right level:

- the user intent is immediate;
- the behavior is narrow;
- the hook injects a short direction rather than a long policy;
- examples, quoted strings, regex discussions, and term-definition questions
  are excluded;
- `CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK` provides a local escape hatch.

No hook rewrite is needed now.

### Keep Launchers Fail-Open

The POSIX and Windows launchers exit cleanly when the guard script or Python
runner is missing. That is right for runtime hooks: a missing launcher should
not trap the user in a broken Codex session.

Compass owns the capability, so the fail-open runtime path must be paired with
repo checks. That is already true.

### Keep Doctor As The Hard Gate

`scripts/doctor/checks/hooks.ps1` checks:

- `hooks.json` parses as JSON;
- Python is runnable;
- `portable_guard.py` is silent when no adjacent guard package exists;
- the launcher does not import a non-adjacent `guard` package through
  `PYTHONPATH`;
- missing packaged guard modules are not hidden;
- unreadable guard packages fail open silently;
- broken packaged guards fail;
- chained guard modules continue when the first returns false;
- the guard does not write bytecode cache;
- hook doctor tests exist and run.

That is the correct split: runtime fail-open, repo doctor hard-fails.

No check change is needed now.

### Keep Hook Docs Local To Hooks

`codex/hooks/README.md` is installed next to the hook code. It is operational
hook documentation, not general agent instruction. It correctly explains the
launcher shape, guard module routing, active Codex home resolution, fail-open
posture, and hook trust review.

No pruning is needed now.

## Decisions

- Treat `codex/hooks.json` and `codex/hooks/` as installed runtime surfaces in
  the Compass inventory.
- Keep the understanding-check hook installed.
- Keep hook behavior mechanical and narrow.
- Keep launchers fail-open.
- Keep `doctor.ps1` as the hard hook integrity gate.
- Do not add hook behavior to installed skill or agent prose.

## Next PR Boundary

No hook runtime PR is needed now.

Future hook changes should be one hook at a time and include:

- the hook definition;
- the guard module;
- hook-local docs;
- doctor tests;
- `.\scripts\doctor.ps1`;
- `.\scripts\verify-live.ps1 -SkipCodexCommand` when live install behavior is
  claimed.
