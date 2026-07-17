# Behavior Validation Report Schema

Use this shape when a principal, reviewer, or script will consume the result.
The report records exactly which isolated workspace and target were tested.

```json
{
  "schema_version": 2,
  "tested_at": "ISO 8601 timestamp with timezone",
  "workspace": {
    "manifest_sha256": "hex digest",
    "allowed_local_paths_checked": true
  },
  "target": {
    "surface": "string",
    "identity": "exact build, ref, version, or artifact",
    "user_posture": "string"
  },
  "contract": {
    "path": "contract.md",
    "revision": "string or null"
  },
  "source_blind": true,
  "contaminated": false,
  "summary": {
    "pass": 0,
    "fail": 0,
    "blocked": 0,
    "out_of_scope": 0
  },
  "clauses": [
    {
      "id": "BV-1",
      "status": "pass | fail | blocked | out_of_scope",
      "steps": ["string"],
      "observed": "string",
      "evidence": ["redacted locator or compact observation"],
      "finding": "string or null"
    }
  ],
  "anti_cheat_probes": [
    {
      "probe": "string",
      "observed": "string",
      "result": "pass | fail | blocked"
    }
  ],
  "blockers": ["string"],
  "remaining_proof_gaps": ["string"]
}
```

Keep credentials, cookies, tokens, private user data, raw session logs, source,
and implementation details outside the report. When implementation material
becomes visible, set `source_blind` to `false`, set `contaminated` to `true`,
record what was exposed, and stop. A contaminated report cannot close the
behavior gate.
