---
name: update-local-codex-config
description: Update live Codex home and user skill home from reviewed Compass. Use for local Codex config refreshes or the latest-to-live flow.
---

# Update Local Codex Config

Use the local Compass checkout as source. Run the reviewed updater instead of
copying files by hand.

1. Confirm the Compass worktree is clean.
2. From the Compass repo, run `.\scripts\update-live.ps1`.
3. If Git reports dubious ownership, rerun with `safe.directory` set to the
   Compass repo root.
4. Report the new HEAD, backup path, and verification result.
5. Confirm live `config.toml` against stable keys in `codex/config.review.toml`
   without replacing the file.
6. If the updater stops on local changes or a non-fast-forward branch, stop and
   report the blocker.
