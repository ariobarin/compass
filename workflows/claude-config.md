# Portable Claude Config Workflow

Claude is an install target of Compass. Shared skills and most shared agents
derive from the reviewed `codex/` source. A platform-specific direct agent may
live under `claude/agents/` when Claude needs different frontmatter, tools, or
isolation instructions.

Use [portable-config.md](portable-config.md) for the shared edit, diff, install,
and latest-to-live flow.

## Source Rules

- Edit shared skills under `codex/skills/<name>/` and list them in
  `[claude].derived_skills`.
- Edit shared agents under `codex/agents/<name>.toml` and list them in
  `[claude].derived_agents`.
- Put a Claude-specific agent under `claude/agents/<name>.md` and list it in
  `[claude].agents` only when the shared transform cannot express its contract.
- With `-ClaudeHome`, skills install to `<ClaudeHome>\skills\<name>` and agents
  to `<ClaudeHome>\agents\<name>.md`; otherwise their root is `$HOME\.claude`.
- Keep shared guidance runtime-neutral and avoid Codex-only invocation syntax.
- Do not list Codex-only skills such as `using-codex-goals` in
  `[claude].derived_skills`.
- Carried packs are not installed into Claude unless a target project explicitly
  adopts them.

## Derivation

For each derived skill, the installer copies `SKILL.md`, `references/`,
`scripts/`, and `assets/` from the Codex source while excluding
`agents/openai.yaml`.

For each derived agent, it creates Claude frontmatter from the Codex TOML and
`scripts/common.ps1`, preserves `developer_instructions`, and drops Codex-only
fields. Direct Claude agents are copied as authored.

The manifest and installer are the mechanical source of truth. Use
[addition-intake.md](addition-intake.md) when promoting or retiring a capability.
