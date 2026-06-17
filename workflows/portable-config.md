# Portable Codex Config Workflow

Use this workflow when changing Codex setup that should survive a new machine,
fresh profile, or copied repo checkout.

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
- project trust entries for one machine;
- plugin cache paths;
- migration prompts and generated state;
- auth, browser, or connector state.

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
- [read-only-research.md](read-only-research.md): mapping code paths before
  edits.
- [agent-failures.md](agent-failures.md): converting repeated failures into
  durable improvements.
