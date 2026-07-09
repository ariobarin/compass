# Addition Intake Workflow

Use this workflow when deciding whether a new Compass rule, workflow, skill,
agent, hook, script, manifest entry, or config fragment belongs in Compass.
This is maintainer guidance for promoting durable artifacts, not a runtime rule
for every agent session.

## Intake Standard

Treat additions as candidates until evidence shows they solve a repeated problem
and can be reviewed, reinstalled, and verified without carrying generated state.
Promote additions when they are human-owned, portable, and useful outside one
transient task.

## Reduction Case

Before treating an addition as durable, name its reduction case:

- the recurring context, state, duplication, drift, or maintenance cost it
  removes or prevents;
- the existing artifact, manual step, duplicate source, or decision branch it
  replaces, merges, narrows, derives, or mechanizes;
- why the remaining surface is the narrowest one that preserves the behavior.

An addition can be justified when it creates distinct new behavior. In that
case, state why its continuing cost is worth carrying instead of presenting it
as free improvement.

Keep generated state, plugin cache output, auth state, sessions, logs, browser
profiles, local runtime paths, and one-machine trust settings in live or ignored
local storage.

The default path is staged:

1. For installed agentic guidance, use or test the addition in the live target
   home first when that is the lowest risk way to validate behavior.
2. Capture the problem it solves, the evidence that it worked, and its
   reduction case.
3. Decide the smallest durable artifact type and what existing surface it can
   replace, narrow, or leave untouched by decision.
4. Copy only reviewed portable files into this repo.
5. Wire the addition into the route-specific allowlist, install map, docs, and
   checks that apply to that artifact type.
6. Open a PR before treating the portable copy as accepted.

Imported setup from other agents follows the same path. Treat imported files,
skills, hooks, MCP config, and settings as candidate input only. Review them,
route them to the narrowest durable artifact, and keep imported chats, project
lists, auth, plugin follow-up state, and other migration-only runtime data out
of this repo unless the repo intentionally adopts a reviewed portable form.

## Routing

- Repeated human process: add a focused file in `workflows/`.
- Specialized agent behavior: add a skill under `codex/skills/`.
- Focused reviewer or researcher persona: add an agent under `codex/agents/`.
- Claude Code skill or agent: add the reviewed source under `codex/skills/` or
  `codex/agents/`, then list it in `[claude].derived_skills` or
  `[claude].derived_agents` so it derives at install time.
- Mechanical check or sync behavior: add or update a script under `scripts/`.
- Portability boundary or tool capability: update `manifests/`.
- Repo-only maintenance lesson: update `local-docs/`.
- Session-wide personal default: update `codex/AGENTS.md` only after review.
- Stable config fragment: update `codex/config.review.toml`; keep live
  `config.toml` out of repo changes.

If an addition fits more than one route, choose the narrowest route that solves
the repeated problem.

## Runtime Vs Maintainer Guidance

Decide whether the artifact is meant to be installed into a live Codex home,
user skill home, Claude home, or only used to maintain this repo.

Installed agentic guidance changes how future agent sessions behave. Put its
reviewed source in `codex/AGENTS.md`, `codex/agents/`, or `codex/skills/`; the
Claude surface derives from that source at install time. Keep it focused on
durable role, stance, judgment, and capability boundaries. Do not include
Compass maintenance process, PR hygiene, install-map details, or one-repo
review habits in installed agentic docs.

Repo-maintainer guidance helps humans and agents edit this repository. Put that
in this root `AGENTS.md`, `workflows/`, `local-docs/`, `manifests/`, or
`scripts/`. It can explain promotion rules, local checks, stale-guidance sweeps,
and why a portable file belongs here. It should not pretend to be a runtime rule
for every agent session.

## Skill And Agent Additions

Skills and agents need extra review because they shape future agent behavior.

- Keep skill descriptions concise and specific.
- Put detailed skill instructions in `SKILL.md`, references, scripts, or
  assets.
- Exclude system skills and plugin cache skills unless the repo intentionally
  owns a local copy.
- Install user skills into `$HOME/.agents/skills`; keep `codex/skills/` as the
  reviewed source tree.
- Add each portable skill name to `manifests/portable-files.toml`.
- `scripts/common.ps1` reads portable skill names from that manifest.
- For Claude skills and agents, list the codex skill in `[claude].derived_skills`
  and the codex agent in `[claude].derived_agents` in
  `manifests/portable-files.toml`.
- When removing a previously portable user skill, keep its legacy Codex-home
  retirement entry and add an explicit user-home retirement entry to
  `Get-RetiredPortableFileMap` so `install.ps1 -Apply` actually uninstalls
  both live copies.
- Give agents a sandbox that matches their evidence path. Pure explorers that
  should never mutate state need `sandbox_mode = "read-only"`. Reviewers that
  must run tests, commands, browser checks, or plugin-backed validation should
  be non-editing by instruction instead of blocked by sandbox.
- Run `.\scripts\doctor.ps1` to catch manifest boundary and agent sandbox
  drift.

## Memory-Only Skills

Treat files under the live Codex memory skills directory (`$CODEX_HOME/memories/skills` or equivalent) as candidate
legacy material, not active portable skills. They are useful evidence about past
workflow experiments, but they do not belong in `codex/skills/` until fresh
examples show the capability is still repeated, portable, and worth installing.

When reviewing a memory-only skill:

- Promote it only when recent repeated examples prove the same capability is
  still useful across repos or workflows.
- Fold it into an existing Compass skill when the behavior overlaps a current
  installed skill.
- Retire it as stale local history when it no longer maps to current Codex,
  Compass, or repo workflows.
- Prefer a maintainer workflow note, local doc, or `*-learnings.md` entry in `local-docs/` when
  the material explains how to maintain Compass rather than how future agent
  sessions should act.

Do not create a new installed global skill from memory-only material unless the
fresh evidence supports promotion better than a repo-maintainer note or an
update to an existing Compass skill.

## Stale Guidance Sweep

Every addition should include a nearby stale-guidance pass:

- Check whether README layout notes mention the new artifact type or workflow.
- Check whether `local-docs/README.md` lists new local docs.
- Check whether `workflows/portable-config.md` links new workflows.
- Check whether `scripts/doctor.ps1` should require the new durable file.
- Check whether agent or tool docs still match current sandbox and review rules.
- Replace guidance that describes an old flow with the current route.

Scope the sweep to directly related cleanup. Fix stale items that affect the new
addition flow or current portability checks.

## PR Shape

Use a pull request as the review unit for additions. Keep the PR focused on the
addition and its directly related stale-guidance fixes. Include the verification
commands in the PR body or final report.
