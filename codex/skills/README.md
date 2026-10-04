# Skills

Keep each skill in `codex/skills/<name>/`, then add its name to
`agents.skills` in `manifests/portable-files.json`.

`SKILL.md` describes when to invoke the skill and the judgment it should add.
Keep its frontmatter name and description on single lines for the MCP catalog.
Put necessary specialist prompts and reusable resources inside the skill;
keep source attribution and license notices in `references/sources.md`.

Choose skills for the task. Do not turn the catalog into a mandatory workflow
or assume that every sibling skill is installed in the consuming environment.
