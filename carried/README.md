# Carried Capabilities

This directory is for reviewed Compass source that should travel with the repo
but should not load into every Codex or Claude session.

Nothing here is installed by `install.ps1` or `update-live.ps1`. A target
project opts in by copying the relevant capability into that project, using a
plugin, or promoting the capability through a focused PR.

Expected shape:

```text
carried/
  skills/<name>/
  agents/<name>.toml
```

Do not put global runtime behavior here. Do not put carried material under
`codex/skills` or `codex/agents` unless the same PR intentionally promotes it
into installed context. Claude install surfaces derive from promoted Codex
source rather than a hand-maintained carried mirror.
