# Security Policy

Compass contains reviewed agent skills and working preferences. It should never
contain auth tokens, session data, logs, browser state, generated plugin caches,
SQLite state, or private machine-only runtime files.

## Reporting

Please do not open a public issue for secrets, credentials, private machine
state, or instructions that could expose local data.

Use GitHub private vulnerability reporting if it is enabled. If it is not
available, contact the maintainer privately through the channels listed on their
GitHub profile before posting details publicly.

Useful reports include the affected file or script, the expected boundary, the
observed leak or unsafe behavior, and any command output needed to reproduce the
issue without exposing new secrets.

## Scope

In scope:

- tracked files in this repository;
- the skill catalog, source checks, and optional role definitions;
- guidance that could cause an agent to expose local-only state;
- guidance that could grant stronger authority than the docs explain.

Out of scope:

- private forks or local edits that are not proposed back to this repo;
- untracked runtime state;
- issues in the Codex product or third-party services independent of this
  repository.
