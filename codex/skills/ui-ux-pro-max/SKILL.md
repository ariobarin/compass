---
name: ui-ux-pro-max
description: Guide UI/UX design for web and mobile layout, components, visual systems, palettes, typography, UX review, accessibility, charts, and stack rules.
---

# UI/UX Pro Max

Use this skill for concrete web or mobile UI/UX decisions: structure, visual
systems, interaction behavior, accessibility, charts, responsive layout, and
implementation guidance for the detected stack.

## Start Here

1. Identify the product type, target audience, style keywords, and stack.
2. Generate a design system before detailed searches when creating or reshaping
   a UI.
3. Use focused domain or stack searches for local questions.
4. Apply the quick reference and professional checklist before delivery.

Read [search-workflow.md](references/search-workflow.md) for CLI usage,
domains, stacks, persistence, examples, output formats, and troubleshooting.
Read [quick-reference.md](references/quick-reference.md) for priority rules
across accessibility, interaction, performance, style, layout, typography,
animation, forms, navigation, and charts.
Read [professional-ui-rules.md](references/professional-ui-rules.md) for final
app UI quality checks.

## Entry Points

| Task | Start from |
| --- | --- |
| Page or product surface | Design system search, then stack guidance |
| Component or local surface | Domain search for `style`, `ux`, or stack |
| Color palette or font pairing | Design system search, then `color` or `typography` |
| Existing UI review | `quick-reference.md` checklist |
| UI bug or polish pass | Relevant quick-reference section |
| Charts or dashboards | `chart` domain and stack guidance |

## Priority Model

Use this order when judging tradeoffs:

1. Accessibility
2. Touch and interaction
3. Performance
4. Style selection
5. Layout and responsive behavior
6. Typography and color
7. Animation
8. Forms and feedback
9. Navigation
10. Charts and data

## Working Rules

- Match style, density, and interaction patterns to the product type and user
  context.
- Use explicit palette and typography decisions rather than generic visual
  polish.
- Preserve accessibility, touch targets, keyboard paths, and reduced-motion
  support as baseline requirements.
- Detect the implementation stack from repo files when possible, then use the
  matching stack guidance.
- Verify at small mobile width, landscape, dark mode when present, and the
  most important interaction states before delivery.
