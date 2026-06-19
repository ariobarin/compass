---
name: proper-flowcharts
description: Create readable standard flowcharts for workflows, systems, and Mermaid diagrams. Use when creating, reviewing, or cleaning up flowcharts or process maps.
---

# Proper Flowcharts

## Overview

Create flowcharts that teach the reader how a process works, changes, or transfers decisions and handoffs. Optimize for semantic clarity, readability, and useful decomposition before visual decoration.

## Workflow

1. Define the reader and job.
   - Decide whether the chart is for orientation, review, implementation, debugging, change comparison, or documentation.
   - Pick the level of detail that reader needs. Put rare edge cases in focused supporting diagrams.
   - Treat screenshots, sketches, and examples as intent signals, not templates to copy.

2. Inventory the process before drawing.
   - Identify starts, ends, actors, responsibilities, inputs, outputs, decisions, subprocesses, data stores, documents, waits, failures, loops, parallel work, and handoffs.
   - Ground the chart in the best available source: code, docs, traces, UI/API behavior, requirements, design notes, or the user's intended behavior.
   - Mark what is confirmed, inferred, intended, or changed when that distinction matters to the reader.
   - When the user flags one visible issue, scan for the same pattern across the whole artifact before fixing only that example.

3. Choose a shape language.
   - Use standard flowchart symbols where they fit: terminal, process, decision, input/output, predefined process, connector, data store, document, manual action, preparation, and fork/join.
   - Map shapes to the domain intentionally. A shape can represent any domain concept that matches its flowchart meaning. Keep project-specific meanings in labels or legends.
   - Keep one meaning per shape within a diagram or diagram set. Add a compact legend only when the mapping is not obvious.
   - Make nodes atomic: one operation, one call boundary, one artifact, or one decision. Read [notation-and-quality.md](references/notation-and-quality.md) when you need symbol details, mode rules, Mermaid notes, or final QA.

4. Compose for understanding.
   - Prefer a clear top-to-bottom or left-to-right main path.
   - Label decision exits with the condition, such as `yes`, `no`, `valid`, `retry`, or the business-specific branch name.
   - Use active verb labels for actions and noun labels for artifacts or states.
   - Keep labels short enough to read inside shapes. Move explanation into adjacent notes or prose.
   - Use connectors, lanes, or separate diagrams to keep edges readable.
   - Put branch logic in decision nodes with separate labeled outgoing edges.

5. Decompose complex systems.
   - Start with one readable overview.
   - Add focused supporting diagrams for ranking, retries, exception handling, state transitions, data movement, handoffs, or any subroutine that would make the overview unreadable.
   - Prefer a diagram selector, tabs, or separate sections over showing many tiny diagrams at once. Default to the diagram most useful for the selected task or comparison.

6. Make the artifact functional.
   - Make the flow understandable: trigger, baseline or starting state, changed behavior if any, decision points, risks, responsibilities, and final outcomes.
   - Cite or reference evidence when the chart represents a real system. State assumptions when the chart includes intended or inferred behavior.
   - If a mode, variant, or toggle changes the chart, render the selected state. Disable or normalize controls outside the selected state.
   - Preserve reader context in interactive artifacts. Mode changes should keep the selected diagram and scroll position when possible.

7. Verify the rendered result.
   - Render the diagram in the target medium, such as Markdown, HTML, slides, or an image.
   - Check that text is readable at the expected viewport or page size.
   - Fix tiny full-width mega-flows by splitting them or changing orientation.
   - Use page-level flow by default. Add an internal scroll pane only when the user explicitly needs a large navigable canvas.
   - Confirm there are no clipped nodes, unreadable labels, broken Mermaid parse errors, page-level overflow, stale state, unrelated variant content, missing steps, or impossible paths.
