# Origin of the rigor skill

`codex/skills/rigor` distills the general cognitive posture observed in
benchmark thread `019f2412` (the A3 9B five-arm WebArena run). The full
analysis lives outside this repo, under the session analysis path in
`.codex/sessions/_analysis/`. This note records why the skill is portable and
where the evidence is, so a reviewer can see the promotion reasoning without
reading the whole thread.

## Why it is portable

The skill states the posture in general terms. It carries no task ids, ports,
artifact roots, PIDs, arm names, or model labels from the source run. Those
stay with the run's evidence, not with installed agent behavior.

## What it is not

The benchmark-specific procedural layer from the same thread (strict count
gates, ledger control, launcher and port provenance, Docker hygiene, pause
semantics) is promoted through `benchmark-run-operator` and `using-codex-goals`
on the `ario-benchmark-thread-docs` branch, not through this skill. This skill
is the general epistemic posture underneath those applications.

## Promotion reasoning

The moves clear the repo's promotion bar. They name repeated failure modes:
premature closure on a proxy signal, retry instead of root cause, killing on
suspicion, rounding a number toward the goal, and obeying stale automation over
a human decision. They apply beyond the source run, and they are stance-shaped
rather than a project-specific procedure.
