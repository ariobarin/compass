# Portable Claude Config Workflow

Use this workflow when changing Claude Code setup that should survive a new
machine, fresh profile, or copied repo checkout.

This is the Claude Code mirror of the Codex portable flow in
[portable-config.md](portable-config.md). Compass keeps `codex/` as the reviewed
source for Codex and `claude/` as the reviewed source for Claude Code. Both
surfaces install from the same repo with the same scripts.

These scripts use `-ClaudeHome` for Claude-home files, otherwise `$HOME\.claude`.

## Targets

- Claude skills install to `$HOME\.claude\skills\<name>`.
- Claude agents install to `$HOME\.claude\agents\<name>.md`.
- No `CLAUDE.md` is installed automatically. The personal `~/.claude/CLAUDE.md`
  stays separate, the same way `codex/config.review.toml` stays repo-only.

## Change flow

1. Edit files in `claude/skills/` or `claude/agents/` first.
2. Run `.\scripts\doctor.ps1`.
3. Run `.\scripts\verify-live.ps1 -SkipCodexCommand` for a quick drift report.
4. Run `.\scripts\diff-live.ps1` for a full diff against live files.
5. Review the diff.
6. Run `.\scripts\install.ps1 -Apply` only after the diff is accepted.

## Latest-to-live flow

`.\scripts\update-live.ps1` already installs the Claude surface alongside the
Codex surface. No separate command is needed.

## Porting From Codex

Claude and Codex share the `name` and `description` SKILL.md frontmatter, so
skill bodies are mostly portable. When porting a `codex/skills/<name>` skill to
`claude/skills/<name>`:

1. Copy `SKILL.md` and any `references/*.md`. References are tool-agnostic prose.
2. Drop `agents/openai.yaml`. Claude discovers agents from
   `$HOME/.claude/agents`, not from a skill bundle.
3. Adapt Codex-runtime references:
   - `@codex` review gates: keep the dual-review intent without making `@codex`
     mandatory. "Run `neutral-critic`; for `ariobarin/*` repos also request a
     second independent reviewer."
   - `~/.codex`, `$CODEX_HOME`, "Codex home": generalize to "the live config
     home" or name both surfaces.
   - bare `codex` CLI calls: generalize or note the Claude equivalent.
   - Codex-only features such as `/goal`: drop or reword for a generic agent.

When porting a `codex/agents/<name>.toml` agent to `claude/agents/<name>.md`:

1. Convert TOML to markdown with YAML frontmatter: `name`, `description`, then
   `tools`, `model: inherit`, and an optional `color`.
2. Move `developer_instructions` into the markdown body verbatim.
3. Give critics and explorers read-only tools (`Read, Grep, Glob, Bash`). Give
   the research critic web tools. Let the coordinator agent inherit all tools.

Skip skills that only make sense in the Codex runtime, such as
`using-codex-goals` and the `webmcp-*` set, until Claude has the matching
runtime.

## Related Workflows

- [portable-config.md](portable-config.md): the Codex side of the same flow.
- [addition-intake.md](addition-intake.md): promoting new portable artifacts.
