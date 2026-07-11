# Behavior Validation Report Schema

Use this shape when another agent or script will consume the result.

```json
{
  "schema_version": 1,
  "target": {
    "surface": "string",
    "identity": "string",
    "user_posture": "string"
  },
  "contract": {
    "path": "string or null",
    "inline": false,
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
  "anti_cheat_probes": ["string"],
  "blockers": ["string"]
}
```

Do not place credentials, cookies, tokens, private user data, raw session logs,
or implementation details in the report. When contamination occurs, set
`source_blind` to `false`, set `contaminated` to `true`, and do not count that run
as the behavior gate.
