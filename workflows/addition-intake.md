# Addition Intake Workflow

Use this workflow when deciding whether a new Codex rule, workflow, skill,
agent, script, manifest entry, or config fragment belongs in `codex-portable`.
This is maintainer guidance for promoting durable artifacts, not a runtime rule
for every Codex turn.

## Intake Standard

Treat additions as candidates until evidence shows they solve a repeated problem
and can be reviewed, reinstalled, and verified without carrying generated state.
Promote additions when they are human-owned, portable, and useful outside one
transient task.

Keep generated state, plugin cache output, auth state, sessions, logs, browser
profiles, local runtime paths, and one-machine trust settings in live or ignored
local storage.

The default path is staged:

1. Use or test the addition in the live Codex home first when that is the lowest
   risk way to validate behavior.
2. Capture the problem it solves and the evidence that it worked.
3. Decide the smallest durable artifact type.
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
- Mechanical check or sync behavior: add or update a script under `scripts/`.
- Portability boundary or tool capability: update `manifests/`.
- Repo-only maintenance lesson: update `local-docs/`.
- Session-wide personal default: update `codex/AGENTS.md` only after review.
- Stable config fragment: update `codex/config.review.toml`; keep live
  `config.toml` out of repo changes.

If an addition fits more than one route, choose the narrowest route that solves
the repeated problem.

## Skill And Agent Additions

Skills and agents need extra review because they shape future agent behavior.

- Keep skill descriptions concise and specific.
- Put detailed skill instructions in `SKILL.md`, references, scripts, or
  assets.
- Exclude system skills and plugin cache skills unless the repo intentionally
  owns a local copy.
- Add each portable skill name to `manifests/portable-files.toml`.
- Add each portable skill to `Get-PortableFileMap` in `scripts/common.ps1`.
- Give read-only reviewer or researcher agents a top-level
  `sandbox_mode = "read-only"` setting.
- Run `.\scripts\doctor.ps1` to catch manifest, install-map, and read-only
  agent drift.

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
