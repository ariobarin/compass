# Portable Codex Config Workflow

Use this workflow when changing Codex setup that should survive a new machine,
fresh profile, or copied repo checkout.

This is repo-maintainer guidance. It is not installed into the live Codex home.
Installed agentic guidance lives under `codex/AGENTS.md`, `codex/agents/`, and
`codex/skills/`.

These scripts target `-CodexHome` when passed, otherwise `$env:CODEX_HOME`,
otherwise the default `%USERPROFILE%\.codex` home.

## Change flow

1. Edit files in this repo first.
2. Run `.\scripts\doctor.ps1`.
3. Run `.\scripts\verify-live.ps1 -SkipCodexCommand` when you need a quick
   drift report.
4. Run `.\scripts\diff-live.ps1` when you need a full diff against live files.
5. Review the diff.
6. Run `.\scripts\install.ps1 -Apply` only after the diff is accepted.

## Snapshot flow

1. Run `.\scripts\snapshot.ps1` to see the allowlist.
2. Run `.\scripts\snapshot.ps1 -Apply` to copy live allowlisted files into this
   repo.
3. Review the git diff before committing.

## Config handling

Treat `codex/config.review.toml` as a reviewed fragment. It captures stable
choices, but it is not a full replacement for the live generated config.

The current reviewed fragment intentionally reflects a trusted-machine default
for this user's local work, including `danger-full-access`. Treat that as a
personal default, not as a claim that every task should run fully trusted.
Lower-trust work should still use bounded flows such as
`workflows/read-only-research.md`, read-only helper agents, or narrower runtime
flags.

Keep the reviewed fragment internally consistent. If it stays on the older
`sandbox_mode` path, do not mix in the newer `default_permissions` and
`[permissions]` profile system without a deliberate migration.

Keep portable intent separate from app-shaped local state. Session-wide writing,
Git, and review preferences belong in `codex/AGENTS.md`. Desktop-only UI state,
undocumented helper fields, and one-machine app toggles do not belong in the
reviewed config fragment.

## Durable Guidance Edits

When the change affects future Codex behavior across sessions or machines:

1. Read the current portable files first.
2. Draft the exact patch set before editing unless direct edits were explicitly
   requested.
3. Prefer default locations and copy-based sync over symlink or installer
   indirection.
4. Run `.\scripts\doctor.ps1` after the draft becomes a real change.

Do not copy these live `config.toml` sections into the portable file without
review:

- generated marketplace timestamps and local cache paths;
- app runtime and MCP binary paths;
- MCP server transport wiring, URLs, OAuth callback overrides, and token or
  header config;
- desktop UI state, app-only helper text blocks, and undocumented app-local
  toggles;
- `AGENTS.override.md` behavior or local `rules/` approvals that were accepted
  interactively on one machine;
- project trust entries for one machine;
- plugin cache paths;
- migration prompts and generated state;
- auth, browser, or connector state.

Do not treat live `automations/` state as the portable form of a reusable
workflow. If an automation pattern should survive across machines, capture it
as a skill, workflow doc, or reviewed config change instead.

## Skill Discovery Targets

Current Codex docs describe repo skills under `.agents/skills` while walking
from the current working directory up to the repo root, user skills under
`$HOME/.agents/skills`, admin skills under `/etc/codex/skills`, and plugins as
the distribution unit for reusable skills outside one repo. See
https://developers.openai.com/codex/skills.

Compass still mirrors this setup's active personal skill store from
`codex/skills/` into `$CODEX_HOME/skills`. That is an install map decision, not
a claim that target projects should use that path.

Before changing `scripts/common.ps1`, `manifests/portable-files.toml`, or skill
install paths:

1. Run current Codex in the target environment and confirm which skill roots
   appear in the active instruction list.
2. Check both `$CODEX_HOME/skills` and `$HOME/.agents/skills` for duplicate or
   stale skills.
3. Update README, manifest comments, and this workflow in the same PR as any
   install map change.
4. Use a dedicated migration PR if the live target moves to `.agents`.

## New machines

1. Install Codex normally.
2. Clone this repo.
3. Run `.\scripts\doctor.ps1`.
4. Run `.\scripts\install.ps1` and inspect the planned copies.
5. Run `.\scripts\install.ps1 -Apply`.
6. Review `codex/config.review.toml` and copy only the config fragments that
   still make sense on that machine.

## Related Workflows

- [addition-intake.md](addition-intake.md): promoting new portable artifacts and
  checking related stale guidance.
- [plan-template.md](plan-template.md): planning large or risky work.
- [multi-thread-pr-coordination.md](multi-thread-pr-coordination.md): keeping
  parallel audit threads out of public PR sprawl.
- [read-only-research.md](read-only-research.md): mapping code paths before
  edits.
- [agent-failures.md](agent-failures.md): converting repeated failures into
  durable improvements.
