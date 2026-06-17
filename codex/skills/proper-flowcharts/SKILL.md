---
name: proper-flowcharts
description: Create readable standard flowcharts for workflows, proposals, decisions, systems, and Mermaid diagrams. Use for flowcharts, process maps, or diagram cleanup.
---

# Proper Flowcharts

## Overview

Create flowcharts that teach the reader how a process works, what a proposal changes, or where decisions and handoffs occur. Optimize for semantic clarity, readability, and useful decomposition before visual decoration.

## Workflow

1. Define the reader and job.
   - Decide whether the chart is for orientation, review, implementation, debugging, proposal comparison, or documentation.
   - Pick the level of detail that reader needs. Do not put every edge case in the overview.

2. Inventory the process before drawing.
   - Identify starts, ends, actors, responsibilities, inputs, outputs, decisions, subprocesses, data stores, documents, waits, failures, loops, parallel work, and handoffs.
   - For existing systems, read the source, docs, traces, or UI/API behavior first. Do not draw from guesses when evidence is available.
   - For proposals, show the current state, proposed state, or delta explicitly instead of mixing them in one ambiguous path.

3. Choose a shape language.
   - Use standard flowchart symbols where they fit: terminal, process, decision, input/output, predefined process, connector, data store, document, manual action, preparation, and fork/join.
   - Map shapes to the domain intentionally. A shape can represent any domain concept that matches its flowchart meaning, but do not bake in project-specific meanings.
   - Keep one meaning per shape within a diagram or diagram set. Add a compact legend only when the mapping is not obvious.
   - Read [notation-and-quality.md](references/notation-and-quality.md) when you need symbol details, Mermaid shape notes, or a final QA checklist.

4. Compose for understanding.
   - Prefer a clear top-to-bottom or left-to-right main path.
   - Label decision exits with the condition, such as `yes`, `no`, `valid`, `retry`, or the business-specific branch name.
   - Use active verb labels for actions and noun labels for artifacts or states.
   - Keep labels short enough to read inside shapes. Move explanation into adjacent notes or prose.
   - Avoid crossing lines. Use connectors, lanes, or separate diagrams instead of tangled edges.

5. Decompose complex systems.
   - Start with one readable overview.
   - Add focused supporting diagrams for ranking, retries, exception handling, state transitions, data movement, handoffs, or any subroutine that would make the overview unreadable.
   - Prefer a diagram selector, tabs, or separate sections over showing many tiny diagrams at once.

6. Make the artifact functional.
   - If the user asks for a proposal, make the change understandable: baseline, proposed behavior, decision points, risks, and where responsibilities shift.
   - If the user asks to visualize an existing workflow, show what actually happens and cite or reference the evidence used.
   - If a mode, variant, or toggle changes the chart, ensure every visible note, title, legend entry, and diagram respects that selected state.

7. Verify the rendered result.
   - Render the diagram in the target medium, such as Markdown, HTML, slides, or an image.
   - Check that text is readable at the expected viewport or page size.
   - Fix tiny full-width mega-flows by splitting them or changing orientation.
   - Avoid internal scroll panes unless the user explicitly needs a large navigable canvas.
   - Confirm there are no clipped nodes, unreadable labels, broken Mermaid parse errors, page-level overflow, stale state, or unrelated variant content.
