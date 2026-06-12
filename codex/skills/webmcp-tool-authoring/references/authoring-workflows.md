# WebMCP Authoring Workflows

This reference is portable. It distills the established local authoring docs and
prior site sweeps without depending on their original paths.

## Cold-Start Discovery

Use this when the site has no current tool inventory.

1. Read the site like a user for a short focused pass.
   - Build a page-kind taxonomy: home, list, detail, search results, form,
     modal, settings, admin, profile, checkout, or editor.
   - For each page kind, list what a user actually does there.
2. Look for source documentation.
   - Help center, route docs, API docs, OpenAPI, Swagger, GraphQL, sitemap, and
     `robots.txt`.
   - API schemas are useful for stable ids and validation rules, even when the
     final tool should drive the page UI.
3. Inspect network traffic while doing representative tasks.
   - Use requests to infer verbs, ids, hidden state, validation behavior, and
     persistence checks.
   - Do not assume an API call is the correct tool implementation. It is often
     evidence for what the page's own widget does.
4. Crawl or sample pages by template when the site is large.
   - Group pages by DOM structure.
   - Record forms, lists, modals, stateful filters, and virtualized rows.
5. Pattern-match to known site categories.
   - Forums, ecommerce, CMS admin, source control, wiki, maps, and social feeds
     each have recurring tool families.

Discovery output: page kinds, representative URLs, user verbs, state
transitions, candidate ids, and known auth or mutation requirements.

## Candidate Selection

For each page kind, ask:

1. What is the primary verb: search, list, view, sort, filter, edit, submit,
   vote, add, remove, navigate, or open?
2. Is there a list/action pair: `list_X` returns stable ids, then `act_on_X`
   takes one of those ids?
3. What state transition happens: navigation, in-place mutation, modal open,
   route change, form submission, or persistent write?
4. Does the tool expose hidden state or reduce fragile repeated UI operation?

Cull these candidates:

- Simple visible clicks are usually weak tool candidates unless reliability,
  state access, or task coverage clearly requires a tool.
- Duplicate tools that answer the same workflow.
- Too-specific filters that are just ordinary query parameters.
- Login or account-control operations.
- Summary tools the model can perform from returned structured data.
- Simple visible navigation unless the site state makes it unreliable.
- Tools that combine listing and acting in one call.

Candidate output: page kind, tool name, user workflow, state transition, input
source, output shape, page scope, and intentional omissions.

## Generation Routes

Choose a route based on the evidence available.

| Route | Use When | Tradeoff |
|---|---|---|
| Declarative form pass | The page has real visible forms with stable fields. | Cheap and deterministic, but only covers form flows. |
| API-informed authoring | The site has OpenAPI, GraphQL, or clear backend calls. | Strong schemas, but raw wrappers can bypass user-visible state. |
| Trace recording | You can record a human completing tasks once. | Good behavioral oracle, but selectors may drift. |
| Task-list plus source | You have benchmark tasks, site HTML, and WebMCP rules. | Fast for known sites, but must be verified live. |
| Agent-in-loop | The site will be benchmarked repeatedly and quality matters. | Slow, but can refine tools against scripted scenarios. |

Hybrids usually work best:

- Declarative forms plus manual or LLM-authored imperative tools.
- API schema for ids and validation plus DOM-driven execution for UI state.
- Human trace as oracle plus generated tools checked against the trace.

## Implementation Shapes

| Interaction | Tool Shape |
|---|---|
| Visible form to results page | Declarative form annotations. |
| Current-page list | Imperative DOM read returning structured rows with stable ids. |
| Act on a listed row | Imperative action by stable id, returning a structured outcome. |
| Sort or filter in place | Imperative action that drives the real control and returns a structured outcome. |
| Page sections, tables, sidebars | Imperative read with `detail: outline` by default and `detail: full` when needed. |
| Modal or expansion | Imperative action returning the newly visible structured content. |
| Known sibling navigation | Imperative navigation with synchronous validation and teardown-safe return handling. |

## Validation Loop

Before declaring tools done:

1. Run structural checks where available.
   - Registration scope.
   - Schema shape.
   - Return shape.
   - Tool description clarity.
   - Annotation correctness.
2. Round-trip list/action pairs.
   - List rows.
   - Choose a stable id from the returned data.
   - Act on that id.
   - Re-list or observe the destination state.
3. Read description versus behavior.
   - Hide the implementation.
   - Predict arguments and result shape from the description.
   - Compare with schema and actual execution.
4. Verify in a browser or WebMCP runtime.
   - A reward score is not enough.
   - Tool registration, execution, and persisted state are stronger evidence.

## Common Authoring Failures

- Index drift: action tools accept a rendered row index instead of a stable id.
- Scope drift: tools register on pages where calling them fails.
- Description drift: the description tells the agent what to do instead of what
  the tool does.
- API drift: implementation replicates a backend call and leaves the live UI
  stale.
- Shape drift: return value uses an MCP `content` envelope instead of one
  structured value.
- Navigation drift: tool awaits across page teardown or returns before
  validating inputs.
- Annotation drift: `readOnlyHint` or `untrustedContentHint` is applied by habit
  rather than behavior.
