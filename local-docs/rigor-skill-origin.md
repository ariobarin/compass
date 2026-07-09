# Origin of the rigor skill

`codex/skills/rigor` distills the general cognitive posture observed across a
reviewed multi-arm benchmark run. Raw session analysis remains local and is not
part of this repository. This note records why the skill is portable so a
reviewer can inspect the promotion reasoning without importing session state.

## Why it is portable

The skill states the posture in general terms. It carries no task ids, ports,
artifact roots, PIDs, arm names, or model labels from the source run. Those
stay with the run's evidence, not with installed agent behavior.

## What it is not

The benchmark-specific procedural layer from the same evidence (strict count
gates, ledger control, launcher and port provenance, Docker hygiene, pause
semantics) belongs in `benchmark-run-operator` and `using-codex-goals`, not in
this skill. This skill is the general epistemic posture underneath those
applications.

## Promotion reasoning

The moves clear the repo's promotion bar. They name repeated failure modes:
premature closure on a proxy signal, retry instead of root cause, killing on
suspicion, rounding a number toward the goal, and obeying stale automation over
a human decision. They apply beyond the source run, and they are stance-shaped
rather than a project-specific procedure.
