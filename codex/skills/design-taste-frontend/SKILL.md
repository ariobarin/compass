---
name: design-taste-frontend
description: Design or redesign landing pages, portfolios, marketing sites, and editorial pages with deliberate visual direction; not dashboards, app flows, or mobile UI.
---

# Design Taste Frontend

Act as a design director who can implement. Read the brief before choosing an aesthetic, establish one coherent visual system, and ship a complete responsive page that does not look like a rearranged template.

The terminal result is a working frontend whose hierarchy, typography, layout, imagery, motion, and interaction states all support the same design read. Avoid novelty that cannot be justified by the audience or product.

## Start With A Design Read

Before code, state one line in this form:

> Reading this as: <page kind> for <audience>, with a <visual language> direction, leaning toward <design system or implementation family>.

Infer that line from:

- page kind: SaaS landing, consumer launch, agency site, portfolio, redesign, editorial page;
- audience: buyer, consumer, recruiter, reader, public-service user;
- explicit vibe words and references;
- existing logo, type, color, photography, and product UI;
- accessibility, trust, regulatory, or age-related constraints.

Ask one clarifying question only when two materially different directions remain plausible. Otherwise proceed from the strongest evidence.

## Set The Three Dials

Make these values explicit before implementation:

- `DESIGN_VARIANCE`: 1 means symmetric and conventional; 10 means highly asymmetric and experimental.
- `MOTION_INTENSITY`: 1 means nearly static; 10 means cinematic, scroll-driven, or physics-based.
- `VISUAL_DENSITY`: 1 means gallery-like and spacious; 10 means information-packed.

Use `8 / 6 / 4` as a landing-page baseline, then adjust from the brief:

| Direction | Variance | Motion | Density |
| --- | ---: | ---: | ---: |
| Calm, minimal, editorial, Linear-like | 5-6 | 3-4 | 2-3 |
| Premium consumer or brand-led | 7-8 | 5-7 | 3-4 |
| Creative studio or experimental | 9-10 | 8-10 | 3-4 |
| Trust-first, regulated, public-sector | 3-4 | 2-3 | 4-5 |
| Redesign that preserves the product | Match | Match + 1 | Match |

Use the values as decision constraints, not decoration. A high motion value must produce meaningful motion. A low variance value must still have deliberate hierarchy.

## Choose The Right Foundation

Use one coherent design system or implementation family.

- Use official systems when the brief clearly calls for them: Fluent UI, Material, Carbon, Polaris, Atlaskit, Primer, GOV.UK Frontend, USWDS, Radix Themes, or Bootstrap.
- Use Tailwind or native CSS for aesthetic directions that are not official systems, such as editorial, brutalist, bento, kinetic type, dark tech, or glass effects.
- Treat Apple Liquid Glass on the web as an approximation, not an official CSS package.
- Do not mix component systems in one project.
- Check `package.json` before importing a dependency. Add the install command when it is missing.

## Correct The Common Model Defaults

Do not automatically produce:

- purple or blue glow gradients;
- a centered hero over a dark mesh;
- three equal feature cards;
- glass treatment on every surface;
- Inter with slate neutrals by reflex;
- a small uppercase eyebrow above every heading;
- repeated image-left, text-right zigzags;
- fake product screenshots made from empty rectangles;
- decorative version numbers, city or weather strips, scroll cues, or meaningless dots;
- multiple CTAs that express the same intent with different labels.

Every departure from a plain layout needs a reason tied to hierarchy, storytelling, feedback, or brand.

## Typography

- Choose type from the design read, not from a generic premium formula.
- Default to a strong sans display family unless the brand is genuinely editorial, heritage, manuscript, publication, or explicitly serif-led.
- Do not insert one random serif word into a sans headline for visual interest. Use weight or italic within the same family.
- Avoid Fraunces and Instrument Serif as automatic creative defaults.
- Keep body measure near 60-70 characters and use relaxed line height.
- Keep hero headlines at two desktop lines or fewer.
- Reserve extra line height and bottom space for italic display words with descenders.
- Use `next/font` in Next.js or self-hosted `@font-face` with `font-display: swap`.

## Color And Shape

- Choose one neutral family and one primary accent unless the brand requires more.
- Lock the accent across the full page. Do not introduce a new CTA color late in the page.
- Do not use AI purple by default. Use it only when the brief or brand supports it.
- Do not default every premium-consumer brand to cream, brass, clay, oxblood, and espresso. Select a palette that makes this brand distinguishable.
- Pick one radius system. Document any intentional rule such as pill buttons with 16px cards and 8px inputs, then apply it consistently.
- Use shadows only when elevation communicates hierarchy. Tint shadows to the surrounding surface.

## Layout And Hierarchy

- When `DESIGN_VARIANCE > 4`, prefer asymmetric, split, offset, layered, or scroll-pinned composition over automatic centering.
- Keep the hero inside the initial viewport. Show the main CTA without scrolling.
- When the brief requires the whole page in one viewport, name the tested width
  and height, wait for fonts and media to settle, then require
  `document.documentElement.scrollHeight <= window.innerHeight` and
  `document.documentElement.scrollWidth <= window.innerWidth`.
- Confirm fixed and sticky elements do not obscure required content at that
  viewport. Repeat the measurement for every required viewport size.
- Limit hero copy to an optional eyebrow or brand strip, headline, short subtext, and one primary plus at most one secondary CTA.
- Keep desktop navigation on one line and at or below 80px tall.
- Use at least four layout families across an eight-section landing page.
- Use one layout family only once unless repetition is structurally meaningful.
- Stop alternating split image and text sections after two consecutive uses.
- Use no more than one eyebrow per three sections.
- Build bento grids for the exact content count. Do not leave empty cells.
- Use cards only when containment or elevation carries meaning. Prefer spacing, alignment, dividers, and typography for ordinary grouping.
- Keep logo walls below the hero and use actual logo assets rather than plain-text stand-ins.

## Imagery

- Use real supplied, generated, licensed, or clearly sourced imagery.
- When an image-generation or asset tool is available, use it rather than drawing fake screenshots from generic divs.
- When no asset is available, create an explicit placeholder slot with dimensions and a clear asset requirement. Do not disguise a placeholder as a finished image.
- Do not overlay decorative pills or invented photo credits on images.
- Optimize hero media for LCP and reserve dimensions to prevent layout shift.

## Motion

Every animation must support hierarchy, storytelling, feedback, or a real state transition.

- Use CSS transitions for simple hover and focus behavior.
- Use Motion values or a dedicated animation library for continuous pointer, scroll, or physics-driven values. Do not push those values through React `useState` on every frame.
- Keep animated code in isolated client-leaf components in Next.js.
- Provide strict cleanup for effects, observers, timelines, and listeners.
- Respect `prefers-reduced-motion` whenever `MOTION_INTENSITY > 3`.
- Use at most one marquee per page.
- Never attach a raw window scroll listener when `useScroll`, Intersection Observer, ScrollTrigger, or CSS scroll-driven animation fits.

## Interaction And Accessibility

Implement complete state cycles, not only the successful static state:

- loading states that match final geometry;
- useful empty states;
- inline or contextual error states;
- hover, focus-visible, active, disabled, and keyboard behavior;
- labels above form controls, never placeholder-only labels.

Before shipping:

- verify text and control contrast at WCAG AA;
- keep desktop CTA labels on one line;
- use one label for each CTA intent across nav, hero, and footer;
- verify form labels, placeholders, helper text, errors, and focus rings against their actual background;
- use semantic HTML and meaningful alt text;
- keep visible page copy free of em dashes;
- re-read every visible string for grammar and invented claims.

## Responsive And Implementation Discipline

- Use CSS Grid instead of percentage-heavy flex calculations.
- Use `min-h-[100dvh]`, not `h-screen`, for full-height sections.
- Use a consistent container such as `max-w-7xl mx-auto` or a project token.
- Make mobile collapse explicit for high-variance layouts.
- Prefer server components for static layout and client components only for interaction.
- Use one icon family. Prefer Phosphor, HugeIcons, Radix Icons, or Tabler. Do not hand-roll icon paths.
- Provide loading, empty, and error behavior where the page includes asynchronous data.
- Keep Core Web Vitals plausible: LCP below 2.5s, INP below 200ms, and CLS below 0.1.

## Redesign Mode

For an existing project, audit before changing code:

1. Identify the current visual language, tokens, component system, and repeated layout patterns.
2. Separate brand assets worth preserving from accidental inconsistency.
3. Decide whether the request is preserve, evolve, or overhaul.
4. Name the three highest-impact problems in hierarchy, spacing, type, color, imagery, or interaction.
5. Fix the smallest system-level causes before polishing individual sections.
6. Preserve product behavior, routes, content, and accessibility unless the brief explicitly changes them.

Do not erase a functioning brand just to make the result resemble the latest design trend.

## Final Evidence

Do not call the page complete until every relevant statement is true:

- The design read and dial values are explicit.
- One foundation, theme, palette, and radius logic govern the page.
- The hero, navigation, CTAs, and forms fit and remain readable at desktop and mobile widths.
- Every whole-page one-viewport claim names the tested dimensions and includes
  measured vertical and horizontal overflow evidence.
- Section layouts have visible rhythm without template repetition.
- Real imagery or honest asset placeholders are present.
- Motion is motivated, implemented, cleaned up, and reduced-motion safe.
- Loading, empty, error, focus, active, and disabled states exist where relevant.
- No duplicate CTA intent, fake precision, decorative metadata, generic AI copy, or broken visible strings remain.
- Dependency use matches `package.json`.
- The page is responsive, keyboard-usable, and plausibly performant.

If a check fails, fix it before delivery.

## Boundaries

This skill is for landing pages, portfolios, marketing surfaces, editorial pages, and visual redesigns. For dashboards and tables, use the product's design system plus a data-grid library. For multi-step forms, code editors, realtime collaboration, and native mobile, use domain-specific interaction patterns and apply only the relevant visual principles from this skill.

For the reviewed upstream source and MIT notice, see [references/upstream.md](references/upstream.md). Do not load that reference during normal design work.
