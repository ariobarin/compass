---
name: webmcp-tool-authoring
description: Design and implement WebMCP tool surfaces. Use for workflow discovery, tool shaping, and live validation.
---

# webmcp-tool-authoring

Use this skill to build WebMCP tools from real site workflows. A good tool
surface is small, stable, composable, and aimed at workflows that are tedious,
fragile, hidden, scroll-heavy, or stateful in the normal browser path.

## Required References

Read the local references before authoring:

- [authoring-workflows.md](references/authoring-workflows.md): cold-start
  discovery, generation routes, choosing tool candidates, and validation loops.
- [tool-shape-contract.md](references/tool-shape-contract.md): WebMCP return
  shape, list/action pairs, ids, page scope, annotations, descriptions, and
  navigation teardown handling.

If editing an existing tool, also use `webmcp-verify-tool` before calling the
change done.

## Workflow

1. Discover the site as a user, from docs, API surfaces, network traces, page
   templates, and task lists.
2. Produce an inventory: page kinds, user verbs, state transitions, and candidate
   tools.
3. Prioritize workflows where the browser path is meaningfully hard: hidden
   state, lazy-loaded content, multi-step filters, unstable lists, modals,
   or repeated actions that are easy to mis-execute by sight alone.
4. Cull weak candidates that duplicate obvious one-click navigation, login or
   account operations, one-off visible filters, or summarization the model can
   do from returned data.
5. Pick a shape from the local decision table: declarative form, DOM read,
   list/action pair, modal, sort/filter, or navigation.
   Prefer declarative forms when a real visible form exists, even if a select
   field has a large enum. Large enums alone are not a reason to switch that
   workflow to imperative.
6. Implement with the page lifecycle in mind: page scope, abort signals, stable
   ids, one structured return value, and no hidden alias behavior.
7. Validate by structural checks and live browser behavior.

## Output

Report the discovered workflow, selected tools, intentionally omitted actions,
implementation shape, contract decisions, and live validation status. If a tool
has only static evidence, say that it is not verified. Keep the rationale in
docs or inventory notes, not in long callable tool descriptions.
