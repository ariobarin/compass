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

## Runtime Routing

- The root session uses GPT-5.6 Sol. Use it for user-facing synthesis,
  orchestration, difficult integration, and work that needs frontier capacity.
- Fresh delegated work uses GPT-5.6 Luna by default. Use `high` for ordinary
  bounded work, `xhigh` for demanding review, validation, or recovery, and
  `max` only for latency-tolerant work that rewards extended proof.
- A Sol child needs a concrete capability reason. Cost or habit alone is not a
  reason.
- Use a fresh non-forked Luna worker for judgment-light monitoring. Use
  `monitor-to-completion` for pure waits so no model spends turns polling.
- Set `fork_turns="none"` unless a child needs exact parent context. Prefer a
  reviewed assignment with named anchors over inherited conversation history.
- Choose role, effort, service tier, and context mode deliberately. Portable
  role files omit `service_tier`; verify effective routing rather than assuming
  inheritance.

## Long-Running Continuity

- Treat compaction and principal replacement as lossy handoffs. Preserve the
  objective in principal-authored goals, plans, catalogs, ledgers, assignments,
  and checkpoints before context pressure forces recovery.
- Delegates own assigned artifacts and return evidence through the named return
  channel. The principal reviews assignments and remains the logical author of
  control state.
- A fresh context must be able to reopen the anchors, verify current state, and
  resume without relying on private conversation history.
- A work catalog may record a blocker immediately. Mark the active Codex goal
  blocked only when the same blocking condition has repeated for at least three
  consecutive goal turns and no meaningful progress remains without user input
  or an external state change. Count the original or user-triggered turn and any
  automatic continuations. After a blocked goal resumes, start a fresh blocked
  audit and require three consecutive resumed goal turns before blocking it
  again. Once those conditions hold, mark the goal blocked instead of leaving it
  active while repeatedly reporting the blocker.

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
