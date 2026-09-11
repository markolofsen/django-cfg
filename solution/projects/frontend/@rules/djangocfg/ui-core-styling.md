---
title: "ui-core — styling and theming"
status: current
version: "1.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# `@djangocfg/ui-core` — styling and theming

Everything here fails **silently**: the palette survives, the layout does not,
and nothing is logged. That is why this page exists.

## The stylesheet entry, in order

`apps/web/app/globals.css` and `apps/web-bali/app/globals.css` open with:

```css
@import "@djangocfg/ui-core/styles/full";      /* FIRST — Tailwind + tokens + base + utilities */
@plugin "tailwindcss-animate";
@import "@djangocfg/ui-core/styles/presets/soft";
@import "@djangocfg/layouts/styles";
@import "@djangocfg/devtools/styles";
```

Three things about this order are load-bearing:

- **`styles/full`, never plain `styles`.** The plain entry emits unlayered CSS
  and does not import Tailwind; in v4 an unlayered rule beats `@layer utilities`,
  so the base resets defeat `gap`, `space-y`, `divide`, `flex`, `border` and
  `padding`. Colours are `var()` lookups and survive — the page looks themed and
  lays out wrongly.
- **`tailwindcss-animate` must be declared here.** `ui-core/styles/full` does not
  include the plugin; a consumer that omits it loses every `animate-*` class.
- **The preset comes after `full`.** Presets only redefine tokens.

The layer order is then declared explicitly, before any layer has content — a
layer's precedence is fixed where it is **first named**, so declaring it up front
makes reordering later imports a safe edit. The commentary in `globals.css` is
the authority; read it before touching import order.

## Tailwind must be told to scan package source

Every `@mls/*` package and every `@djangocfg/*` package is consumed as **source**,
not built CSS. Tailwind v4 scans only the app it runs in, and skips
`node_modules` by default. A class used solely inside package source is therefore
absent from the production CSS.

```css
@source "../../../packages/portal/src";
@source "../node_modules/@djangocfg/widget-*/src";
```

**Add a `@source` line when a package starts emitting class strings.** The widget
glob is deliberately a glob, so adding a widget to `package.json` needs no CSS
edit.

**Never build a class by interpolation.** `bg-${tone}-500` is invisible to
Tailwind, which reads complete tokens only. A static map of full class strings is
the shape that survives a production build.

## Next must be told to transpile them too

The same source-not-dist fact has a second consequence, in
`apps/*/next.config.ts`:

```ts
transpilePackages: ["@djangocfg/ui-core", "@djangocfg/widget-code", /* … */]
```

Turbopack cannot compile a package it was not told to transpile — it fails with
**"Unknown module type"**, naming the file but not the missing entry.

Transitive widgets need their own entries: `widget-code` pulls `widget-data`,
`widget-diagram`, `widget-editor` and `widget-kit`, and all four publish source.

## Theme tokens

Tokens are the single source of truth for colour and text size; components read
them, so overriding a token restyles everything coherently and a per-component
literal does not.

- **Font size**: Tailwind's `text-*` utilities are bridged to `--font-size-*` in
  `theme/tokens.css`. To change sizing, override `--font-size-*` in a block
  **after** the preset import. Never add `text-[15px]` literals or inject styles
  at runtime.
- **Colour**: use the semantic tokens (`bg-background`, `text-muted-foreground`,
  `border-border`), not raw palette values.
- **`text-on-destructive`, not `text-white`, on a destructive fill.** White on
  destructive fails WCAG AA; the token is near-black and the contract a11y gate
  upstream enforces it.
- **Presets** (`soft`, `default`, `django-cfg`, `ios`, `macos`, `windows`,
  `dense`, `high-contrast`) are static CSS files. `BaseApp` owns only the
  light/dark class and injects no tokens at runtime.

## Z-index

The popover layer sits at `z-[1400]`, above dialogs at `z-1300`. Keep it there —
below, and every dropdown or select opened **inside a modal** renders behind it.
