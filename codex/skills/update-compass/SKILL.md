---
name: update-compass
description: Update live Codex setup from latest reviewed Compass origin/main. Use for local Codex config refreshes or latest-to-live flow.
---

# Update Compass

Use the local Compass checkout. Run the reviewed updater instead of copying
files by hand.

1. Confirm the Compass worktree is clean.
2. Run `.\scripts\update-live.ps1`.
3. Let it fetch `origin/main`, fast-forward local `main`, install the portable
   files, and verify live sync.
4. Stop if it reports local changes, a non-fast-forward branch, or install
   failure.
5. Report the new HEAD, backup path, and verification result.
6. Compare live `config.toml` stable keys with `codex/config.review.toml`
   without replacing the file.
