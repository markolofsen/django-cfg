---
title: "Which package to add, and which not to"
status: current
version: "1.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# Choosing a package

The catalogue pages answer *what exists*. This one answers *whether to add it*,
and — more often the useful question — **whether you already have it**.

## Before adding anything: you probably already have it

The three cheapest mistakes, in the order they happen.

**1. It is already in `ui-core`.** ~400 component exports and 57 hooks. A
kanban, a data grid or a file upload is a widget; almost everything else —
buttons, fields, dialogs, menus, tables, empty states, stats, toasts — is
already here. Check [components](ui-core-components.md) and
[hooks](ui-core-hooks.md) **first**, not after writing the component.

**2. It is a transitive dependency you must not redeclare.** `clsx`,
`tailwind-merge`, `class-variance-authority`, `sonner`, `next-themes`,
`@radix-ui/*`, `recharts`, `date-fns`, `embla-carousel-react` and ~40 more are
`ui-core`'s own dependencies. Importing them directly means **your version and
its version both resolve**, and this workspace has no `pnpm.overrides` to
collapse them — a duplicated React or `@types/react` is the documented failure.

Use the ui-core export instead: `cn()` from `@djangocfg/ui-core` rather than
`clsx` + `tailwind-merge`, `Toaster` rather than `sonner`.

**3. A `@mls/*` package already wraps it.** `@mls/portal` owns the catalogue
transport, shared UI and page regions. A second wrapper around the same widget
splits the ownership of one decision across two files.

## What this workspace declares and never imports

Measured against the source, not the manifest. In **both** `apps/web` and
`apps/web-bali`:

| Declared | Referenced in source |
|---|---|
| `clsx` | never |
| `tailwind-merge` | never |
| `sonner` | never |
| `next-themes` | only in comments *about* ui-core's behaviour |
| `@hookform/resolvers` | never |
| `react-hook-form` | never — one comment mentions it |
| `react-ga4` | never |
| `@djangocfg/analytics` | only its `transpilePackages` entry |
| `@djangocfg/i18n` | only its `transpilePackages` entry |

All nine are reachable anyway: the first six because `ui-core` depends on them,
the last two because the app compiles them. **A dependency nothing imports is
not free** — it pins a version, joins the resolution graph, and reads as a
decision somebody made.

Two entries on that list are *not* dead and should stay:

- **`@djangocfg/devtools`** — no TypeScript import, but
  `@import "@djangocfg/devtools/styles"` in `globals.css` is a real use.
- **`server-only`** — imported bare for its side effect, nine times.

**This is an observation, not a licence to prune.** Removing a dependency that
`ui-core` also declares changes nothing today and breaks the day ui-core drops
it. Decide deliberately, and if you remove one, say so in the commit.

## When adding a widget is right

Add it when the surface is **a feature, not a component**: a kanban board, a
data grid with virtualisation, a Mermaid renderer, a media player, a product
tour, a JSON-Schema form. Those cost weeks to build and a line to install.

Adding one costs two edits, both silent when forgotten — see
[widgets](widgets.md): `transpilePackages` in **both** apps, and the Tailwind
`@source` glob (already a glob; keep it one).

## When writing it yourself is right

When the widget's behaviour is not the behaviour you want. This workspace has a
documented case: `packages/portal/src/ui/cards/shelf.tsx` is a scroll container
with buttons rather than a carousel, and its header argues why — native touch
momentum, real links in the document, no hydration layout shift.

**Decide, don't default.** Either import it, or write down in the file why not.

## Packages to leave alone

| Package | Why not |
|---|---|
| `@djangocfg/eslint-config`, `@djangocfg/typescript-config` | This workspace has `@mls/eslint-config` and `@mls/typescript-config`. Two config sets over one tree give a file two answers |
| `@nextra/seo-engine` | `private: true` — unpublishable, and a Nextra-docs tool. This workspace's SEO is [`../custom/seo-and-publication.md`](../custom/seo-and-publication.md) |
| `@djangocfg/api` *as a replacement for* `@mls/api` | Different backends. Both are generated clients; reaching for the wrong one compiles and calls the wrong host |

## The one rule that decides most cases

**Prefer the package that already owns the decision.** A value that lives in one
place has one answer; the same value in two places has two, and the second one
is discovered at a build that fails somewhere unrelated.
