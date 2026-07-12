# User preferences

## Writing style
- Never use em dashes or en dashes anywhere: commits, code comments, prose, chat replies. Use a regular hyphen, comma, colon, parentheses, or two sentences instead.

## Commit messages
- Single short lowercase subject line, around 8 words or fewer. No body, no `Co-Authored-By` trailer.
- Past-tense imperatives like "add", "fix", "move", and "return" are fine. No trailing punctuation, no leading capital.
- Do not name personal preferences in commit messages or other public artifacts. Describe changes neutrally, such as "clean up tool docs".

## Pull requests
- Make them and add to them often. When something should be updated, a pull request is usually the right unit.
- Descriptive title, often verb-led. No `feat:`, `fix:`, or `chore:` prefixes. Title need not match the commit subject.
- Body is optional and minimal: 0-2 sentences, lead with motivation or why, not what changed. Empty body is fine.
- No markdown headers, checkboxes, emojis, or "Generated with Codex" footer.

## Workflow
- Keep moving on work already in scope. Return for a decision, completion, or a material question, not routine steps.
- Plan non-trivial changes briefly, then verify the changed behavior with real output, logs, or a live browser check when applicable.
- Use subagents only when they save tokens or improve the result.
- Default new local sessions to GPT-5.6 Sol at medium reasoning. Escalate to high or xhigh only when material risk, ambiguity, or verification evidence justifies the added cost.
- For simple tasks, prefer non-forked subagents with lower reasoning effort when delegation is still useful.
- Portable subagent role files must omit `service_tier`. Do not force Fast or Flex. Inherit the active parent tier when the runtime supports it.
- Confirm a spawned child actually received the intended role, model, and reasoning effort. If MultiAgent V2 hides routing controls or the child inherits the parent Sol settings, treat role routing as unavailable and use a fresh direct run with explicit settings.
- For long-running monitoring that still requires model judgment, prefer a lower model tier at higher effort, currently GPT-5.6 Luna at xhigh, over GPT-5.6 Sol at high. Keep the worker fresh and non-forked. Pure waits belong in `monitor-to-completion`.
- Set `fork_turns="none"` unless a subagent must inherit the parent context.
- Prefer a script, CLI, or API path over handing routine manual steps back to the user.
- Keep Claude, Codex, and repo-local configs separate. Never copy secrets, auth, sessions, logs, caches, browser state, generated plugin state, local runtime paths, or provider tokens between tools or into tracked config.
- In a worktree, read and edit that worktree's own files. Keep one scope per branch or PR and preserve unrelated user work.
- Read frontend code to find the API call a click produces and reproduce it directly.
- For browser debugging, use the in-app Browser for local or unauthenticated
  pages. Use Chrome when signed-in state, cookies, extensions, existing tabs,
  or the regular profile matter.
- Fix root causes, reuse existing mechanisms, and keep docs aligned with behavior. Update memory only when the user explicitly asks.

## Windows host
- Any `.sh` script that serves as a container entrypoint must be written with LF-only line endings. CRLF causes the container to exit immediately with a misleading "No such file or directory" on the entrypoint because the kernel tries to exec `/bin/sh\r`. If a container exits on start with that error, check line endings before assuming a missing file or wrong path.
