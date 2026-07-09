# Carried Capabilities Design

Use this design before moving any installed skill or agent out of global
availability.

Carried capability means reviewed source that travels with Compass but does not
load into every Codex or Claude session. It is not a fallback. It is an opt-in
route for useful material that fails the global-install test.

## Purpose

Global runtime context is expensive. Every installed skill and agent can shape
future work, trigger retrieval, and compete with stronger guidance. A capability
should not stay global because it was useful once, because it is impressive, or
because removal feels wasteful.

Useful material still deserves a home. Carried source lets Compass preserve it
without forcing every future agent to carry it in normal work.

## Eligibility

Keep a capability globally installed only when it passes this test:

- it is reusable across many repos or workflows;
- it should be available during ordinary Codex or Claude work;
- it shapes judgment that is broadly useful, not project taste;
- it does not make the active skill set noisy;
- it has a clear audience and invocation moment;
- it is strong enough to justify its retrieval cost.

Move a capability toward carried status when:

- it is project-specific, benchmark-specific, or domain-shaped;
- it is useful only during occasional campaigns;
- it overlaps a stronger global skill;
- it is mostly a template, reference, or specialized procedure;
- it belongs near a target repo instead of every session.

Do not move a capability only because it is long. First ask whether the length
is bloat, necessary procedure, or the wrong audience.

## Proposed Source Shape

Carried material lives under the top-level `carried/` directory. The directory
is listed as repo-only in `manifests/portable-files.toml`.

Use runtime-shaped subdirectories without making them installed roots:

```text
carried/
  codex/
    skills/<name>/
    agents/<name>.toml
  claude/
    skills/<name>/
    agents/<name>.md
```

Do not use `.agents/skills`, `codex/skills`, `codex/agents`, `claude/skills`, or
`claude/agents` for carried material. Those paths mean installed runtime
context in this repo.

Carried skills may keep normal `SKILL.md` shape so they can be promoted,
copied, or compared without reformatting. Their location is what keeps them out
of global runtime.

## Manifest Contract

The manifest should make carried status visible without installing it.

The manifest contract:

- `carried` is listed in `[repo_only].dirs`;
- `[carried]` lists carried Codex skills, Codex agents,
  Claude skills, and Claude agents;
- keep install functions reading only installed sections;
- keep carried entries out of live copy maps;
- make `doctor.ps1` reject carried entries that also appear in installed lists
  unless an explicit migration PR says the overlap is temporary.

The manifest must answer one question: does this capability load by default?
For carried material, the answer is no.

## Demotion Flow

Use this flow when moving a global skill or agent into carried status:

1. Audit the runtime surface and prove it fails the global-install test.
2. Copy the source to the matching `carried/` path.
3. Remove it from the installed manifest list.
4. Add explicit retired-map handling when live install should remove the old
   global copy.
5. Update Claude mirror entries in the same PR or state why no Claude change
   applies.
6. Update the surface inventory and any relevant workflow links.
7. Run `.\scripts\doctor.ps1`.
8. Run `.\scripts\verify-live.ps1 -SkipCodexCommand` when claiming live install
   drift or removal behavior.

Do not demote several unrelated capabilities in one PR. The reviewer should see
the audience decision for each capability.

## Promotion Flow

Use this flow when moving carried material into global install:

1. Show repeated cross-repo or cross-workflow use.
2. Show the invocation moment and audience.
3. Prune carried text before promotion.
4. Move source into the installed runtime path.
5. Add manifest entries and Claude mirror entries.
6. Add or update checks only for proven drift risks.
7. Run validation.

Promotion is not restoration. The promoted version must earn global context
again.

## Project Opt-In

Target projects should opt in from their own repos.

Good opt-in routes:

- copy the carried skill into the target repo's `.agents/skills/<name>`;
- copy the carried agent into the target repo's agent surface when that project
  owns the behavior;
- turn the capability into a plugin when it should be shared across many repos
  without being personal global context;
- keep it as a Compass reference when it is only source material.

Do not make Compass install carried material into every session. That destroys
the distinction.

## Claude Handling

Claude carried material follows the same rule: source can travel, runtime does
not load it by default.

Use `carried/claude/` only when Claude needs runtime-specific wording. If Codex
source is enough, keep the carried source under `carried/codex/` and record the
Claude decision in the demotion or promotion PR.

Do not add carried material to `[claude].skills`, `[claude].derived_skills`, or
`[claude].agents`. Those lists install live runtime context.

## Doctor Checks

Doctor checks cover mechanical boundaries:

- `carried/` is listed as repo-only;
- carried entries are not installed entries;
- carried paths exist when listed;
- carried paths stay outside live install roots;
- demoted live user skills have explicit retirement entries when removal is
  intended.

Do not make `doctor.ps1` judge whether a skill deserves carried status. That is
reviewer judgment.

## Candidate Review State

Do not move a capability just because it appears in an old candidate list.
Current audit packets decide the next move.

Audited global keepers:

- benchmark skills stay global because they prevent expensive long-run collapse;
- WebMCP skills stay Codex-global because they govern a recurring tool surface
  where weak evidence is dangerous;
- `workspace-steward` stays global because workspace mistakes can delete work,
  hide evidence, or point commands at the wrong repo.

Global keepers to audit for pruning instead of demotion:

- `compass`;
- `using-codex-goals`;
- `orchestration-controller`;
- `monitor-to-completion`;
- `root-cause-not-symptom`;
- PR and review loop skills that shape normal repository work.

The first demotion PR should move one audited capability only. It needs current
evidence that the capability fails the global-install test now, not only that
the capability is domain-shaped.
