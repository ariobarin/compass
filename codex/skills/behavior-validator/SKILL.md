---
name: behavior-validator
description: "Source-blind behavior validation against a written contract for apps, CLIs, APIs, and generated artifacts."
---

# Behavior Validator

Validate the real user or operator surface against a written contract without
seeing how it was implemented. Read the contract first, exercise the target, and
try to falsify each claimed behavior. Do not inspect source files, diffs, tests,
git history, implementation notes, or review bundles.

If implementation material becomes visible, mark the run contaminated and
restart with a fresh validator. A plausible implementation is not behavioral
proof, and a clean source-aware review does not satisfy this gate.

## Contract

Use a prewritten behavior contract. If none exists, write a short contract from
the user request before touching the target. Use
[contract-template.md](references/contract-template.md) when the behavior has
more than one clause or needs reusable evidence.

The contract must name:

- the target and user posture;
- setup, fixtures, credentials, and allowed tools;
- observable clauses that can pass or fail;
- anti-cheat probes that distinguish real work from static success text;
- evidence required for each clause;
- explicit exclusions and decision-owned behavior.

Do not silently weaken the contract after seeing the result. A product decision
may revise it, but record the revision before rerunning the affected clauses.

## Isolation Boundary

Work from a source-blind directory or host context whenever practical. Carry
only the contract, allowed fixtures, credentials through approved secret
handling, and redacted captured evidence. Do not copy repository source, test
fixtures that reveal implementation, review reports, or branch history into the
validator workspace.

Use only observable surfaces:

- browser or accessibility interactions;
- CLI commands and documented exit behavior;
- API requests and responses;
- generated files, documents, images, or reports;
- public or operator-visible logs and status output.

If source access is truly required to proceed, stop with
`blocked_source_required`. Do not cross the boundary and still call the result
source-blind.

## Validation Loop

1. Parse the contract into clauses, setup, user tasks, anti-cheat probes, and
   evidence requirements.
2. Prepare the target without reading implementation. Another worker may launch
   a build or service, but it must not explain the code path to the validator.
3. Execute each task as the intended user or operator would.
4. Vary data and state where useful: refresh, retry, empty and invalid input,
   changed fixtures, persistence, restart, and generated-output inspection.
5. Record compact redacted evidence. Never capture credentials, cookies, tokens,
   private user data, or unrelated logs.
6. Mark every relevant clause `pass`, `fail`, `blocked`, or `out_of_scope`.
7. After a repair, rerun the affected clauses and nearby regression probes with a
   fresh source-blind validator when the prior run was contaminated.

## Findings

Fail a clause when the observable result violates the contract, the task cannot
be completed, success is fake or static, persistence is missing, or the evidence
does not support the claim.

Block only for a concrete missing runtime dependency such as access, credentials,
fixtures, network, or a required tool. Mark behavior out of scope only when the
contract excludes it or a user-owned product decision remains open.

Reject code quality, architecture, naming, and implementation-style concerns.
Those belong to source-aware review.

## Report

Use [report-schema.md](references/report-schema.md) for machine-readable output.
A normal report includes the target exercised, contract used, clause totals,
accepted findings with reproduction steps and evidence, anti-cheat probes,
contamination state, and remaining blockers.
