# Portable Claude Config Workflow

Claude is a derived install target of the reviewed `codex/` source. Use
[portable-config.md](portable-config.md) for the shared edit, diff, install,
and latest-to-live flow. There are no hand-maintained `claude/` source files.

## Source Rules

- Edit `codex/skills/<name>/` or `codex/agents/<name>.toml`, then list shared
  capabilities in the relevant Claude-derived manifest array.
- With `-ClaudeHome`, derived skills install to
  `<ClaudeHome>\skills\<name>` and agents to `<ClaudeHome>\agents\<name>.md`;
  otherwise their root is `$HOME\.claude`. No `CLAUDE.md` is installed
  automatically.
- Keep shared guidance runtime-neutral: preserve dual-review intent without
  requiring `@codex`; describe a capability instead of a Codex-only command or
  skill; use generic authoring and validation terms; and name the live config
  or user skill home when paths differ.
- Do not list Codex-only skills such as `using-codex-goals` or `webmcp-*` in
  `[claude].derived_skills`.

## Derivation

The installer copies `SKILL.md` and `references/` from each listed Codex skill,
excluding `agents/openai.yaml`. For each listed agent, it creates Claude YAML
frontmatter from the TOML and `scripts/common.ps1`, preserves
`developer_instructions`, and drops Codex-only fields such as `sandbox_mode`
and `model_reasoning_effort`.

The manifest and `scripts/common.ps1` are the mechanical source of truth for
the exact mapping. Use [addition-intake.md](addition-intake.md) when promoting
or retiring a capability.
