# Optional Codex Role

[simplicity-critic.toml](simplicity-critic.toml) defines a read-only review role
for finding what can be removed without weakening the intended outcome. Copy
it into your Codex agent definitions if useful. It inherits the model selected
by the caller.

Specialists required by a skill live inside that skill. No Comments supplies
[its own Comment Sicko prompt](../skills/no-comments/references/comment-sicko.md)
to a fresh subagent without requiring a configured custom role.
