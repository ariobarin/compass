# Agent Signal And Measurement

This document defines one evidence path for prompt compression, orchestration
protocols, agent routing, session traces, and compaction accounting. It
deliberately separates behavioral quality from quantities that are easy to
count.

## Decision Principles

1. **Preserve role signal before reducing text.** Reduction is acceptable only
   when the agent's stance, failure mode, non-negotiable behavior, evidence
   standard, authority boundary, and output contract remain unmistakable.
2. **Treat static prompt measurements as inventory.** Bytes and estimated tokens
   describe deployment surface. They do not establish clarity, redundancy, or
   behavioral equivalence.
3. **Keep ordinary continuation implicit.** An active owner continues while safe,
   authorized work remains. Model-facing acknowledgements must not become a
   permission gate at each turn boundary.
4. **Separate host state from worker reports.** The runtime owns lifecycle state.
   Completion claims, input requests, external waits, and failure reports are
   evidence for routing rather than self-authorizing transitions.
5. **Keep structural causality without retaining content.** A useful trace must
   connect parent, child, role, route, tool phase, outcome, and token mechanics.
   Prompts, messages, reasoning text, commands, paths, repository names, and tool
   output remain excluded.
6. **Keep compaction accounting mechanical.** Token replay can estimate context,
   cache categories, and compaction frequency. It cannot infer whether the right
   requirement, caveat, or piece of evidence survived.
7. **Make a routing, protocol, or compression change only after a behavior
   comparison.** A smaller prompt or cheaper route is a secondary benefit, not
   the acceptance criterion.

## Prompt Signal Floor

A routed agent or skill should make all six items clear in its primary loaded
surface:

- **Stance:** the directional bias that distinguishes the role.
- **Named failure mode:** the behavior the role is designed to prevent.
- **Non-negotiable behavior:** the few actions or refusals that must survive
  ambiguity and pressure.
- **Evidence standard:** what must be inspected, executed, or cited before a
  claim is accepted.
- **Authority boundary:** what the role owns and what it must not take over.
- **Output contract:** the decision or evidence shape returned to the caller.

A reference may add examples and detail, but it should not be the only place
that defines the role. Deliberate repetition is justified when it protects
independence, evidence, ownership, or stop conditions.

## Orchestration Protocol

Keep the state machine around the model rather than turning conversational
sentinels into the model's working rhythm.

- Ordinary continuation is implicit while safe, authorized work remains. A
  worker should not stop for an acknowledgement or permission-to-proceed token.
- The controller sends no worker-directed message while a worker is making
  coherent progress under a clear owner, boundary, and evidence gate.
- Controller messages should change the route: supply exact input, correct the
  objective, add a constraint, hold, cancel, reassign, request review, or direct
  a concrete recovery.
- Resume is a typed runtime action after a real suspension. It should identify
  the interrupted run and carry the condition or payload that changed.
- Runtime lifecycle state is machine-owned. Derive queued, running, suspended,
  waiting on an external dependency, completed, failed, and cancelled from
  process events, tools, explicit actions, and named dependencies.
- A worker report is a claim, not lifecycle authority. Use a small terminal or
  exceptional result vocabulary: completed, needs input, waiting on an external
  dependency, or failed. Keep remaining concerns in a separate field.

Do not use a bare continuation acknowledgement, make a progress label a
condition for retaining ownership, or treat a completion word, blocker word,
negative-result word, or review-wait word as a self-interpreting control
decision. A negative search result is content; pending review is a named
dependency; completion still requires matching evidence.

A completion or exception report should carry the result summary, evidence,
remaining concerns, and, when progress cannot continue, the exact dependency or
failed action, recovery tried, current state, smallest unblock, and next owner.
A routine progress checkpoint is nonterminal and should preserve the same owner
without an acknowledgement round trip.

### Protocol Comparison

Evaluate the protocol independently from prompt compression. Compare at least:

1. an acknowledgement/status-token baseline;
2. autonomy-first execution with implicit continuation; and
3. autonomy-first execution with typed completion and exception actions.

Include long tool runs, misleading first plans, recoverable local failures,
genuine missing input, external waits, and tasks whose correct result is no
change or no finding. Measure verified completion, false completion, premature
returns, unnecessary controller-worker messages, blocker precision, recovery
attempts, stale-plan persistence, repeated work, tokens, and elapsed time. Also
permute legacy label order and spelling in the baseline; sensitivity to those
incidental choices is evidence that the protocol is not representing stable
state.

## Static Inventory

Run:

```powershell
python scripts/prompt-inventory.py
python scripts/prompt-inventory.py --json
```

The inventory reports repository-owned prompt surfaces, activation mode, byte
and character counts, deterministic token estimates, agent model/effort routes,
and skill routing-description size. It does not label instructions as too
strong, declare clauses duplicates, assign prompt budgets, or fail a build based
on size.

Use inventory deltas to locate a change for review. Do not use them as proof that
signal was preserved.

## Content-Free Session Trace

Run:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$sessions = Join-Path $codexHome "sessions"
$traceDir = Join-Path ".local" "agent-signal-measurement"
$traceFile = Join-Path $traceDir "traces.jsonl"
New-Item -ItemType Directory -Force -Path $traceDir | Out-Null
python scripts/session-trace.py $sessions --output $traceFile
python scripts/session-trace.py $sessions --summary
```

Schema version 2 emits export-scoped structural metadata. Every invocation uses
a fresh random HMAC salt that is not written to the trace. Identifiers can be
joined within one export, but the same session or child receives a different
pseudonym in a later export.

The allowlist includes:

- export-scoped session, actor, parent, and operation pseudonyms;
- child ordinal and event order;
- fixed role categories, including Compass specialist roles;
- requested and effective model, reasoning effort, service tier, and fork mode;
- fixed tool category, phase/status, duration, and content-free token size;
- turn or agent outcome and fixed failure class;
- compaction reason plus pre/post context size;
- input, cache-read, cache-write, output, reasoning, tool-output, active-context,
  and child-inherited token fields when the source reports them.

The exporter excludes message bodies, prompts, assistant text, reasoning text,
tool output, commands, tool names, working directories, repository names, raw
paths, originator data, secrets, and raw identifiers. Warnings contain only a
fixed code and line number.

Role and route fields are structural metadata, not arbitrary copied strings.
Unknown roles are reduced to `custom`; tool names are reduced to a fixed
category; outcomes and failures are reduced to fixed classes. Host-observed
outcomes remain separate from conversational completion or exception claims.

## Routing And Compression Experiment

### Baseline And Candidate

Compare one current baseline with one candidate at a time. Freeze the task set,
repository revision, tool permissions, model availability, and scoring rubric.
Do not combine prompt compression, topology changes, model changes, and
compaction changes in one treatment unless the goal is explicitly to measure the
combined system.

### Task Set

Use representative tasks that exercise the role's defining failure mode, not
only ordinary happy paths. Include:

- cases where the leading narrative is wrong;
- cases where a confident completion report is unsupported;
- cases with a real blocker and cases with a recoverable local next move;
- cases where reuse exists and cases where custom work is justified;
- cases where external current evidence changes the answer;
- cases with no valid finding, so false-positive pressure is visible.

Keep task authors and evaluators separate where practical. Randomize treatment
order and hide the prompt variant from the evaluator.

### Behavioral Measures

Record at least:

- critical-finding recall and false-positive rate;
- evidence-to-claim match;
- instruction or authority-boundary violations;
- role separation and independent minority findings;
- unsupported consensus, takeover, premature-stop, or stale-plan behavior;
- premature worker returns and acknowledgement-only coordination turns;
- precision of missing-input, external-wait, and failure reports;
- correction count, review misses, and verification misses;
- task outcome and fixed failure class.

Then record secondary operational measures:

- input, cached input, cache writes, output, and reasoning tokens;
- latency and retries;
- agent spawns, fork mode, and inherited context;
- compactions and active context;
- requested versus effective model, effort, and tier.

Do not declare equivalence from a small mean difference alone. Inspect the worst
role-defining failures and uncertainty around the comparison. A candidate should
not ship when the aggregate result looks neutral but the defining anti-drift
behavior regresses.

### Decision Gate

A candidate is eligible only when:

1. the prompt signal floor is present;
2. no material authority or safety boundary regresses;
3. defining behavioral measures are no worse within the experiment's stated
   uncertainty;
4. any operational gain is measured rather than inferred from static size; and
5. residual risks and missing coverage are recorded.

## Compaction Accounting

Run:

```powershell
$traceFile = Join-Path (Join-Path ".local" "agent-signal-measurement") "traces.jsonl"
python scripts/compaction-accounting.py $traceFile
python scripts/compaction-accounting.py $traceFile --thresholds 64000,96000,128000 --json
```

The accounting model reports, for each threshold:

- simulated compaction and overflow counts;
- average and maximum pre-turn context;
- logical, uncached, estimated cache-read, and estimated cache-write input;
- ordinary, reasoning, and tool output;
- retained root-context additions and child-inherited context separately;
- simulated post-compaction context size;
- field coverage and mechanical warnings.

Prompts below the configured cache minimum do not seed reusable cache prefixes.
After a turn-level observed compaction, retained ordinary and tool output are
included in the observed baseline so the next turn does not count them again.
Reasoning output and child-inherited context are reported but are not assumed to
grow the root context.

The tool emits no semantic-risk score, confidence label, Pareto frontier, or
threshold recommendation. Use it to select useful points for a separate quality
experiment, not to select a production threshold by itself.

## Decision Record

For each accepted change, record:

```text
Change:
Baseline:
Candidate:
Control protocol variant:
Defining failure mode tested:
Task set and exclusions:
Behavioral result:
Operational result:
Worst observed regression:
Missing coverage:
Decision and owner:
Rollback signal:
```

A dated decision record should stay shorter than the evidence it points to. Raw
experimental output can remain generated or local rather than becoming a large,
speculative policy document.
