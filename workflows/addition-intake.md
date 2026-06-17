# Addition Intake Workflow

Use this workflow when deciding whether a new Codex rule, workflow, skill,
agent, script, manifest entry, or config fragment belongs in `codex-portable`.

## Intake Standard

Additions should be promoted only when they are human-owned, portable, and useful
outside one transient task. Do not commit generated state, plugin cache output,
auth state, sessions, logs, browser profiles, local runtime paths, or one-machine
trust settings.

The default path is staged:

1. Use or test the addition in the live Codex home first when that is the lowest
   risk way to validate behavior.
2. Capture the problem it solves and the evidence that it worked.
3. Decide the smallest durable artifact type.
4. Copy only reviewed portable files into this repo.
5. Wire the addition into the allowlist, install map, docs, and checks.
6. Open a PR before treating the portable copy as accepted.

## Routing

- Repeated human process: add a focused file in `workflows/`.
- Specialized agent behavior: add a skill under `codex/skills/`.
- Focused reviewer or researcher persona: add an agent under `codex/agents/`.
- Mechanical check or sync behavior: add or update a script under `scripts/`.
- Portability boundary or tool capability: update `manifests/`.
- Repo-only maintenance lesson: update `local-docs/`.
- Session-wide personal default: update `codex/AGENTS.md` only after review.
- Stable config fragment: update `codex/config.review.toml`, never live
  `config.toml`.

If an addition fits more than one route, choose the narrowest route that solves
the repeated problem.

## Skill Additions

Skills need extra review because their descriptions are loaded into future
sessions.

1. Keep the description concise and specific.
2. Put detailed instructions in `SKILL.md`, references, scripts, or assets.
3. Exclude system skills and plugin cache skills unless the repo intentionally
   owns a local copy.
4. Add the skill name to `manifests/portable-files.toml`.
5. Add the skill to `Get-PortableFileMap` in `scripts/common.ps1`.
6. Run `.\scripts\doctor.ps1` to catch manifest and install-map drift.

## Stale Guidance Sweep

Every addition should include a nearby stale-guidance pass:

- Check whether README layout notes mention the new artifact type or workflow.
- Check whether `local-docs/README.md` lists new local docs.
- Check whether `workflows/portable-config.md` links new workflows.
- Check whether `scripts/doctor.ps1` should require the new durable file.
- Check whether agent or tool docs still match current sandbox and review rules.
- Remove or update guidance that describes an old flow.

Do not broaden the sweep into unrelated cleanup. Fix stale items that directly
affect the new addition flow or current portability checks.

## PR Shape

Use a pull request as the review unit for additions. Keep the PR focused on the
addition and its directly related stale-guidance fixes. Include the verification
commands in the PR body or final report.
