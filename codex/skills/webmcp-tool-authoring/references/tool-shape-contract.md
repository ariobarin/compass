# WebMCP Tool-Shape Contract

This contract supersedes older notes that told action tools to return
`{ content: [] }`. Current WebMCP tools return one structured value.

## Site Layout Assumptions

Each site should maintain:

- A page-kind inventory: page taxonomy and target tool list.
- A README or notes file: decisions, departures, and open questions.
- Tool code colocated with the page kind where possible.
- Representative snapshots or examples when selectors are fragile.

For online sites, a shared loader usually detects the page kind, loads one
partial, registers tools with an abort signal, and re-registers on route changes.
For local Docker sites, tools are often baked into framework templates or an
injected script.

## Core Rules

1. List and act are separate.
   - `list_X` returns rows with stable ids.
   - `act_on_X` accepts a stable id from `list_X`.
   - Never combine list and mutate in one tool.
2. Stable id is the action handle.
   - Do not accept rendered indexes, array positions, virtual-list offsets, or
     `data-index` values as inputs.
   - Ordinals may appear in output only when they are real page content or
     same-turn labels.
3. Register only where the tool works.
   - If a button, form, modal, or session is required, gate registration on that
     state.
4. No URL parameters.
   - Read `window.location` and current DOM state instead of asking the agent for
     URLs.
5. Login is not a tool.
   - Login-gated mutations register only when authenticated state and target DOM
     are present.
6. No `limit` on read tools unless the page itself exposes that choice.
   - Return what the page presents by default.
   - Keep substantive user-driven filters such as search, state, date, and
     category.
7. One structured return value.
   - Read tools return rows or objects.
   - Mutations and navigations return small outcome objects.
   - Failures return objects with an `error` field.
   - Do not wrap results in `{ content, structuredContent }`.
   - Do not `JSON.stringify` structured data into a string.
8. Descriptions split selection from arguments.
   - Tool description tells the agent when to choose the tool.
   - Input schema descriptions tell the agent how to fill arguments.
   - Keep descriptions short, positive, and behavioral.
   - Do not repeat enum values or argument lists in the tool description.
9. Annotation behavior must be true.
   - `readOnlyHint` is false for navigators and mutators.
   - `untrustedContentHint` is only for content outside the site author's
     control, such as user-generated text or external search snippets.
10. Avoid quote noise.
   - Prefer single quotes inside returned messages that quote user values.

## Navigation And Mutation Returns

For in-place DOM changes where the execution context survives:

1. Trigger the page's real control or route update.
2. Await the DOM or route reflecting the new state.
3. Return a structured outcome, for example:

```js
return { status: "Sorted issues by created date." };
```

For full-document navigation or a cross-kind SPA route that aborts the current
tool signal:

1. Validate inputs synchronously.
2. Prepare a structured outcome.
3. Defer the navigation by one macrotask.
4. Return the outcome before the page teardown.

```js
setTimeout(() => {
  window.location.assign(targetUrl);
}, 0);
return { status: "Opened issue 12.", id: issueId };
```

Do not:

- Await `pagehide`, `load`, or a future DOM after teardown.
- Use a non-zero timer to keep a return alive.
- Throw validation errors that the runtime may collapse into opaque failures.

## Declarative Tool Rules

Declarative form tools require real visible forms.

- Use spec-defined attributes only: `toolname`, `tooldescription`,
  `toolparamdescription`, and `toolautosubmit`.
- Field parameter names come from each field's `name` attribute.
- Missing `toolautosubmit` on a real declarative form is a bug unless a
  documented contract exception exists.
- Verify declarative attributes on the served form element, not helper comments
  or count-based grep alone.
- Large select enumerations alone are not a reason to abandon a real visible
  form. Keep those workflows declarative unless the widget behavior cannot be
  expressed safely with declarative annotations.
- Hidden fake forms appended only for agents are not acceptable.
- If the UI is a sort control, dropdown, path segment, or JS widget with no real
  form, use an imperative tool.

## Tool Description Examples

Good:

- `Filters the products grid`.
- `Posts a reply under a comment`.
- `Sets checkout shipping address`.
- `Opens the selected search result`.

Poor:

- `Use this to filter by id, price, qty, name, sku, type, visibility, or status`.
- `Click this before calling checkout`.
- `Navigating to the selected post`.
- `Returns content and structuredContent`.

## Contract Checklist

Before shipping, confirm:

- Tool scope is specific and gated.
- Description distinguishes this tool from neighbors.
- Inputs come from page state or prior tool outputs, not guessed indexes.
- Output is one structured value.
- Navigation teardown is handled safely.
- Return status is past tense and short.
- Errors are structured.
- Docs or inventory record any intentional departure.
