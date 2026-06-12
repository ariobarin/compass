# Live Verification Workflow

Use this when a WebMCP tool change needs proof in a running browser or stack.

## Confirm What Is Served

1. Identify the changed file.
   - Online partial, shared loader, userscript or extension delivery file.
   - Local framework patch, template, module, entrypoint, or proxy override.
2. Identify how the page serves it.
   - Baked Docker image.
   - Bind-mounted source.
   - Injection proxy.
   - Browser extension or userscript delivery.
3. Rebuild, restart, or refresh the correct path.
   - Baked images need rebuild and recreate.
   - Bind mounts may need only process restart or browser reload.
   - Proxies need restart if injection order changed.
4. Prove the live page has the changed code.
   - Inspect served script text, container content, dev logs, or visible runtime
     behavior.
   - Do not infer this from a source diff.

## Browser Verification

Prefer a real headful browser when the user-visible workflow matters.
Prefer headful Chrome with the plugin when existing browser state, extension
delivery, or page-world runtime state matters.

1. Open the page where the tool should register.
2. Confirm WebMCP is available.
3. Check registration.
   - Tool is present on valid pages.
   - Tool is absent on invalid pages.
   - Auth-gated mutations register only when session and target DOM are present.
4. Use inspector evidence first when available.
   - `tab.dev.logs()` for runtime errors and registration logs.
   - `#__webmcp-inspector-state` for page-world registration state.
   - If the state node is missing, verify `/__webmcp/__inspect.js` loads before
     `/__webmcp/__load.js` and restart the proxy if needed.
   - Prefer page-world evidence over isolated automation globals when the two
     disagree.
5. Invoke through the real tool path.
   - Avoid workaround harnesses that bypass the runtime being validated.
6. Observe the outcome.
   - Tool return structure.
   - DOM state after the call.
   - Route or URL if navigation happened.
   - Persistent server state or data visible after reload.

## Frontend And API Evidence

When debugging what a click should do:

- Read frontend code to find the request or state transition produced by the UI.
- Use DevTools network traces to confirm the request, payload, and response.
- Reproduce the API call directly when that is the fastest way to isolate server
  behavior or state persistence.
- Treat direct API replay as a debugging and persistence check, not automatic
  proof that the final WebMCP tool should be a raw API wrapper.
- For the WebMCP tool implementation, prefer driving the page's own widget when
  page state, validation, or event coupling matters. Raw API wrappers are valid
  only when the chosen authoring route is API-backed and the user-visible state
  remains coherent.

## Evidence Standards

Strong evidence:

- Tool registered in the expected page state.
- Tool executed through WebMCP runtime.
- Return value matched the contract.
- The next DOM observation or route reflects the change.
- Mutation persisted across relist, reload, or direct API check.
- Dev logs show no registration or execution errors.
- Tool docs and mirrored fixtures reflect the verified behavior.

Weak evidence:

- Source diff only.
- Static selector review only.
- Benchmark reward only.
- Tool appears in a catalog but was never invoked.
- Invocation returned text but the page state was not checked.

## Blockers

If any blocker prevents live proof, report it directly:

- Browser cannot reach the stack.
- WebMCP runtime is unavailable.
- Proxy or extension is not injecting.
- The service is serving stale code.
- Auth state is missing or expired.
- A required target element is absent.

Do not call the tool verified until the blocked step has evidence.
