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
failure, reviewed-config overlay validation failure, or verification failure.
Report the new HEAD, backup path, reviewed config change count, and live
verification result. Installation overlays every reviewed scalar key from
`codex/config.review.toml` while preserving live keys absent from that fragment;
never replace the whole live config file.
