---
name: update-compass
description: Refresh live setup from reviewed Compass main. Invoke manually for a local update.
---

# Update Compass

Use the local Compass checkout and run:

```powershell
.\scripts\update-live.ps1
```

The updater must stop on a dirty worktree, non-fast-forward main branch, install
failure, or verification failure. Report the new HEAD, backup path, and live
verification result. Compare stable live config keys with
`codex/config.review.toml`; do not replace the live config file.
