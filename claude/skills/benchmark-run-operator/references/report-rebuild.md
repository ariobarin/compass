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

If reruns landed after an older aggregate, rebuild the final aggregate first,
then rebuild the report from that aggregate.

## Rebuild Sequence

1. Read the current report contract so the rebuilt output matches local naming,
   CSV schema, and narrative style.
2. Preserve older report snapshots unless the user explicitly wants in-place
   replacement. A fresh report root or archive is safer than mutating
   historical output.
3. Regenerate the canonical aggregate and per-site tables from the current
   validated artifacts.
4. Build report tables from canonical final outputs, not from partial rerun
   folders or ad hoc counts.
5. Separate valid paired rows, invalid rows, unpaired or unscored rows, and
   rerun or rescore provenance.
6. For token or efficiency comparisons on shared-success rows, derive the
   aggregate from the already filtered shared-success intersection source so the
   overall and per-site numbers stay aligned.
7. Recompute any missing-valid inventory from the invalid or unscored table
   instead of guessing from headline counts.

## Required Checks

Before publishing:

- total row count matches the canonical per-task source;
- paired-valid or shared-success intersection size matches the generated
  comparison table;
- per-site pass counts match the canonical per-site summary;
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
