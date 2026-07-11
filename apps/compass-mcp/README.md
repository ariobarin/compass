# Compass MCP app

This directory exposes the reviewed Compass profile and skills as a read-only MCP server for regular ChatGPT conversations.

At initialization, the server includes the reviewed user profile plus every skill name, description, and source path. This mirrors the native Codex harness: select a workflow from the available catalog without a discovery call, then load only that workflow's full `SKILL.md` before applying it.

## Tools

- `get_profile` re-reads `codex/AGENTS.md` for explicit inspection or freshness checks. The profile is already present in initialization instructions.
- `list_skills` re-reads the reviewed skill catalog for explicit inspection or freshness checks. Skill summaries are already present in initialization instructions.
- `get_skill` loads one full `SKILL.md` after a workflow is selected.
- `search` and `fetch` expose the same content through the standard read-only knowledge shapes.

The app does not install global config, run hooks, mutate the repository, or create subagents. Native subagents remain a host capability. A later server-side workflow can add explicit multi-agent execution without pretending it is native ChatGPT delegation.

## Run locally

Use Node.js 20 or later.

```bash
cd apps/compass-mcp
npm install
npm run build
npm run smoke
npm run dev
```

By default the server finds Compass three directories above its source or compiled output. Set `COMPASS_ROOT` to point at another reviewed checkout. Set `HOST` and `PORT` to change the listener.

The local endpoint is `http://127.0.0.1:3000/mcp`. The health check is `http://127.0.0.1:3000/healthz`.

## Connect ChatGPT

ChatGPT developer-mode apps require an HTTPS MCP endpoint. Deploy this directory with the Compass repository available at runtime, or expose the local server through a secure tunnel. Create a developer-mode app with its MCP URL ending in `/mcp`, then add Compass from the conversation tools menu.

When a tunnel or reverse proxy forwards a public hostname to the default localhost listener, set `ALLOWED_HOSTS` to a comma-separated list of accepted hostnames. Include the local address when local probes or the smoke client also connect directly:

```bash
ALLOWED_HOSTS=127.0.0.1,localhost,compass.example.com npm start
```

Values are hostnames only, without schemes, paths, or ports. Leaving `ALLOWED_HOSTS` unset preserves the SDK's automatic localhost-only DNS-rebinding protection.

The server is intentionally unauthenticated and read-only. Add authentication before exposing private Compass content or per-user configuration.
