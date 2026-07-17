# User Preferences

## Writing

- Never use em dashes or en dashes in commits, code comments, prose, or chat.
  Use other punctuation or separate sentences.

## Git And Pull Requests

- Commit with one lowercase subject, about 8 words or fewer, with no trailing
  punctuation, body, or `Co-Authored-By` trailer. Describe changes neutrally.
- Prefer a pull request as the unit for repository changes. Use a descriptive,
  often verb-led title without conventional-commit prefixes. Keep the body to
  0-2 motivation-first sentences with no headers, checkboxes, emojis, or
  generated footer.

## Runtime Identity

- This Claude Code setup routes delegated model work through GLM-5.2. Treat
  GLM-5.2 as the only available child model identity.
- Spawn roles deliberately. Do not invent Opus, Sonnet, Haiku, or other model
  tiers from generic Claude examples when the configured gateway does not
  provide them.
- Prefer a fresh narrow subagent for a bounded assignment. Give it reviewed
  anchors, scope, evidence, and a return channel instead of the full parent
  conversation.
- Use a blocking command for pure waits. Use a fresh narrow monitor only when a
  periodic check needs judgment.

## Long-Running Continuity

- Treat compaction and principal replacement as lossy handoffs. Preserve the
  objective in principal-authored goals, plans, catalogs, ledgers, assignments,
  and checkpoints before context pressure forces recovery.
- Delegates own assigned artifacts and return evidence. The user-facing
  principal reviews assignments and remains the logical author of control
  state.
- A fresh context must be able to reopen the anchors, verify current state, and
  resume without private conversation history.

## Planning Authority

- A planning-only request authorizes inspection, research, questions, plans,
  and explicitly scoped experiments. Production implementation begins when the
  user or named authority opens that phase.
- Review material goals, plans, delegation boundaries, and irreversible actions
  before launch unless the user already granted or waived that review.

## Repository And State Boundaries

- In a worktree, read and edit only that worktree. Keep one scope per branch or
  pull request, and preserve unrelated user work.
- Prefer the smallest coherent change that fixes the owning boundary. After a
  repair, review for removable guards, wrappers, duplicate state, and obsolete
  paths.

## Windows

- Container entrypoint `.sh` files use LF line endings. When startup reports
  `No such file or directory`, inspect line endings before assuming a missing
  path.
