# Report Rebuild Reference

Use this reference after reruns, top-up recovery, rescoring, or final
aggregation changes when the user wants a refreshed report, comparison CSVs, or
a clear answer about what is still missing for a complete result set.

## Canonical Inputs

Start from the harness's canonical finalized artifacts, not whichever raw run
directories changed most recently.

Prefer sources such as:

- final per-task scoreboard;
- final per-site summary;
- invalid or unscored task inventory;
- paired-valid or shared-success intersection sources;
- the existing report family's README or aggregation notes.

If reruns landed after an older aggregate, inventory and select attempts before
rebuilding the selected aggregate and report.

## Name The Result Set

Use these names before calculating or describing a subset:

- **Intended task population:** the frozen expected task ids for the report.
- **Candidate-attempt union:** every attributable attempt found across original,
  rerun, rescore, and manual-classification roots in the named epoch cohort
  before selection.
- **Accepted valid set per arm:** one selected valid row per arm and task after
  deterministic de-duplication.
- **Paired-valid intersection:** task ids with accepted valid rows in every arm
  being compared.
- **Shared-success intersection:** paired-valid task ids that succeeded in every
  compared arm.
- **Any-arm-success union:** paired-valid task ids that succeeded in at least one
  compared arm.

State the set name, task-id count, row count, denominator, epoch cohort, and
selection rule in every table or export. Use the intended task population for
headline arm success and coverage. Do not silently remove missing or invalid
tasks from that denominator. If the report also shows success among accepted
valid rows, label it separately. Use the paired-valid intersection for paired
deltas and the shared-success intersection for shared-success efficiency.
Report operational candidate-attempt usage across the full candidate-attempt
union separately from comparable accepted-row usage.

An any-arm-success union is a complementary-coverage diagnostic. It does not
replace intended-population or paired-valid headlines, and it is not a
normalized efficiency comparison unless the report defines how non-successful
counterparts are included.

## Evidence Epochs

Assign every candidate attempt to an evidence epoch keyed by the identities that
can change comparability, including agent, harness, task set, scorer, model
policy, tool surface, environment, auth or state policy, and material repair
conditions.

Record a compatibility ruling and name the epoch cohort before selecting rows.
Preserve incompatible historical rows and their artifacts, but exclude them
from current report cells unless the report explicitly presents a labeled
cross-epoch comparison.

## Rebuild Sequence

1. Read the current report contract so the rebuilt output matches local naming,
   CSV schema, and narrative style.
2. Preserve older report snapshots unless the user explicitly wants in-place
   replacement. A fresh report root or archive is safer than mutating
   historical output.
3. Inventory candidate attempts, assign their evidence epochs, and preserve
   parent-attempt identity.
4. Declare the compatible epoch cohort for each comparison.
5. Apply the accepted-attempt selector within that cohort for each arm and task.
6. Regenerate selected canonical per-task aggregates and per-site tables from
   the accepted rows. Label any broader raw inventory as candidate-attempt
   inventory and do not use it for accepted-row checks.
7. Materialize each named result set from the selected canonical rows.
8. For token or efficiency comparisons on shared-success rows, derive the
   aggregate from the already filtered shared-success intersection source so the
   overall and per-site numbers stay aligned.
9. Recompute any missing-valid inventory from the invalid or unscored table
   instead of guessing from headline counts.
10. Confirm every included row belongs to a compatible evidence epoch or a
   documented cross-epoch comparison.

## Required Checks

Before publishing:

- selected row count matches the selected canonical per-task source for the
  named result set and epoch cohort;
- accepted rows match the documented deterministic selector;
- paired-valid or shared-success intersection size matches the generated
  comparison table;
- every output names its result set and evidence epoch scope;
- per-site pass counts match the selected canonical per-site summary for the
  same named result set and epoch cohort;
- caveats mention estimated or missing-token rows only when they truly apply;
- report artifact paths and provenance are stated clearly.

## Output Shape

Report:

- the canonical input artifacts used;
- the refreshed report root or archive path;
- the valid paired or shared-success set size;
- invalid, unscored, and missing counts;
- overall and per-site comparison outputs when applicable;
- any preserved historical snapshot;
- the exact checks used to confirm the rebuild.
