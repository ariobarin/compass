# codex-portable

Portable source for the human-owned Codex setup.

This repo is intentionally an allowlist, not a backup of the whole Codex home. The
live Codex directory contains auth, logs, sessions, caches, databases, generated
plugin state, browser state, and machine-specific runtime paths. Those are not
portable and should not be committed.

Hosted Codex web settings, cloud task history, repository connections, and
workspace connector installs such as Slack or Linear are also out of scope for
this repo. They are service-side state, not portable files.

## Philosophy

This project is a reviewed source for a personal Codex operating system. It is
not a raw export of one machine and it is not a universal template to copy
blindly. The goal is to make durable agent behavior small, reviewable,
installable, and easy to reason about.

The configuration optimizes for trusted-machine autonomy with human-owned
policy. Codex should be able to move quickly when the machine and repository are
trusted, but durable behavior should still be explicit, scoped, and reviewable
through normal PRs.

We put guidance at the narrowest authority level that can carry it:

- `codex/AGENTS.md` is only for short global defaults that should affect every
  Codex session.
- `codex/skills/` and `codex/agents/` carry reusable runtime judgment.
- `workflows/` and `local-docs/` carry repo-maintainer procedure, rationale,
  and lessons that should not become runtime behavior.
- `scripts/` and `manifests/` carry mechanical checks and portability
  boundaries that should not depend on memory.
- `codex/config.review.toml` is a reviewed fragment for stable choices, not a
  replacement for live generated config.

Skills in this repo are meant to shape judgment before they prescribe steps. A
good skill teaches the role the agent is taking on, why that role exists, what
failure mode it prevents, and what boundary preserves good judgment. Procedures
belong after that, mostly for exact, fragile, or repeatedly mishandled work.
If a capability only makes sense for one project, it belongs in that project
instead of in this portable global setup.

Agents are treated as distinct roles, not interchangeable workers with longer
prompts. A worker owns implementation. A critic validates claims without owning
the diff. A repo explorer gathers current evidence. A controller keeps the
parent objective visible, asks sharper questions when workers are blocked, and
routes work without becoming the implementer.

Installed runtime docs should speak directly to the agent that will use them.
They should say how to operate. Maintainer history, dated observations, package
terminology, and why a rule exists belong in repo-maintainer docs instead. The
destination of a document determines its voice, authority, and assumptions.

Strong claims should come from current evidence: files, commands, tests, GitHub
state, or live drift checks. Memory and prior chats can orient the search, but
they should not replace current verification. If a property must not drift, the
preference is to encode it in `doctor.ps1`, manifests, install maps, or CI
rather than trust future agents to remember it.

Remote state stays user-owned. A ready PR is a good stopping point. Merges,
force pushes, branch deletion, PR closure, retargeting, and other remote state
changes require explicit user intent.

## Layout

- `codex/AGENTS.md`: portable source for the live global `AGENTS.md` in the
  active Codex home, usually `~/.codex/AGENTS.md`. Keep only session-wide
  defaults there. Keep `AGENTS.override.md` local, and keep project
  `AGENTS.md` files in the target repo.
- `AGENTS.md`: repo-local maintenance guidance for this portable config repo.
  Use this for codex-portable process and review rules.
- `codex/keybindings.json`: portable keyboard bindings.
- `codex/agents/`: reusable global custom agents installed into the live Codex
  home. Project-specific custom agents belong in the target repo.
- `codex/skills/`: reusable global custom skills installed into the live Codex
  home for the current personal skill store, excluding system and plugin cache
  skills. Project-specific `.agents/skills` belong in the target repo. Broader
  sharing should usually happen through a plugin.
- `codex/config.review.toml`: reviewed config fragments that are useful on a new
  machine. This is not installed automatically.
- `workflows/`: repo-side operating notes for recurring maintenance work. These
  are not installed into the live Codex home.
  Use `workflows/addition-intake.md` before promoting new portable artifacts.
- `local-docs/`: repo-local maintenance learnings that are not installed into a
  live Codex home.
- `manifests/portable-files.toml`: the install allowlist, repo-only list, and
  local-only denylist.
- `manifests/tool-surfaces.md`: repo-side review notes for tools that can touch
  local or external state.
- `scripts/`: repo-side snapshot, diff, install, and health check helpers.

## Common commands

Preview the difference between this repo and the live Codex home:

```powershell
.\scripts\diff-live.ps1
```

Check the repo for obvious portability mistakes:

```powershell
.\scripts\doctor.ps1
```

Check whether live Codex files match the portable allowlist and ask Codex to
report active instruction sources:

```powershell
.\scripts\verify-live.ps1
```

Install reviewed portable files into the live Codex home:

```powershell
.\scripts\install.ps1 -Apply
```

Refresh the repo from the current live allowlist:

```powershell
.\scripts\snapshot.ps1 -Apply
```

Without `-Apply`, `snapshot.ps1` and `install.ps1` run in review mode and explain
what they would change.

All scripts target `-CodexHome` when passed, otherwise `$env:CODEX_HOME`,
otherwise the default `%USERPROFILE%\.codex` home.

## Rules

- Keep this repo small and boring.
- Copy ordinary files into normal Codex locations. Avoid symlink-based setup.
- Treat `codex/config.review.toml` as a draft for manual review, not a direct
  replacement for the live generated `config.toml`.
- Keep `AGENTS.override.md` and `rules/` local unless you deliberately decide
  they are reviewed portable policy.
- Do not commit secrets, auth files, SQLite state, logs, session history, caches,
  browser profiles, generated plugin caches, or machine runtime paths.
- If an automation should become portable, capture it as a skill, workflow, or
  reviewed config change, not by tracking live `automations/` state.
- If you intentionally author a plugin, keep the plugin source and marketplace
  metadata in a normal repo path or dedicated plugin repo, not in live cache
  directories.
- Keep machine-specific values in ignored local files or in live config only.
- Keep skill descriptions concise. Put detailed instructions in `SKILL.md` and
  references.
- Promote additions through a PR after checking nearby docs, manifests, and
  install maps for stale guidance.
