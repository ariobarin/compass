# Agent Topology Experiment

Status: stopped at the observability gate. No child agent was launched because the
available execution environment did not expose a Codex `spawn_agent` tool or an
installed Codex CLI. This report separates source-confirmed behavior from live
measurements and does not invent token or routing data.

## 1. Runtime and version information

| Item | Value |
| --- | --- |
| Inspection date | 2026-07-12 |
| Compass baseline | `main` at `9dc684635a4fbd271e6f33093500b59a9592b3fb` |
| OpenAI Codex source | `main` at `9e552e9d15ba52bed7077d5357f3e18e330f8f38` |
| Official documentation | Current Subagents and Configuration Reference pages inspected on 2026-07-12 |
| Execution host | ChatGPT session with GitHub, web, and Linux shell access |
| Codex CLI | Not installed |
| Codex child-agent tool | Not exposed |
| PowerShell | Not installed |
| Child probes launched | 0 of the maximum 6 |
| Stop condition | Actual child routing and usage metadata could not be observed reliably |

Result classes used below:

- **Live measurement** means evidence from a spawned child thread or its trace.
- **Source-confirmed behavior** means behavior established from the current public
  Codex implementation and official documentation.
- **Proposal** means a candidate policy that was not applied.

## 2. Supported controls discovered

The current MultiAgent V2 source accepts these spawn controls:

| Control | Source-confirmed behavior |
| --- | --- |
| `fork_turns` | Accepts `none`, `all`, or a positive integer string. Omission defaults to `all`. |
| `fork_context` | Rejected in MultiAgent V2. The runtime directs callers to `fork_turns`. |
| `agent_type` | Selects a built-in or configured role for non-full-history spawns. |
| `model` | Selects an available child model for non-full-history spawns. |
| `reasoning_effort` | Selects a supported child effort for non-full-history spawns. |
| `service_tier` | May be requested independently and is validated against the resolved child model. |
| `agents.max_depth` | Official default is `1`. Root is depth 0, so the default permits root to child only. |
| `agents.max_threads` | Official default is `6`. |

Important precedence and rejection behavior:

1. A full-history spawn rejects `agent_type`, `model`, or `reasoning_effort`.
   The error states that the child inherits the parent agent type, model, and
   reasoning effort.
2. A non-full-history spawn starts from the parent turn's effective config.
   Requested model and effort overrides are applied, then the selected role is
   applied as a high-precedence config layer. A role that pins model or effort
   therefore owns those settings.
3. The role layer preserves the current provider and service tier unless the role
   explicitly sets those keys.
4. Service tier validation considers the resolved child config, explicit request,
   and parent turn tier. It keeps the first tier supported by the child model. An
   explicitly requested unsupported tier fails the spawn.
5. Parent runtime choices such as approval policy, permission profile, current
   working directory, environment selection, and execution policy are inherited.

The current Compass roles pin `gpt-5.6-terra` at `high` effort and omit
`service_tier`. The root reviewed config pins `gpt-5.6-sol` at `medium` effort,
omits `service_tier`, sets `max_depth = 2`, and disables hidden spawn metadata.

## 3. Probe matrix

The planned deterministic task was a read-only lookup of one known symbol in one
small file. No prompt or conversation content was recorded.

| Probe | Planned topology | `fork_turns` | Planned routing check | Live result |
| --- | --- | --- | --- | --- |
| 1 | Root to fresh custom child | `none` | Role, model, effort, tier, and zero copied parent rollout | Not launched |
| 2 | Root to recent-context child | `1` | Last-turn context and custom role routing | Not launched |
| 3 | Root to largest inherited child | `all` | Parent inheritance and copied context | Not launched |
| 4 | Sol root to custom Terra child | `none` | Whether role settings replace the Sol parent settings | Not launched |
| 5 | Fresh direct lower-tier run | `none` | Explicit lower model and effort without a role | Not launched |
| 6 | Root to reviewer to specialist | `none` at both hops | Added layer, routing, context, quality, and usage | Not launched |

The preflight found no callable child-agent surface and no local Codex executable.
Continuing would have produced claims without observable role, model, effort, tier,
or token evidence, so the assignment's stop condition was applied before probe 1.

## 4. Results table

These are source-confirmed routing results, not live probe measurements.

| Mode | Parent rollout copied | Role, model, and effort behavior | Context accounting |
| --- | --- | --- | --- |
| `none` | Zero parent rollout items | Custom role and explicit model or effort are allowed. Role-pinned settings take precedence. | Exact tokens unavailable. Child still receives shared instructions, config, runtime policy, environment, and the explicit handoff. |
| Positive integer `N` | A suffix beginning at the last `N` fork-turn boundaries, then filtered | Custom role and explicit model or effort are allowed. | Exact tokens unavailable. If fewer than `N` boundaries exist, the suffix begins at the first boundary and drops pre-turn startup context. |
| `all` | The full persisted parent rollout, then filtered | Custom role, model, and effort overrides are rejected. Parent agent type, model, and effort are inherited. | Exact tokens unavailable. Full-history mode preserves reference context for cached-prefix reuse. |

A fork-turn boundary is a real user message or a turn-triggering inter-agent
communication. Rollback markers are applied before selecting the suffix.

For both integer and full-history forks, the retained rollout is not a raw copy of
every event. The runtime keeps system, developer, and user messages, final assistant
answers, compacted records, event records, and session metadata. It drops reasoning,
tool calls, tool outputs, web calls, image calls, and inter-agent communication
records. Full-history mode also keeps turn context and world state. Truncated forks
drop those reference-context items and rebuild context on the child's first turn.

## 5. Routing failures or hidden metadata

`hide_spawn_agent_metadata = false` does not make the spawn result a routing proof.
The current MultiAgent V2 result contains the task name and optional nickname only.
It does not return:

- actual child role;
- actual model;
- actual reasoning effort;
- actual service tier;
- input, cached input, output, or reasoning tokens;
- child initial context size.

The implementation obtains an internal child config snapshot during spawn, but the
spawn result uses it only to resolve the nickname. A parent cannot establish actual
routing from this result alone.

A valid runtime experiment therefore needs at least one of:

- child-thread details that display the effective role, model, effort, and tier;
- a structured trace or event stream with the effective child config and usage;
- a child self-report backed by runtime metadata rather than model inference.

None of those surfaces was available in this execution environment.

## 6. Context-inheritance findings

`fork_turns = "none"` is fresh with respect to conversation rollout, not empty with
respect to operating context. The child still receives:

- base and developer instructions;
- the parent turn's effective config before role layering;
- the selected role instructions and pinned settings;
- the explicit handoff message;
- current approval, permission, working-directory, environment, and execution policy.

The direct token effect of no-fork routing could not be measured. The source proves
that it copies zero parent rollout items, while integer and full-history modes copy a
filtered variable-size rollout. It does not prove a billing percentage or cached-input
amount for this account and model route.

Inference, not measurement: a compact explicit handoff with `none` should use less
child input than inherited history when the task is self-contained. Full-history mode
may preserve more prompt-cache reuse, so the charged-token difference cannot be
computed from copied item count alone.

## 7. Coordinator-layer findings

No live quality comparison was possible. The topology cost is still mechanically
clear:

| Topology | Spawned children for `K` specialists | Depth | Communication shape |
| --- | --- | --- | --- |
| Direct root to specialists | `K` | 1 | One handoff and one result per specialist |
| Root to reviewer to specialists | `K + 1` | 2 | Root handoff, reviewer dispatch, specialist result, reviewer consolidation |

The reviewer layer has a real contract: remove framing bias, select only relevant
specialists, derive operational constraints, preserve disagreements, and consolidate
specialist-backed findings. That value applies when coordinated selection and
consolidation are part of the request.

The existing `specialist-review` skill already excludes ordinary PR review and uses
the reviewer only for explicit coordinated specialist review. For a task where the
specialist is already known, direct root-to-specialist dispatch is the smallest
source-supported topology. Whether it preserves equal task quality across broader
reviews remains unmeasured.

## 8. Proposed defaults, not applied

1. Keep `fork_turns = "none"` as the normal custom-role route and send a compact
   handoff. This is required when the child must use a different role, model, or
   effort from the parent because full-history mode rejects those overrides.
2. Treat `hide_spawn_agent_metadata = false` as presentation support, not routing
   verification. Require effective child config and usage evidence. When that
   evidence is unavailable, use a fresh direct run with explicit settings and label
   the subagent route unverified.
3. Dispatch a known specialist directly from root. Reserve the reviewer coordinator
   for explicit specialist selection, bias removal, and consolidation. If a later
   live comparison shows no quality loss, reduce `max_depth` to `1`. Do not change
   `max_depth` from this source-only run.

Retain the current omission of `service_tier` from portable role files. The source
supports carrying the active parent tier when the child model supports it and falling
back when it does not.

No lower thread cap is proposed. This run produced no concurrency or fan-out evidence
from which to choose a defensible number.

## 9. Limitations

- No child thread was launched.
- No actual Sol-to-Terra or lower-tier route was observed.
- No role, model, effort, or tier was read from a child runtime.
- No input, cached input, output, reasoning, latency, or tool-call counts were
  available.
- No direct-versus-coordinator task-quality comparison was run.
- Public source behavior may differ from an older installed Codex build.
- The shell could not clone GitHub and had no PowerShell, so local
  `./scripts/doctor.ps1` validation was unavailable. Pull-request CI is the available
  doctor path for this branch.

No raw prompt, conversation content, auth data, session data, or runtime trace was
stored.

## Sources

- [Official Codex Subagents documentation](https://developers.openai.com/codex/multi-agent)
- [Official Codex Configuration Reference](https://developers.openai.com/codex/config-reference)
- [MultiAgent V2 spawn handler](https://github.com/openai/codex/blob/9e552e9d15ba52bed7077d5357f3e18e330f8f38/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs)
- [Shared spawn config and tier logic](https://github.com/openai/codex/blob/9e552e9d15ba52bed7077d5357f3e18e330f8f38/codex-rs/core/src/tools/handlers/multi_agents_common.rs)
- [Forked-thread construction](https://github.com/openai/codex/blob/9e552e9d15ba52bed7077d5357f3e18e330f8f38/codex-rs/core/src/agent/control/spawn.rs)
- [Fork-turn truncation](https://github.com/openai/codex/blob/9e552e9d15ba52bed7077d5357f3e18e330f8f38/codex-rs/core/src/thread_rollout_truncation.rs)
- [Role config layering](https://github.com/openai/codex/blob/9e552e9d15ba52bed7077d5357f3e18e330f8f38/codex-rs/core/src/agent/role.rs)
