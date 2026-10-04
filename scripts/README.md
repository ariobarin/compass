# Source Checks

Run with Python 3.11 or later:

```sh
python3 scripts/check.py
```

`check.py` validates the published skill catalog against the source directories,
valid skill names, single-line descriptions for Compass MCP, readable UTF-8
profile and host metadata, optional role TOML syntax, and local inline
Markdown links. It checks files in this repository without installing anything
or contacting external services.

CI runs this check on Windows and Linux. Its `portable (...)` job names are
retained because the repository's branch protection requires those contexts.

The MCP bridge reads `codex/AGENTS.md`, `manifests/portable-files.json`, and
`codex/skills/<name>/SKILL.md`. Keep those paths and the `agents.skills` catalog
shape stable while the bridge consumes them. The manifest selects guidance;
it carries no runtime settings.
