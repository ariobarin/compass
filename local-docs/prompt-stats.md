# Static Prompt Statistics

Use `scripts/prompt-stats.py` to measure repository-owned prompt surfaces without
running a model or reading runtime state. The tool reads only files under the
repository root that Compass owns as global guidance, custom agents, selected
skills, skill references, skill templates, or reviewed config.

## Commands

```powershell
python scripts/prompt-stats.py
python scripts/prompt-stats.py --json
python scripts/prompt-stats.py --check
.\scripts\prompt-stats.ps1 -Json
```

Use `--root` for a different checkout. The PowerShell wrapper uses the checkout
that contains the script.

## What Is Measured

The report includes:

- UTF-8 bytes, Unicode characters, and estimated tokens per file;
- strong steering clauses and term counts;
- likely duplicate clauses across files;
- custom agent model and reasoning effort routing;
- absolute prompt budget warnings.

The default estimator divides Unicode characters by 4 and rounds up. It is
stable and dependency-free, but it is not an exact tokenizer. Change the ratio
with `--chars-per-token` when a different approximation is useful.

Strong steering counts cover `must`, `always`, `never`, `required`, numbered
steps, and word forms related to spawn, launch, dispatch, review, and verify.
These counts describe force and process density. They do not declare an
instruction wrong.

Duplicate findings compare normalized clauses across different files with
Jaccard similarity. The default threshold is 0.9 and clauses shorter than 8
words are ignored. JSON contains paths, similarity, and a short normalized label.
It does not contain prompt bodies.

## Surface Rules

The first version scans these repository-owned surfaces:

- root `AGENTS.md` and `codex/AGENTS.md` as always-loaded global guidance;
- every `codex/agents/*.toml` file as a routed agent surface;
- manifest-listed `codex/skills/*/SKILL.md` files as routed skill surfaces;
- Markdown, text, JSON, TOML, and YAML files under each listed skill's
  `references/`, `templates/`, and `assets/` folders as manually selected
  payloads;
- `codex/config.review.toml` as manually selected reviewed config.

It does not scan sessions, logs, caches, databases, home directories, generated
plugin state, or MCP state.

## Budgets And Check Mode

Defaults are reporting thresholds, not policy:

- global prompt aggregate: 4000 estimated tokens;
- all agent prompts: 12000 estimated tokens;
- one agent prompt: 2500 estimated tokens;
- all skill routing descriptions: 2000 estimated tokens;
- largest selected skill payload: 4000 estimated tokens.

Each threshold has a matching CLI option. `--check` exits with code 1 only when
one or more configured budgets are exceeded. Invalid input or unreadable prompt
metadata exits with code 2. Without `--check`, budget findings are warnings and
the command exits successfully.

The selected skill payload groups `SKILL.md` with its Markdown or text references
and templates. It is a conservative upper bound for a skill whose linked payload
is fully loaded.

## Future Integration

A later focused change can add `prompt-stats` to `scripts/compass.ps1` beside the
existing `skills-audit` route. Keep the standalone Python and PowerShell commands
as the implementation surface so dispatcher integration stays thin.
