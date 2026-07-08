# Portable Claude Config Workflow

Use this workflow when changing Claude Code setup that should survive a new
machine, fresh profile, or copied repo checkout.

This is the Claude Code side of the Codex portable flow in
[portable-config.md](portable-config.md). Codex is the reviewed source of truth.
Every Claude skill and agent derives from `codex/` at install time, so a change
lands once and applies to both runtimes. There are no hand-maintained `claude/`
source files to keep in step. Both surfaces install from the same repo with the
same scripts.

These scripts use `-ClaudeHome` for Claude-home files, otherwise `$HOME\.claude`.

## Targets

- Claude skills install to `$HOME\.claude\skills\<name>`.
- Claude agents install to `$HOME\.claude\agents\<name>.md`.
- No `CLAUDE.md` is installed automatically. The personal `~/.claude/CLAUDE.md`
  stays separate, the same way `codex/config.review.toml` stays repo-only.

## Change flow

1. Edit the codex source: `codex/skills/<name>/` for a skill,
   `codex/agents/<name>.toml` for an agent.
2. Run `.\scripts\doctor.ps1`.
3. Run `.\scripts\verify-live.ps1 -SkipCodexCommand` for a quick drift report.
4. Run `.\scripts\diff-live.ps1` for a full diff against live files.
5. Review the diff.
6. Run `.\scripts\install.ps1 -Apply` only after the diff is accepted.

## Latest-to-live flow

`.\scripts\update-live.ps1` already installs the Claude surface alongside the
Codex surface. No separate command is needed.

## Keep The Source Runtime-Neutral

Because Claude derives from the codex source verbatim (modulo dropped
`agents/openai.yaml`), the codex source must work for both runtimes. When
writing or editing a skill or agent that both runtimes use, keep it neutral:

- `@codex` review gates: keep the dual-review intent without making `@codex`
  mandatory. "Run `neutral-critic`; for `ariobarin/*` repos also request a
  second independent reviewer (such as `@codex` when available)."
- `~/.codex`, `$CODEX_HOME`, "Codex home": generalize to "the live config
  home" or name both surfaces (`.codex`, `.agents`, `.claude`).
- bare `codex` CLI calls: generalize or name both runtimes.
- Codex-only features such as `/goal` and `using-codex-goals`: describe the
  capability ("a durable goal contract") instead of naming the codex-only skill.
- Skill Creator helpers (`$skill-creator`, `init_skill.py`,
  `quick_validate.py`): keep skill authoring generic; validate with
  `.\scripts\doctor.ps1`.
- Paths: prefer runtime-neutral forms such as "the user skill home
  (`.agents/skills` on Codex, `.claude/skills` on Claude)".

The installer derives a Claude skill from `codex/skills/<name>` by copying
`SKILL.md` and `references/` and dropping `agents/openai.yaml`. It derives a
Claude agent from `codex/agents/<name>.toml`, building YAML frontmatter
(`name`, `description`, `tools`, `model: inherit`, `color`) from the TOML plus
the per-agent frontmatter map in `scripts/common.ps1`; the body is the TOML
`developer_instructions` verbatim. Codex-only fields such as `sandbox_mode` and
`model_reasoning_effort` are dropped, since Claude has no equivalent.

Skip skills that only make sense in the Codex runtime, such as
`using-codex-goals` and the `webmcp-*` set: do not list them in
`[claude].derived_skills`, since Claude has no matching runtime.

## Related Workflows

- [portable-config.md](portable-config.md): the Codex side of the same flow.
- [addition-intake.md](addition-intake.md): promoting new portable artifacts.
