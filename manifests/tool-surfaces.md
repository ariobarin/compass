# Tool Surfaces

This manifest documents tools that may affect portability, host state, network
access, browser state, or external systems. Keep generated config, credentials,
and cache paths out of this repo.

| Surface | Capability | Portable | Risk | Review note |
| --- | --- | --- | --- | --- |
| Shell | Read, write, run commands, start processes | No | High | Controlled by live sandbox and approval policy. Keep command habits in workflows, not hardcoded runtime paths. |
| GitHub CLI | Create repos, push branches, open PRs, inspect checks | Partial | High | Portable docs are fine. Auth state and tokens stay local. |
| Browser plugin | Uses the in-app browser for localhost, file previews, screenshots, DOM inspection, and public web pages | Partial | Medium | Prefer first for localhost and unauthenticated pages. Website allowlists, blocked sites, and any deeper developer-mode or CDP state stay local. |
| Chrome plugin | Uses logged-in Chrome state and browser tabs | Partial | High | Prefer when session state, cookies, extensions, or the regular browser profile matter. Do not commit profile paths or cookies. |
| Computer Use plugin | Controls Windows desktop apps | Partial | High | Useful fallback for visual desktop tasks. Keep runtime paths local. |
| Documents plugin | Creates and edits document artifacts | Partial | Medium | Portable skill knowledge is fine. Generated files belong in task outputs, not config. |
| which-llm plugin | Looks up current model costs, slugs, and benchmarks | Partial | Medium | Install and update route lives in `workflows/which-llm-plugin.md`. Plugin cache and snapshots stay local. |
| Compass MCP app | Serves the reviewed profile and skills to ChatGPT over read-only HTTP tools | Partial | Medium | Source lives in `apps/compass-mcp`. Keep deployment URLs, tunnels, auth, logs, dependencies, and runtime state outside the portable bundle. |
| Third-party MCP servers | Connect to external tools or context over STDIO or HTTP | Partial | High | Keep transport commands, server URLs, OAuth callback settings, env vars, tokens, and per-server tool policy local or project-scoped unless a generic shared default is clearly justified. |
| node_repl MCP | Runs JavaScript and browser automation helpers | No | High | Binary paths, pipes, env vars, and trusted client hashes are machine-local. |
| Web search | Reads current web sources | No | Medium | Use for unstable facts and source attribution. Do not encode search results as permanent rules without review. |
| Skills | Load task-specific instructions, references, scripts, and assets | Yes | Medium | Keep descriptions concise. Move details into `SKILL.md` and references. |
| Agents | Spawn focused Codex sessions with custom instructions | Yes | Medium | Keep agents narrow and explicit. Pure explorers should use read-only sandboxing. Critics that validate behavior can run tools while staying non-editing by role. |
| Hooks | Run trusted commands around Codex tool use and turn closeout | Yes | High | Keep hook code small, local, and reviewed. Hooks must not carry secrets, network calls, machine paths, or auth state. Runtime hooks should fail open when dependencies are missing, with `doctor.ps1` catching invalid portable copies. |
| Review bundle helper | Reads a committed Git diff and explicit repo-relative context, then writes a private bundle outside the checkout | Yes | Medium | Refuses dirty worktrees, partial or oversized diffs, sensitive paths, secret-like content, escaping context, and existing output. Keep generated bundles local and never pass them to a source-blind validator. |
| Restart recovery script | Registers a Windows logon task and can resume saved Codex sessions once per boot | Partial | High | Keep scheduled-task instances, logs, and session state local. Review the script and workflow here, cap resumed sessions, and avoid recurring polling. |

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
