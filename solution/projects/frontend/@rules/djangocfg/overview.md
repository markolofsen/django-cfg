---
title: "@djangocfg packages — overview and import rules"
status: current
version: "1.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# Overview and import rules

Read this once before touching any `@djangocfg` package. The per-package pages
assume it.

## The eleven packages this workspace depends on

| Package | What it is | Page |
|---|---|---|
| `@djangocfg/ui-core` | ~400 component exports + ~57 hooks on Radix/Tailwind v4. **The one you reach for by default.** | [components](ui-core-components.md) · [hooks](ui-core-hooks.md) · [styling](ui-core-styling.md) |
| `@djangocfg/layouts` | App shell for Next.js App Router: `BaseApp` providers, `PublicLayout`, `PrivateLayout`, `AuthLayout` | [layouts](layouts.md) |
| `@djangocfg/nextjs` | Next-only *server* utilities: sitemap, OG image, health, PWA, i18n routing | [nextjs](nextjs.md) |
| `@djangocfg/api` | The generated Django client, auth, SWR hooks | [api and the rest](api-and-others.md) |
| `@djangocfg/i18n` | Locale catalogues and the translation CLI | [api and the rest](api-and-others.md) |
| `@djangocfg/analytics` | GA4 / pageview transport | [api and the rest](api-and-others.md) |
| `@djangocfg/devtools` | Dev-only inspector panel | [api and the rest](api-and-others.md) |
| `@djangocfg/widget-map` | Map rendering | [widgets](widgets.md) |
| `@djangocfg/widget-visual` | Gallery, QR, colour picker, marquee, Lottie | [widgets](widgets.md) |
| `@djangocfg/widget-ogimage` | OG card composition | [widgets](widgets.md) |
| `@djangocfg/widget-code` | Markdown, code editor, diff viewer | [widgets](widgets.md) |

## Published but not installed here

Naming one of these in an import fails at **install**, not at compile. They are
listed because the fix is `pnpm add`, not a week of building it by hand.

| Package | What it is |
|---|---|
| `@djangocfg/payments` | Provider-agnostic checkout. **Stripe-first but never depends on the SDK** — the host injects an adapter, and `createMockPaymentAdapter()` lets the whole checkout UX be built before a backend exists |
| `@djangocfg/widget-*` | Twelve more widgets: kanban, data grid, file upload, product tour, charts, chat, media player, avatars, TipTap editors. **[The full catalogue is on the widgets page](widgets.md)** |
| `@djangocfg/eslint-config`, `@djangocfg/typescript-config` | Shared config. **Not wanted here** — this workspace has its own `@mls/eslint-config` and `@mls/typescript-config`, and mixing the two gives one tree two rule sets |

`@nextra/seo-engine` lives in that monorepo too, but it is **private and
un-publishable**, and it is a Nextra-docs tool — it cannot be installed here and
would not apply if it could. This workspace's SEO is
[`../custom/seo-and-publication.md`](../custom/seo-and-publication.md).

## Import paths

**Import from the package root.** `@djangocfg/ui-core` re-exports `./components`,
`./hooks` and `./lib` wholesale, so the flat path always works and is what this
workspace uses (55 of 57 ui-core imports).

```tsx
import { Button, Card, Stat, useMediaQuery } from "@djangocfg/ui-core";
```

The subpath entries (`/components`, `/hooks`) resolve to the same modules and are
equally correct; **do not mix both in one file** — two entries for one symbol read
as two different symbols.

**A subpath is required only where the root does not re-export it**: the router
adapters, `lib/pretext`, the style entries, and every `@djangocfg/nextjs` and
widget subpath. Those are listed on their own pages.

**Group folders are organisational, not import paths.** `components/forms/` is
where `Button` lives upstream; `@djangocfg/ui-core/components/forms` is not an
entry point. The catalogue pages list the group only so you can find the source.

## The three rules that break silently

Each of these produces no error — which is what makes them worth writing down.

### 1. `styles/full`, never `styles`

```css
@import "@djangocfg/ui-core/styles/full";   /* FIRST style import */
```

The plain `…/styles` entry emits its CSS **unlayered** and does not import
Tailwind. In Tailwind v4 an unlayered rule beats anything in `@layer utilities`,
so the base resets defeat layout utilities — `gap`, `space-y`, `divide`, `flex`,
`border`, `padding`. Colours survive, because they are `var()` lookups. The
result is a page that looks themed and lays out wrongly, with no console error.

### 2. One `<UiProviders>` / `<BaseApp>`, at the root only

Tooltip, Dialog and Toast providers are mounted once by the host. A component
that mounts its own nested `TooltipProvider` produces the canonical
`Tooltip must be used within TooltipProvider` — two `createContext()` instances,
and the consumer reads the wrong one.

Never add a provider inside a component. If one is missing, it belongs at the
root.

### 3. Tailwind must scan the package source

Both this workspace's packages and the `@djangocfg` ones are consumed as
**source, not `dist`** — `exports` point at `./src/*`. A class used only inside
package source is absent from the generated CSS unless the app's Tailwind source
globs reach that directory.

The failure is a component that renders **unstyled, with no error anywhere**.

## Local development against unpublished changes

`package.json` keeps the published range. To work against a local djangocfg
checkout:

```bash
node scripts/sync-djangocfg.mjs              # the default set
node scripts/sync-djangocfg.mjs ui-core      # one package
node scripts/sync-djangocfg.mjs restore      # back to published
```

It **builds and copies** into `node_modules` rather than symlinking, deliberately.
A link points into the djangocfg repo, which has its own `node_modules`, so
resolvers here resolve that package's dependencies against the wrong tree —
observed as ~40 spurious "Two different types with this name exist" errors from a
doubled `@types/react`.

**Peers must be synced together.** Syncing `ui-tools` without `ui-core` drags in a
second React type root. Restart the dev server afterwards; Next caches
pre-bundled deps.
