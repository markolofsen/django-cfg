---
title: Tokens, Themes, and Styles
status: current
version: "3.0"
audience: design, frontend, agents
last_reviewed: 2026-09-01
---

# Tokens, Themes, and Styles

Semantic CSS tokens are the visual source of truth. Components consume meaning,
not palette coordinates.

## Token layers

Use three levels:

1. **Foundation values**: raw color, spacing, type, radius, and shadow scales.
2. **Semantic tokens**: `background`, `foreground`, `primary`, `warning`,
   `divider`, `sidebar-background`.
3. **Component decisions**: a button or alert maps its variant to semantic
   tokens.

Product code SHOULD consume levels 2 and 3. Raw values belong only in theme
definition, branded assets, or an explicitly documented data visualization.

## Static CSS is authoritative

The design system owns colors, typography, radii, status surfaces, charts, and
sidebar tokens **in CSS**. Do not create a parallel TypeScript palette or inject
a runtime token sheet: a value that exists in two languages has no owner, and
the one that loses is whichever loaded second.

The consumer contract is an ORDER, and every clause below has a failure behind
it:

- The design system's own stylesheet MUST be the **first** style import. Loaded
  after a preset, the preset's overrides are the ones discarded.
- Import **exactly one** product preset after it. Two presets are two answers
  for every token, resolved by import order rather than by a decision.
- Import a secondary library's stylesheet only when that library is used.
- Add small product overrides **after** the preset, never before.
- Do not import the utility framework a second time when the design system's
  stylesheet already owns it. A second copy duplicates every base rule and
  re-resets what the first one had already themed.
- Register animation or plugin layers once, in the consumer.

## Complete color values

Semantic color variables contain complete CSS colors:

```css
:root { --background: hsl(240 17% 97%); }
.dark { --background: hsl(240 5% 8%); }
```

Use `bg-background` or `var(--background)`. Never wrap the token again as
`hsl(var(--background))`.

## Semantic vocabulary

Prefer these roles:

| Role | Examples |
|---|---|
| Canvas and content | `background`, `foreground`, `muted`, `muted-foreground` |
| Interactive | `primary`, `secondary`, `accent`, `ring` |
| Containers | `card`, `popover`, `border`, `divider`, `overlay` |
| Forms | `input`, `ring` |
| Status | `success`, `warning`, `destructive`, `info` and their background/border/foreground pairs |
| Navigation | `sidebar-background`, `sidebar-foreground`, `sidebar-accent`, `sidebar-border` |
| Data visualization | `chart-1` through `chart-5` |

Add a semantic token only when an enduring role is missing. Do not add a token
named after one screen or one component instance — `--settings-page-blue` names
a place and a hue, so it can never be reused and can never be re-themed.

## Light, dark, and system modes

- A preset MUST define coherent light and dark pairs.
- `ThemeProvider` owns the mode preference and the `html.dark` class only.
- Theme values MUST remain static CSS so navigation, hydration, and lazy chunks
  cannot remove them.
- Default to system preference unless product requirements say otherwise.
- Use a route override only for a complete, intentional route treatment.
- Use a forced opposite-theme subtree rarely; it creates contrast and token
  boundary risks.

Every changed surface MUST be reviewed in light and dark modes. High-contrast
and reduced-motion behavior SHOULD be checked when the product supports them.

## Programmatic colors

Canvas, SVG libraries, diagram renderers, and some third-party components need
a resolved color STRING rather than a token reference.

**MUST**: read the computed value through the design system's palette helper —
one that resolves a semantic token against the live theme, plus an alpha helper
for washes — rather than reaching for the raw value or hardcoding a hex beside
the call.

**MUST NOT** pass `var(...)`, `color-mix(...)`, or `oklch(...)` to an API that
requires a parsed color. Those are CSS expressions, not colors: the renderer
receives a string it cannot parse and falls back to black, transparent, or
nothing at all, silently and in only one theme.

The helper is also what keeps the mode switch working. A color read once at
module scope freezes the theme that happened to be active at load.

## Product density and layout tokens

Shared presets establish a coherent baseline. Product-specific density MAY use
a small stable override:

```css
:root, .dark {
  --font-size-base: 0.875rem;
  --layout-reading-max: 64rem;
}
```

- Name layout tokens by role, not route.
- Keep one token per recurring width or shell dimension.
- Feature code SHOULD consume the token instead of repeating pixel literals.
- Breakpoints encode layout transitions, not device brands.

## Tailwind v4 source scanning

Tailwind does not automatically scan arbitrary workspace packages or
`node_modules`. The app MUST declare source roots for every unbuilt package that
emits utility class strings. Missing source scanning can leave tokens present
while layout utilities are silently absent.

Keep source directives centralized in the app style entry. Do not let each
feature add its own scanner configuration.

Tailwind detects complete text tokens, not runtime interpolation. Map component
variants to complete class strings such as `warning: "bg-warning-background"`.
Never construct utilities such as `` `bg-${tone}-500` ``; the production build
cannot generate a class it never sees. Use a deliberate static map or, rarely,
an owned `@source inline()` safelist.

## Overlays and glass

- Overlay backdrops use the semantic `overlay` token.
- Blur requires a translucent surface; an opaque card hides the effect.
- A transformed or filtered ancestor can create a new backdrop root. Portal a
  floating surface when it must blur content outside that context.
- Glass is a material for hierarchy, not decoration. Provide a solid fallback
  and maintain contrast without blur.

## Local styling

Use the least powerful mechanism that solves the problem:

1. Existing component variant.
2. Semantic utility classes.
3. Product layout primitive.
4. CSS module for shell geometry, complex selectors, or isolated animation.
5. New shared token or utility after proving reuse.

Avoid raw hex values, arbitrary z-indexes, one-off shadows, and inline style
objects for stable presentation.

## Styling review

- Is every color semantic and valid in both modes?
- Is there one static token source and one theme-mode owner?
- Are imports and Tailwind source roots deterministic?
- Are layout dimensions roles rather than repeated literals?
- Does programmatic rendering resolve tokens through palette helpers?
- Does materiality communicate hierarchy rather than add noise?
