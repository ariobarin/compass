# Tool Surfaces

This manifest documents tools that may affect portability, host state, network
access, browser state, or external systems. Keep generated config, credentials,
and cache paths out of this repo.

| Surface | Capability | Portable | Risk | Review note |
| --- | --- | --- | --- | --- |
| Shell | Read, write, run commands, start processes | No | High | Controlled by live sandbox and approval policy. Keep command habits in workflows, not hardcoded runtime paths. |
| GitHub CLI | Create repos, push branches, open PRs, inspect checks | Partial | High | Portable docs are fine. Auth state and tokens stay local. |
| Chrome plugin | Uses logged-in Chrome state and browser tabs | Partial | High | Prefer for debugging when session state matters. Do not commit profile paths or cookies. |
| Computer Use plugin | Controls Windows desktop apps | Partial | High | Useful fallback for visual desktop tasks. Keep runtime paths local. |
| Documents plugin | Creates and edits document artifacts | Partial | Medium | Portable skill knowledge is fine. Generated files belong in task outputs, not config. |
| which-llm plugin | Looks up current model costs, slugs, and benchmarks | Partial | Medium | Plugin source can be documented. Plugin cache and snapshots stay local. |
| node_repl MCP | Runs JavaScript and browser automation helpers | No | High | Binary paths, pipes, env vars, and trusted client hashes are machine-local. |
| Web search | Reads current web sources | No | Medium | Use for unstable facts and source attribution. Do not encode search results as permanent rules without review. |
| Skills | Load task-specific instructions, references, scripts, and assets | Yes | Medium | Keep descriptions concise. Move details into `SKILL.md` and references. |
| Agents | Spawn focused Codex sessions with custom instructions | Yes | Medium | Keep agents narrow and explicit. Pure explorers should use read-only sandboxing. Critics that validate behavior can run tools while staying non-editing by role. |

## Review Checklist

- Does this tool read or write outside the workspace?
- Does it depend on logged-in state, cookies, tokens, local pipes, or runtime
  cache paths?
- Can it mutate GitHub, browser state, files, processes, containers, or cloud
  resources?
- Is the capability needed for the task, or would source reads and scripts be
  enough?
- Should the durable artifact be a workflow, skill, script, manifest entry, or
  local-only config note?
