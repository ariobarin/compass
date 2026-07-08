# Portable Claude Config Workflow

Use this workflow when changing Claude Code setup that should survive a new
machine, fresh profile, or copied repo checkout.

This is the Claude Code side of the Codex portable flow in
[portable-config.md](portable-config.md). Codex is the reviewed source of truth.
Claude skills and agents derive from `codex/skills/` and `codex/agents/` at
install time by default, so a change lands once and applies to both runtimes.
Only skills or agents with Claude-specific wording keep a hand-maintained
`claude/` override. Both surfaces install from the same repo with the same
scripts.

These scripts use `-ClaudeHome` for Claude-home files, otherwise `$HOME\.claude`.

## Targets

- Claude skills install to `$HOME\.claude\skills\<name>`.
- Claude agents install to `$HOME\.claude\agents\<name>.md`.
- No `CLAUDE.md` is installed automatically. The personal `~/.claude/CLAUDE.md`
  stays separate, the same way `codex/config.review.toml` stays repo-only.

## Change flow

1. Edit the source first: `codex/skills/<name>/` for a derived skill,
   `codex/agents/<name>.toml` for a derived agent, or the matching `claude/`
   path for a Claude-specific override.
2. Run `.\scripts\doctor.ps1`.
3. Run `.\scripts\verify-live.ps1 -SkipCodexCommand` for a quick drift report.
4. Run `.\scripts\diff-live.ps1` for a full diff against live files.
5. Review the diff.
6. Run `.\scripts\install.ps1 -Apply` only after the diff is accepted.

## Latest-to-live flow

`.\scripts\update-live.ps1` already installs the Claude surface alongside the
Codex surface. No separate command is needed.

## Deriving And Overriding Skills

Claude and Codex share the `name` and `description` SKILL.md frontmatter, so
skill bodies are mostly portable. Derivation is the default: list a skill in
`[claude].derived_skills` and the installer generates the Claude skill from
`codex/skills/<name>` by copying `SKILL.md` and `references/` and dropping
Codex-only metadata such as `agents/openai.yaml`. There is no second source tree
to keep in step.

Keep a hand-maintained `claude/skills/<name>/` override only when the skill needs
Claude-specific wording. List it in `[claude].skills`, not `derived_skills`.
When porting `codex/skills/<name>` to such an override:

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

If an override later converges with the Codex source, delete the
`claude/skills/<name>` tree and move the name from `[claude].skills` to
`[claude].derived_skills` so it derives again.

Claude agents also derive by default. List an agent in
`[claude].derived_agents` and the installer generates `claude/agents/<name>.md`
from `codex/agents/<name>.toml`, building YAML frontmatter (`name`,
`description`, `tools`, `model: inherit`, `color`) from the TOML plus the
per-agent frontmatter map in `scripts/common.ps1`. The body is the TOML
`developer_instructions` verbatim. Codex-only fields such as `sandbox_mode` and
`model_reasoning_effort` are dropped, since Claude has no equivalent.

Keep a hand-maintained `claude/agents/<name>.md` override only when the agent
needs Claude-specific wording. List it in `[claude].agents`, not
`derived_agents`. When porting `codex/agents/<name>.toml` to such an override:

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
