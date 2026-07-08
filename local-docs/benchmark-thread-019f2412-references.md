# Benchmark Thread 019f2412 Evidence Extracts

Status: repo-local reviewed extraction for future Compass changes.

Source thread: `019f2412-2c4e-7230-ba78-99386a0e546d`.

Do not commit raw session logs, run artifacts, shell transcripts, auth state,
local benchmark roots, or generated session state into Compass. Use this file as
a compact evidence extract, then promote only portable guidance through the
existing Compass workflow surfaces.

## Reviewed Evidence Classes

| Evidence class | What the thread showed | Portable lesson |
| --- | --- | --- |
| Launch contract | The run needed named arms, task set, smoke gates, monitor expectations, and stop conditions before full launch. | Expensive benchmark launches need an up-front contract and proof gates before full spend. |
| Full authority | Once the user removed approval blockers, the useful response was local action plus continued evidence checks. | Full authority should increase action pressure, not reduce verification standards. |
| Strict reconciliation | Deeper scans found terminal artifacts whose related logs proved missing tools, wrong routing, or other infrastructure poison. | Headline counts need related-log validation, not terminal artifacts alone. |
| Live repair loop | Invalid rows became marked exclusions, rescored cases, or smallest safe replacement slices while healthy lanes continued. | Invalid benchmark rows are recovery work until classified, repaired, or proven unsafe. |
| Stack provenance | Repair attempts depended on live upstream services, wrapper compatibility, derived ports, Docker ownership, and working launch records. | Repair launches should inherit provenance from active run records or known-good scripts. |
| Rate honesty | ETA claims changed after strict valid-row pace and required pace were recalculated. | Status should state observed pace, required pace, and the action taken when they diverge. |
| Pause control | Explicit user pause stopped owned workers, neutralized monitors, preserved artifacts, and left forced-stop rows uncounted. | User pause authority overrides automation, but it is not proof of original objective completion. |
| Ledger ordering | Mixed status ordering made old sections look current during continuation work. | Long-run ledgers need one obvious latest-state block and a stable ordering rule. |

## Evidence To Change Matrix

| Evidence class | Candidate change | Why it is not project-specific |
| --- | --- | --- |
| Terminal artifact with infrastructure poison | Tighten artifact validation to require related-log checks before headline counts. | Any tool-augmented benchmark can produce a terminal artifact after an invalid tool path. |
| Timeout before summary write | Treat missing-summary timeout rows as recovery work that needs exclusion or repair provenance. | Any long benchmark can lose rows through process timeouts before summary write. |
| Mixed status ordering | Require one latest-state block and stable ordering in long-run ledgers. | Any long-running workflow can mislead future agents with stale visible headers. |
| Proxy or port health mismatch | Add stack-operation caution about verifying upstream services, not only proxy listeners or free ports. | Any proxy-backed stack can listen while upstream is unavailable. |
| Wrapper drift | Prefer active parent command lines and working launcher records over checkout assumptions. | Long runs can outlive branch checkouts or wrapper revisions. |
| Explicit pause plus heartbeat | Add goal guidance for pause state and monitor neutralization. | Any durable goal with automation can violate a user stop unless pause authority is explicit. |
| Model latency under lane cap | Report bottleneck evidence before scaling concurrency. | Any model-backed benchmark can be throughput-bound outside Docker capacity. |

## Promoted Skill Surfaces

| Target | Installed use |
| --- | --- |
| `codex/skills/benchmark-run-operator/SKILL.md` | Treat the run ledger as the control surface, keep invalid rows as recovery work, and report strict pace honestly. |
| `codex/skills/benchmark-run-operator/references/artifact-validation.md` | Add related-log checks, exclusion ancestry, denominator-unit naming, and infra-poison separation from valid task failures. |
| `codex/skills/benchmark-run-operator/references/stack-operations.md` | Add launcher provenance, upstream health, poisoned-parent, pace, and Docker cleanup cautions from the repair launches. |
| `codex/skills/using-codex-goals/SKILL.md` | Clarify how explicit user pause interacts with durable goals and heartbeat monitors. |
| `codex/skills/using-codex-goals/references/goal-contracts.md` | Add copyable pause and stop authority language for controller, runner, monitor, and subagent contracts. |

## Remaining Candidate Targets

| Target | Proposed use |
| --- | --- |
| `workflows/agent-failures.md` | Record failures for stale ledger ordering, raw count drift, and arbitrary repair offset launches if these recur in later runs. |

## Review Questions

- Should Compass add a benchmark-ledger template, or is the existing
  `benchmark-run-operator` output contract enough after a short tightening?
- Should goal tooling gain a distinct paused state, or should installed guidance
  explain how to preserve resume state without completing the objective?
- Should benchmark docs require a separate evidence extract for thread-derived
  lessons before they can become installed skill text?

## Verification Notes For Future Changes

- If only local docs change, run `.\scripts\doctor.ps1` and
  `git diff --check`.
- If installed benchmark or goal skills change, run `.\scripts\doctor.ps1` plus
  the local skill validator for each edited skill when available.
- If goal guidance changes, check `codex/skills/using-codex-goals` and any
  Compass-owned references or manifests that apply.
- Do not run live install checks unless the PR claims live drift or install
  behavior. Local docs can remain source-only evidence.
