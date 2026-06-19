# Flowchart Notation And Quality

Use this reference when creating, revising, or reviewing flowcharts. The shape meanings are based on common ANSI/ISO flowchart conventions summarized by Wikipedia's flowchart article.

## Standard Shape Meanings

| Concept | Use for | Common shape |
| --- | --- | --- |
| Terminal | Start, end, entry, exit, trigger, or completed sub-process | Oval, stadium, or rounded rectangle |
| Process | Action that changes state, data, ownership, or position | Rectangle |
| Decision | Conditional branch, usually a question or test | Diamond |
| Input/output | Receiving data, emitting data, submitting a request, returning a result | Parallelogram |
| Predefined process | Named routine, module, playbook, or process expanded elsewhere | Rectangle with double vertical sides |
| Connector | Continuation that avoids long or crossing edges on the same page | Small labeled circle |
| Off-page connector | Continuation in another diagram or page | Labeled pentagon |
| Data store | Database, file, queue, cache, index, durable state | Cylinder |
| Document | Human-readable document, report, ticket, form, spec, output artifact | Rectangle with wavy base if supported |
| Manual operation | Human-only operation or manual adjustment | Trapezoid |
| Manual input | Human-entered input | Slanted-top quadrilateral if supported |
| Preparation | Setup, initialization, configuration, batching, precondition | Hexagon |
| Fork/join | Parallel branches and their rejoin point | Thick bar or paired parallel lines |
| Swimlane | Responsibility boundary by team, actor, system, or phase | Horizontal or vertical lane |

## Shape Mapping Rules

- Choose shapes from semantics, not aesthetics.
- Keep a shape's meaning stable across the artifact.
- Use color as a secondary cue only. The diagram must still work in grayscale.
- Use a legend only for non-obvious mappings. Keep it compact and put it after or beside the diagram.
- When the renderer lacks a desired standard shape, use the closest supported shape and name the semantic role in the label or legend.
- Use a normal process rectangle for distinctions with little reader value.

## Flowchart Grammar

- Use one node for one thing: one operation, one call boundary, one decision, one stored artifact, or one visible state.
- Put conditional logic in diamonds. If a label says the process chooses one path or another, split it into a decision node with labeled edges.
- Split operational `and` labels into separate nodes when they describe multiple actions. Keep compound nouns only when they name one artifact or concept.
- Use call-boundary nodes for external or model calls. The call node should name the call. Parse or interpret the result in the following decision node.
- Keep append and feedback steps precise. Browser observations, tool results, inspected schemas, metadata records, and summary artifacts are different state updates.
- Show causal visibility. If a result is appended before the next model, service, or human decision, make that feedback edge explicit.
- Show required inspection, lookup, schema retrieval, authorization, or other detail steps between a low-detail index and concrete execution.

Generic call-boundary pattern:

```mermaid
flowchart TD
  context[Prepare context]
  decisionCall[/Call decision-maker/]
  choice{Parsed output}
  tool[Use selected tool]
  browser[Run browser action]
  answer[Return answer]
  append[Append result to state]

  context --> decisionCall --> choice
  choice -- tool request --> tool --> append
  choice -- browser action --> browser --> append
  choice -- final answer --> answer
  append --> context
```

## Mermaid Guidance

Prefer Mermaid for Markdown or source-controlled diagrams when the target renderer supports it.

Basic portable shapes:

```mermaid
flowchart TD
  start([Start])
  input[/Receive input/]
  step[Transform data]
  decision{Valid?}
  routine[[Run named sub-process]]
  store[(Persist result)]
  finish([End])

  start --> input --> step --> decision
  decision -- yes --> routine --> store --> finish
  decision -- no --> finish
```

Practical notes:

- Quote or simplify labels that contain punctuation if the renderer is strict.
- Use node ids outside Mermaid reserved words such as `call`, `class`, `default`, or `end`.
- Use stable node ids that describe role, not label text.
- Prefer `TD` for step-by-step workflows and `LR` for compact pipelines. Switch orientation when readability suffers.
- Newer Mermaid shape syntax is not always supported everywhere. Test in the actual target renderer before relying on extended shapes.

## Readability Rules

- One diagram should answer one main question.
- Show the happy path clearly, then add visually secondary exception paths.
- Put rare failures, retries, cleanup, and internals in supporting diagrams when they make the main flow hard to read.
- Keep labels short. Use surrounding prose for detailed explanation.
- Label all non-obvious edges and all decision exits.
- Group repeated or low-value implementation details into a predefined process.
- Use swimlanes when responsibility matters more than sequence alone.
- Use connectors when the alternative is a spaghetti edge.
- Keep visual styling quiet: restrained colors, consistent line weights, no decorative gradients, no oversized legend.
- Split large flows into focused diagrams or change orientation before labels become unreadable.
- Prefer one selected diagram at a time for dense technical briefings. Use tabs, a selector, or sections instead of stacked miniatures.
- Make the default selected view match the reader's main job. For runtime comparison, open on runtime behavior, not training, setup, or background architecture.
- Keep explanatory page text sparse. Use diagrams, concise labels, compact legends, and optional source notes.

## Modes, Variants, And Controls

When an artifact has toggles, filters, modes, or variants:

- The control should select the rendered visualization. Draw all modes inside one graph only when the graph is explicitly a comparison view.
- Every visible title, chip, legend item, note, and diagram body must match the selected state.
- If a mode does not apply to an item, disable the control, normalize to the effective mode, or explain the non-applicability.
- Preserve comparison context. Toggling should keep the selected diagram, scroll position, and comparable view whenever the selected diagram still exists.
- If a selected diagram is unavailable in a temporary mode, fall back cleanly and restore it when the mode becomes available again.
- A superficial label swap is not a meaningful mode difference. Verify that the flow changes in the correct way or remove the implied distinction.

## Source, Certainty, And Change

Use the same flowcharting method for confirmed, inferred, intended, changed, and hybrid flows. The difference is evidence posture, not diagram type.

Choose one of these patterns:

- Before and after diagrams side by side when the change is structural.
- One diagram with explicit delta markers when the starting state is already known.
- Overview plus focused mechanism diagrams when the flow has multiple independent moving parts.
- A single confirmed flow when the goal is simply to document how something works.

Make sure the chart shows:

- what triggers the process;
- what changes state;
- which actor or system owns each step;
- where decisions are made;
- what added risks, validations, waits, or fallbacks exist;
- what final outcomes are possible.

Quality rules:

- Inspect source code, docs, logs, traces, screenshots, API calls, runtime behavior, requirements, design notes, or intended behavior before drawing.
- Distinguish confirmed behavior from inferred or intended behavior when the reader could otherwise mistake one for the other.
- Use separate templates for unrelated components that need comparison.
- Use separate diagrams when systems or alternatives have genuinely different control flow.
- When comparing variants, verify that variant-specific labels, notes, and branches only appear in the matching variant.
- Treat examples and screenshots as evidence of a pattern to inspect. Fix the pattern across the artifact when it recurs.

## Annotations

Use annotations only when they reduce hidden inference:

- prompt or context visibility;
- appended-state visibility;
- fallback behavior;
- controller or responsibility routing;
- artifact evidence semantics;
- mode-specific capability constraints.

Keep annotations short and visually secondary. Use them for hidden inference that the nodes and edges already support.
Use visual proximity or dotted, non-directional connectors for annotations. Keep normal directed flow arrows for executable steps.

## Rendered QA Checklist

Before delivery, verify the actual rendered artifact:

- The diagram has a clear start, end, and main path.
- Decision branches are labeled and recombine only when that is truly the behavior.
- Text is readable at the expected viewport, page size, or slide size.
- Node text fits its shape and stays readable.
- Shapes are large enough for their semantic differences to be visible.
- The page fits mobile and narrow viewports in the available width.
- The main point stays visible in the main page flow. Internal scroll areas appear only in intentional large-canvas interactions.
- Mermaid or diagram tooling reports no parse or render errors.
- Supporting diagrams add clarity instead of repeating the same overview.
- The chart teaches the workflow faster than prose alone.

For interactive artifacts, also verify:

- every reachable mode, variant, and diagram tab renders;
- toggles update the diagram body, not only a chip or label;
- controls preserve the reader's selected diagram and scroll position where possible;
- non-applicable controls are disabled, normalized, or clearly explained;
- visible mode-specific content matches the selected mode.

For semantic validation, check:

- expected required steps are present;
- paths are possible under the documented rules;
- low-detail discovery paths include required inspection or detail retrieval before concrete execution;
- call outputs flow to decisions, then to separate branch actions;
- append steps record the right kind of state;
- critic or reviewer findings are consolidated by source evidence and independently repeated failures.
