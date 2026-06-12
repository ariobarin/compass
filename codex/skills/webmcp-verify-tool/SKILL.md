---
name: webmcp-verify-tool
description: Verify WebMCP tool changes in the live browser. Use for registration, execution, state, logs, fixtures, and evidence.
---

# webmcp-verify-tool

Use this skill after a WebMCP tool patch, partial, injected script, schema, or
page-scope change. Static review and guessed selectors are not verification.

## Required References

Read both local references:

- [live-verification.md](references/live-verification.md): rebuild or refresh
  paths, headful Chrome, inspector bridge, frontend/API tracing, and evidence
  standards.
- [tool-contract-checklist.md](references/tool-contract-checklist.md): the
  contract checks to apply while verifying a changed tool.

## Verification Loop

1. Confirm the exact served file or injection path that changed.
2. Rebuild, restart, or refresh the correct stack so the live page serves the
   changed code.
3. Open the real page in a WebMCP-capable browser and confirm registration.
4. Invoke the tool through the real action path.
5. Verify the effect through the next DOM observation, returned structure, dev
   logs, persisted state, or direct API evidence.
6. Update the site's inventory, README departures, and any mirrored eval or
   schema fixtures when the verified behavior or scope changed.
7. Confirm those docs and fixtures match the live verified surface before
   calling the change done.

## Output

Report the tool, page, served file, rebuild or refresh step, browser evidence,
return value, before/after state, docs and schema fixtures updated, and
working-tree or commit status. If any step is blocked, say exactly what remains
unverified.
