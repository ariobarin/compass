# artifacts

Generated evidence and deliverables: reports, exports, logs, screenshots,
scoreboards, run outputs, manifests, and validation packets.

Preserved evidence names:

- source or producing command;
- owner or producer;
- observed date range and time zone;
- relevant commit, build, or target identity;
- secret-scan status;
- retention or archive decision;
- regeneration instructions when practical.

Prefer dated, descriptive folders. Keep recreatable scratch in `../tmp/`. Keep
raw private or secret-bearing output outside tracked files.
