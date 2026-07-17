# Benchmark Run Evidence

This repo-local record explains the benchmark and goal guidance promoted from a
reviewed run. Raw logs, artifacts, session state, auth, and machine paths stay
local.

| Evidence | Durable response | Surface |
| --- | --- | --- |
| Full launches needed named arms, smoke gates, monitors, and stop conditions. | Require a launch contract and proof gates before expensive spend. | `benchmark-run-operator` |
| Terminal artifacts could conceal missing tools, wrong routes, or other infrastructure poison. | Validate related logs and strict denominators before headline counts. | `artifact-validation.md` |
| Timeout, poison, and forced-stop rows needed recovery or explicit exclusion. | Treat invalid rows as attributable recovery work, not presentation caveats. | `benchmark-run-operator` and `artifact-validation.md` |
| Repair launches depended on working wrappers, upstream health, port validity, and ownership. | Reuse proven launch records and stop the smallest poisoned slice. | `stack-operations.md` |
| Observed valid-row pace contradicted requested deadlines. | Report observed and required pace, then act on the rate gap. | `benchmark-run-operator` and `stack-operations.md` |
| A user pause had to stop owned work and monitors without claiming completion. | Preserve resume state and keep pause distinct from completion or blockage. | `using-codex-goals` and `goal-contracts.md` |
| A prep-only child amended and reconstructed a controller-owned control file from partial context. | Require one named writer, exact edit authority, revision checks, and preservation after a mismatch. | `orchestration-controller` and `benchmark-run-operator` |
| A long-running goal kept producing work after compaction while control files became contradictory. | Require precedence-ordered inputs, one small live surface, explicit re-anchoring, and split controller and execution ownership. | `using-codex-goals`, `goal-contracts.md`, and `orchestration-controller` |
| Recovery successors passed narrow gates but repeated an unchanged real child failure path. | Open recovery when no new discriminating evidence exists, and resume only after the hypothesis, inputs, runtime path, or root-cause evidence changes. | `benchmark-run-operator` and `orchestration-ledger` |

The control-file overwrite and repeated recovery failures justified promoting
writer, revision, delegated edit, and evidence-based recovery state into the
local orchestration ledger. Route new evidence through
`workflows/addition-intake.md` and `workflows/agent-failures.md`.
