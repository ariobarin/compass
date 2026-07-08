# Mechanical Truth Audit

This audit covers the manifest, script, and reviewed config surfaces listed in
`local-docs/compass-surface-inventory.md`.

Scope:

- `manifests/portable-files.toml`
- `manifests/tool-surfaces.md`
- `codex/config.review.toml`
- `scripts/common.ps1`
- `scripts/doctor.ps1`
- `scripts/install.ps1`
- `scripts/verify-live.ps1`
- `scripts/update-live.ps1`
- `scripts/diff-live.ps1`
- `scripts/snapshot.ps1`
- `scripts/codex-restart-recovery.ps1`
- `scripts/doctor/checks/*.ps1`

Purpose: make sure Compass boundaries are checked by mechanical truth instead
of remembered by future agents.

## Current Shape

The mechanical layer is already strong.

- `manifests/portable-files.toml` declares installed Codex files, user skills,
  Claude skills, Claude derived skills, Claude agents, repo-only surfaces,
  carried-but-not-global lists, local-only files, local-only directories, and
  local-only patterns.
- `scripts/common.ps1` turns manifest lists into install, snapshot, diff, and
  live-verify maps.
- `scripts/install.ps1` copies only portable map entries and removes explicit
  retired Codex-home and user-skill copies.
- `scripts/verify-live.ps1` compares live files against repo sources, checks
  derived Claude skills, checks retired portable copies, and verifies live
  `config.toml` has the reviewed agent depth.
- `scripts/update-live.ps1` refuses dirty checkouts, fast-forwards to reviewed
  remote state, installs, and then requires live sync.
- `scripts/doctor.ps1` composes focused checks for required files, manifest
  boundaries, text policy, skills, agents, restart recovery, hooks, and Claude.

## Findings

### Keep Manifest Boundaries As The Source

The manifest is doing the right job. It names what installs, what stays
repo-only, what is carried but not global, and what must remain local-only.

`manifest-boundaries.ps1` makes that real:

- `carried/` must stay listed as repo-only;
- carried list keys must exist;
- carried entries cannot also be installed globally;
- carried paths must exist when listed;
- local-only files, directories, and patterns are blocked in the repo tree;
- tracked files outside the manifest boundary fail `doctor.ps1`;
- manifest-listed files and directories must exist.

No change is needed now.

### Keep The Carried Route Mechanical

The carried route is not only documentation. `doctor.ps1` now checks the
carried root, carried list shape, installed collisions, and missing carried
paths.

That is the right standard. Future demotion PRs can rely on a real route rather
than prose.

No change is needed now.

### Keep Text Policy Mechanical

`text-policy.ps1` blocks non-ASCII text in repo text files and separately
blocks en dash and em dash characters across common text, script, and data
extensions.

That check is exactly the right shape for a user preference that must never
depend on memory.

No change is needed now.

### Fix Stale Snapshot Output

`snapshot.ps1` already reads the shared portable map, so it plans Codex,
user-skill, and Claude snapshots.

Its review-mode final instruction still says:

```text
run with -Apply to refresh this repo from the live Codex home and user skill home
```

That is stale. The command now also includes Claude home. This is small, but it
matters because script output is a maintainer instruction at the moment of
action.

Follow-up PR: update the `snapshot.ps1` review-mode message to name Codex,
user skill, and Claude homes.

### Track Retired Claude Cleanup Before It Is Needed

`Get-RetiredPortableFileMap` removes old Compass-owned copies from Codex home
and user skill home. It does not yet model retired Claude skills or agents.

That is not a bug today because this stack does not remove a Claude-installed
skill or agent. It is a future demotion risk. The first PR that removes a
Claude installed surface should add explicit retired Claude handling in the same
change, with `verify-live.ps1 -SkipCodexCommand -RequireInSync` as evidence.

Do not add broad deletion logic. Retired removals should stay explicit.

### Keep Reviewed Config Fragment Separate

`codex/config.review.toml` is correctly treated as a reviewed fragment, not a
live replacement. The current verifier checks the `agents.max_depth` contract
because specialist review depends on it.

No change is needed now.

## Decisions

- Keep manifest declarations as the root mechanical boundary.
- Keep the carried route enforced by `doctor.ps1`.
- Keep text policy mechanical.
- Keep `config.review.toml` as a fragment, with targeted live verification for
  agent depth.
- Fix the stale `snapshot.ps1` review-mode message in a separate focused PR.
- Add retired Claude cleanup only when a Claude-installed surface is removed.

## Next PR Boundary

Make one focused script PR:

- update `scripts/snapshot.ps1` review-mode wording;
- run `.\scripts\doctor.ps1`;
- run `.\scripts\snapshot.ps1` and inspect the message.
