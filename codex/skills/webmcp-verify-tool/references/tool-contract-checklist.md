# Tool Contract Checklist

Use this checklist while verifying a changed WebMCP tool.

## Registration

- Registers only where it can succeed.
- Unregisters or disappears after route changes where it no longer applies.
- Mutation tools require both authenticated state and target DOM.
- Page-kind comments or inventory explain the scope.
- No central include-everywhere pattern unless the loader gates by page kind.

## Inputs

- Inputs are stable ids, user-visible filters, or real page controls.
- No URL arguments.
- No rendered indexes, virtual-list offsets, or array positions as action inputs.
- No `limit`, `count`, or `per_page` unless the page itself exposes that choice.
- Schema descriptions explain id sources, matching rules, formats, and enum
  meanings.

## Execution

- Declarative tools use real visible forms and spec-defined attributes.
- Imperative tools drive the page's own controls when UI state matters.
- API-backed tools are shaped around a user workflow, not raw backend exposure.
- Navigation tools validate synchronously and handle teardown safely.
- In-place mutations await the observable state change before returning.

## Returns

- One structured value, never `{ content, structuredContent }`.
- Read tools return rows or fields directly.
- Mutations and navigations return a concise outcome object.
- Failures return `{ error: "..." }` or a richer structured error object.
- Status strings are past tense, not instructions or present-progress text.
- No escaped quote noise.

## Descriptions And Annotations

- Tool description is for choosing the tool.
- Input descriptions are for filling arguments.
- Descriptions are short, positive, and distinguish neighboring tools.
- `readOnlyHint` is false for navigators and mutators.
- `untrustedContentHint` is set only for content outside the site author's
  control.

## Live Evidence

- Tool appears on valid page and not invalid page.
- Tool call succeeds through WebMCP runtime.
- Returned structure is inspected.
- DOM or route reflects the effect.
- Mutations persist after relist, reload, or direct API check.
- Dev logs and page errors are checked.
- Site inventory and README departures match the verified live behavior.
- Mirrored eval or schema fixtures match the current callable surface.
