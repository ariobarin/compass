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
| A prep-only child amended and then reconstructed a controller-owned Markdown control file from partial context, creating competing revisions. | Require one named writer, exact edit authority for delegated roles, prior-revision checks, and preservation instead of reconstruction after a mismatch. | `orchestration-controller` and `benchmark-run-operator` |
| A long-running goal kept producing work after compaction while its control files had become large, contradictory, and partly historical. | Require precedence-ordered authoritative inputs, one short mutable-state surface, explicit re-anchoring after compaction or handoff, and restoration of split controller and execution ownership. | `using-codex-goals`, `goal-contracts.md`, and `orchestration-controller` |
| Repeated recovery successors passed narrow gates but failed at different layers of the real child runtime. | Stop after two consecutive successor failures and prove the complete child path before another launch. | `benchmark-run-operator` |

The control-file overwrite and repeated recovery failures justified promoting
writer, revision, delegated edit, and recovery circuit state into the local
orchestration ledger. Route new evidence through `workflows/addition-intake.md`
and `workflows/agent-failures.md` rather than adding another narrative record.
