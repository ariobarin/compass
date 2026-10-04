---
name: to-tickets
description: Break a plan, spec, or conversation into tracer-bullet tickets with explicit blocking edges. Use when the user requests a ticket breakdown or asks to publish it to a tracker.
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

Use the issue tracker and triage vocabulary already configured by the repository or user. Draft the breakdown in the conversation or requested local artifact without requiring a tracker. If publication is requested and no destination is known, finish the draft, then ask where to publish.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through the layers needed for one end-to-end behavior
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Separate prefactoring into a prerequisite only when it enables delivery and has a verifiable outcome of its own; otherwise keep it in the slice it serves

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A mechanical change whose **blast radius** breaks consumers across the codebase may need **expand-contract**:

- Expand: add the new form beside the old so existing consumers still work.
- Migrate: move consumers in batches sized by blast radius, each blocked by the expansion and keeping CI green while the old form remains.
- Contract: remove the old form in a ticket blocked by every migration batch.

When intermediate batches cannot stay green independently, use an explicit integration branch and a final integrate-and-verify ticket blocked by all batches. Promise green only at that integration point. Keep a small atomic migration in one ticket when that is simpler and verifiable.

### 4. Resolve material decisions

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Check that each blocking edge genuinely gates its ticket. Resolve granularity, scope, or dependency choices with the user when their answer would materially change the plan. Use the decisions and discretion they have already given you.

### 5. Publish the tickets to the configured tracker

Publish when the user has asked for publication or approved it. A request to draft tickets ends with the draft. Complete the breakdown before seeking any approval still needed; an already-authorized publication needs no extra approval round.

- **Local files**: write one file per ticket in the requested or configured issue directory, numbered from `01` in dependency order. Each file's "Blocked by" lists the numbers/titles it depends on.
- **An issue tracker**: publish one issue per ticket, blockers first so dependent tickets can reference real identifiers. Use native blocking relationships when available; otherwise record "Blocked by" references in the body. Record parent relationships separately from blockers and apply the configured triage vocabulary consistently with the ticket's readiness.

Publishing a plan does not by itself authorize implementation. When implementation is already authorized, work the **frontier**: tickets whose blockers are complete. Otherwise, finish with the published ticket references.

Leave the parent issue unchanged unless the user also requested or authorized its update.

## Ticket content

Use the repository or tracker's existing template. Otherwise keep each ticket to:

- **What to build**: the end-to-end behavior or verifiable refactor outcome.
- **Acceptance criteria**: observable completion conditions.
- **Blocked by**: actual gating tickets, or "None (can start immediately)".
- **Parent**: the source issue, when one exists.

Describe stable behavior and decisions rather than prescribing a file-by-file edit list that will go stale. Include a source pointer when it saves rediscovery. If a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), include the decision-rich part and note its origin.

Source provenance lives in [references/sources.md](references/sources.md). Do not load it during normal use.
