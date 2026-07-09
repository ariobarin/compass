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

Mixed ledger ordering remains a local candidate: promote a formal ledger shape
only if later runs reproduce the failure. Route new evidence through
`workflows/addition-intake.md` and `workflows/agent-failures.md` rather than
adding another narrative record.
