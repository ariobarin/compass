# User preferences

## Writing

- Never use em dashes or en dashes in commits, code comments, prose, or chat. Use other punctuation or separate sentences.

## Git and pull requests

- Commit with one lowercase subject, about 8 words or fewer, with no trailing punctuation, body, or `Co-Authored-By` trailer. Describe changes neutrally without exposing personal preferences.
- Prefer a pull request as the unit for repository changes. Use a descriptive, often verb-led title without conventional-commit prefixes. Keep the body to 0-2 motivation-first sentences with no headers, checkboxes, emojis, or generated footer.

## Runtime routing

- Default new local sessions to GPT-5.6 Sol at medium reasoning. Use high or xhigh only when risk, ambiguity, or verification needs justify the cost.
- Portable subagent role files must omit `service_tier` and inherit the active parent tier when supported.
- If a child does not receive the intended role, model, or effort, treat role routing as unavailable and use a fresh direct run with explicit settings.
- For long-running monitoring that requires model judgment, prefer a fresh non-forked GPT-5.6 Luna worker at xhigh over GPT-5.6 Sol at high. Use `monitor-to-completion` for pure waits.
- Set `fork_turns="none"` unless a child needs parent context.

## Repository and state boundaries

- Keep Claude, Codex, and repo-local configs separate. Never copy secrets, auth, sessions, logs, caches, browser state, generated plugin state, local runtime paths, or provider tokens between tools or into tracked config.
- In a worktree, read and edit only that worktree. Keep one scope per branch or pull request, and preserve unrelated user work.
- Update memory only when the user explicitly asks.

## Browser routing

- Use the in-app Browser for local or unauthenticated pages. Use Chrome when signed-in state, cookies, extensions, existing tabs, or the regular profile matter.

## Windows

- Container entrypoint `.sh` files must use LF line endings. If startup fails with `No such file or directory`, check for CRLF before assuming a missing file or wrong path.
