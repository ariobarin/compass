---
name: benchmark-run-operator
description: Operate benchmark runs with controlled launches, attributable artifacts, valid-row rules, and evidence-based recovery.
---

# Benchmark Run Operator

Use this skill for benchmark execution. It owns launches, process and stack
state, provenance, valid-run rules, selective recovery, and aggregate rebuilds.
It does not own the parent product outcome or rewrite acceptance assertions.
Return benchmark evidence to `using-codex-goals` for completion judgment.

Read the references that match the task:

- [benchmark-protocol.md](references/benchmark-protocol.md): arm definitions,
  comparability, smoke gates, and publication policy.
- [stack-operations.md](references/stack-operations.md): stack health, ports,
  capacity, launch records, and process ownership.
- [artifact-validation.md](references/artifact-validation.md): terminal
  artifacts, valid rows, poison markers, and denominators.
- [report-rebuild.md](references/report-rebuild.md): recomputing summaries from
  attributable artifacts.

## Launch Contract

Before expensive work, record:

- immutable arm and task-set identity;
- model, tool, scorer, seed, and environment configuration;
- stack, port, auth, and worker ownership;
- output root and provenance label;
- smoke proof and stop conditions;
- capacity, budget, and authority limits.

Name one writer for benchmark policy and queue ownership. Other roles may
propose changes, but they do not edit queue policy or relabel provenance without
an exact grant.

## Prove Before Scaling

Run the smallest probe that exercises the real child path. A smoke gate must
prove:

- correct wrapper and arguments;
- healthy target stack and valid port;
- model and tool backend reachability;
- terminal artifact creation;
- scorer completion;
- clean provenance.

A scheduler return, quiet terminal, result directory, or reward alone is not
completion proof.

## Operate The Run

The execution owner holds the shell, child processes, logs, immediate local
recovery, and output root. Keep controller state separate from runtime state.

During execution:

- monitor real completion conditions;
- use `monitor-to-completion` for mechanical waits;
- inspect valid-row pace and error clusters;
- stop only the smallest poisoned slice when provenance remains separable;
- preserve unaffected comparable work;
- record original, rerun, rescore, and manual classifications explicitly.

## Valid Evidence

Count a row only when the harness produced the required terminal summary and
grader result with no uncaught crash, stale-runner marker, missing-summary gap,
or known infrastructure poison. Recalculate strict and headline denominators
from attributable rows.

Do not mix changed task sets, scorers, tool surfaces, auth state, stacks, or
repair conditions without an explicit comparability decision and label.

## Recovery

Classify the failure before another launch: task, tool, evaluator, executor,
stack, provider, auth, capacity, or long-run drift. Use a single row or small
controlled slice to test a changed hypothesis.

Do not launch another symptom-level successor when the failure signature, inputs, and runtime path are materially unchanged and the prior attempt produced no new discriminating evidence.

Open the recovery circuit in that state. Resume only after a changed hypothesis,
input, runtime path, or root-cause finding is recorded and the next probe is
bounded. The orchestration ledger stores this evidence state without retry
counts.

## Pace And Deadline Claims

Report observed valid-row pace, remaining attributable work, available healthy
capacity, and required pace. Do not invent an ETA from scheduler state or
nominal concurrency. If the requested deadline is impossible under observed
conditions, name the gap and the highest-value bounded action.

## Pause And Completion

On pause, stop owned launches and monitors, preserve process and artifact state,
and record the first safe resume action. Do not call pause complete or blocked.

Complete the operator slice only after:

- owned processes reached a terminal state;
- artifacts and provenance passed validation;
- invalid rows were recovered or explicitly excluded with attribution;
- aggregates were rebuilt from the accepted row set;
- the evidence packet identifies exact rows, configs, and artifact roots.

Return that packet to the goal owner. Do not substitute benchmark process
completion for the parent outcome.
