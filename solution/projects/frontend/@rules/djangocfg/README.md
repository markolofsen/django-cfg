---
title: "@djangocfg packages — index"
status: current
version: "1.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# `djangocfg/` — the upstream component library

Eleven `@djangocfg/*` packages are dependencies of this workspace. They are
**not** written here: they are published from the djangocfg monorepo
(`projects/solution/frontend/` in the `djangocfg` checkout) and consumed from
npm, with `scripts/sync-djangocfg.mjs` copying local builds in for cross-repo
development.

These pages are a **cheatsheet, not a specification**. They answer "does a
component for this already exist, and what is it called" in one lookup, so a
`<div>` does not get written where `Stat`, `Empty` or `Item` was already
available. The authoritative contract for any one component is its source and
its README in the djangocfg repo.

## Read by task

| Work | Page |
|---|---|
| **First contact with any `@djangocfg` package** | [Overview and import rules](overview.md) |
| **Deciding whether to add a package at all** | [Choosing a package](choosing.md) |
| Reaching for a UI component — does one exist, what is it called | [ui-core — component catalogue](ui-core-components.md) |
| Reaching for a hook | [ui-core — hook catalogue](ui-core-hooks.md) |
| Theme tokens, presets, the CSS entry, dark mode | [ui-core — styling and theming](ui-core-styling.md) |
| App shell, providers, sidebar, auth screens | [layouts](layouts.md) |
| Sitemap, OG images, health, PWA, i18n routing | [nextjs](nextjs.md) |
| Maps, galleries, markdown, OG cards, editors | [widgets](widgets.md) |
| Generated Django client, auth, hooks | [api and the rest](api-and-others.md) |

## Three catalogue pages are generated

[`ui-core-components.md`](ui-core-components.md),
[`ui-core-hooks.md`](ui-core-hooks.md) and [`widgets.md`](widgets.md) have their
tables written by `scripts/gen-djangocfg-catalogue.mjs`, read out of the upstream
barrels and package manifests.

```bash
node scripts/gen-djangocfg-catalogue.mjs           # rewrite
```

**Do not hand-edit between the `GENERATED` markers** — the next run discards it.
Prose outside the markers is preserved and is where judgement belongs.

**`pnpm check:boundaries` fails when they drift.** The staleness comparison is
the tenth check in `scripts/check-boundaries.mjs`, so a dependency bump that
renames an export is caught by the gate you already run, not by remembering to
run a second one. It **skips** on a machine with no djangocfg checkout — the
packages come from npm, and a gate that cannot pass for a reason unrelated to
your change is a gate people learn to ignore.

Regenerating needs the checkout (`~/djangocfg-ui`, or the sibling
`djangocfg/projects/solution/frontend/packages`).

This is not defensive habit. The upstream `ui-core/README.md` catalogue names
`Container`, `Grid`, `Marquee`, `Glass` and `Backdrop`, and **none of the five
exist**; its hook table names `useClickOutside`, `useClipboard`, `useTheme`,
`useLink` and `useInterval`, which do not exist either. A hand-written inventory
of ~400 exports drifts silently, and it reads as authoritative while being wrong
— so this one is not hand-written.

## What belongs on these pages

- **The name and the group** of something that exists upstream.
- **Which of several near-identical exports to reach for**, when the names do
  not settle it (`MultiSelect` vs `MultiSelectPro`, `Sheet` vs
  `ResponsiveSheet`, `DatePicker` vs `DateField`).
- **A trap** that cost time in *this* workspace.

**Does not belong:** prop-by-prop documentation, which rots at the first
signature change and is already in the source. Link to the upstream README
instead.

## These pages are not synchronised

Unlike [`../general/`](../general/README.md), nothing copies this directory
between repositories. It describes packages *as this workspace consumes them*.
A sibling frontend on the same packages uses a different subset and has its own.
