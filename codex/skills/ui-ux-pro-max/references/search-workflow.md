# UI/UX Search Workflow

Use this reference for `scripts/search.py` usage, available domains and stacks,
design-system persistence, examples, and common troubleshooting.

## Prerequisites

Check Python:

```bash
python3 --version || python --version
```

Install Python only when it is missing and the user approves the install path
for the host OS.

## Design System First

Start broad UI creation or redesign work with:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

This searches product, style, color, landing, and typography guidance, applies
reasoning rules, and returns a complete design system with pattern, style,
colors, typography, effects, and anti-patterns.

Persist a design system when future page work should reuse it:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

The master file is `design-system/<project_slug>/MASTER.md`. Page overrides
live under `design-system/<project_slug>/pages/`. When building a page, read the
project master first and then apply the page override when it exists.

## Focused Searches

Use domain searches after the design system when a specific dimension needs
more evidence:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

Available domains:

| Domain | Use for |
| --- | --- |
| `product` | Product type recommendations |
| `style` | UI styles, colors, effects |
| `typography` | Font pairings and Google Fonts |
| `color` | Color palettes by product type |
| `landing` | Page structure and CTA strategy |
| `chart` | Chart type and library recommendations |
| `ux` | Interaction, accessibility, loading, and layout guidance |
| `google-fonts` | Individual Google Fonts lookup |
| `react` | React and Next.js performance |
| `web` | App interface rules such as touch targets and safe areas |
| `icons` | Icon style and usage guidance |

## Stack Searches

Use stack searches for implementation-specific guidance:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack <detected-stack>
```

Common stack keys include `angular`, `astro`, `flutter`, `html-tailwind`,
`jetpack-compose`, `laravel`, `nextjs`, `nuxt-ui`, `nuxtjs`, `react`,
`react-native`, `shadcn`, `svelte`, `swiftui`, `threejs`, and `vue`.

## Example

For "Make an AI search homepage":

1. Product type: tool.
2. Audience: consumer search users.
3. Keywords: modern, minimal, content-first, dark mode.
4. Stack: detected from the repo.

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "AI search tool modern minimal" --design-system -p "AI Search"
python3 skills/ui-ux-pro-max/scripts/search.py "search loading animation" --domain ux
python3 skills/ui-ux-pro-max/scripts/search.py "list performance navigation" --stack <detected-stack>
```

## Output Options

The default design-system output is terminal-friendly ASCII. Use Markdown for
docs, JSON for script consumers, and `--output-dir` to choose where persisted
design-system files are written:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system -f markdown
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --json
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system --persist --output-dir docs/ui
```

## Troubleshooting

| Problem | Route |
| --- | --- |
| Style or color is unclear | Re-run `--design-system` with sharper product, industry, tone, and density keywords |
| Dark mode contrast is weak | Check `quick-reference.md` typography and color rules |
| Animation feels unnatural | Check motion duration, easing, and reduced-motion guidance |
| Forms feel poor | Check inline validation, error clarity, and focus management |
| Navigation feels confusing | Check hierarchy, back behavior, and destination availability |
| Layout breaks on small screens | Check mobile-first layout and breakpoint rules |
| Performance or jank appears | Check virtualization, main-thread budget, and throttling guidance |

## Pre-Delivery Checks

- Run a UX validation search such as `--domain ux "animation accessibility z-index loading"`.
- Check the critical and high-priority sections of `quick-reference.md`.
- Test at 375px width and landscape orientation.
- Verify reduced-motion behavior and large dynamic text.
- Check dark-mode contrast separately.
- Confirm touch targets are at least 44pt and content respects safe areas.
