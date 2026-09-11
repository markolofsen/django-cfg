---
title: "@djangocfg widgets"
status: current
version: "2.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# `@djangocfg/widget-*`

Sixteen packages of heavy, self-contained features. Each is separate so an app
pays only for what it imports.

**Four are dependencies here. The other twelve are one `pnpm add` away** — and
that is why all sixteen are listed. The purpose of this page is that nobody
builds a kanban, a data grid, a file upload, a product tour or a lightbox by
hand without first knowing one ships.

## Installed here

| Package | Subpath used | For |
|---|---|---|
| `widget-map` | `.` (lazy) | `LazyMapContainer`, `MapMarker` — property location and search map |
| `widget-visual` | `./gallery` | the listing gallery |
| `widget-code` | `./markdown-message` | `MarkdownMessage` — the property brief |
| `widget-ogimage` | `.` | `createOgCards`, `ogFooter`, `ogImageUrl` |

`widget-data`, `widget-diagram`, `widget-editor` and `widget-kit` are in
`transpilePackages` but **not imported directly** — `widget-code` pulls them
transitively and Turbopack needs each one named.

## The full catalogue

Check here before building a surface by hand. Generated from the upstream
manifests — a release that adds a widget or a subpath shows up here, and
`pnpm check:boundaries` fails until it does.

<!-- GENERATED:start -->
_16 publishable widgets. Generated from their `package.json` manifests — do not hand-edit._

| Package | What it is | Subpaths |
|---|---|---|
| `widget-agent` | Agent tooling: page snapshot and browser bridge, plus viewers for an OpenAPI schema, a request, a log and an environment | `./browser-bridge` `./page-snapshot` `./page-copilot` `./openapi` `./request-viewer` `./api-ref-table` `./log-viewer` `./log-viewer/full` `./env-table` |
| `widget-avatar` | Seeded avatars: one seed picks one style and draws one face, forever, with nothing persisted | `./server` |
| `widget-charts` | Small data visualisations: activity and commit graphs, sparkline, smooth line, gauge, FPS, rating and status indicators | `./activity-graph` `./commit-graph` `./gauge` `./smooth-line` `./sparkline` `./fps` `./rating` `./status-indicator` |
| `widget-chat` | A transport-agnostic chat surface: a pure core, a store, primitives, a composer, and the assembled components a host mounts | `./styles` `./core` `./store` `./primitives` `./widgets` `./content` `./composer` `./ui` `./utils` `./i18n` `./testing` |
| `widget-code` | Code surfaces: a Monaco editor, a diff viewer, a Prism listing, a JSON editor and the markdown renderer that embeds them | `./editor` `./json-editor` `./pretty-code` `./diff-viewer` `./diff-viewer/full` `./markdown-message` `./role-tokens` |
| `widget-data` | Data surfaces: file tree, JSON viewer, data grid and table, kanban, listbox, masonry and timeline | `./tree` `./file-icon` `./file-icon/get-file-icon` `./json-tree` `./data-grid` `./data-table` `./kanban` `./listbox` `./masonry` `./timeline` `./styles` |
| `widget-diagram` | Mermaid diagrams: typed builders that write the source, and a full-parser renderer that draws it | `./builders` |
| `widget-editor` | TipTap editors: a markdown field with mentions and chips, and a Notion-style block editor with slash commands, tables and embedded blocks | `./markdown` `./notion` `./blocks` `./link-preview` `./chips` `./tiptap` |
| `widget-forms` | Input surfaces: a JSON-Schema form, an uploader, a cron builder, a combobox, a sortable list, a scroller and speech dictation | `./json-form` `./json-form/full` `./upload` `./file-upload` `./cron-scheduler` `./combobox` `./sortable` `./scroller` `./speech-recognition` `./composer-registry` `./sounds` |
| `widget-kit` | Shared ground for the djangocfg widgets: formatters and lazy-loading placeholders every surface must agree on | `./format` `./lazy` |
| `widget-map` | Interactive maps on MapLibre GL: markers, clustered GeoJSON, layer factories, key-free basemaps, terrain, geocoding and measuring behind one provider | `./eager` |
| `widget-media` | Media viewers for a conversation or a file preview: zoom/pan image lightbox, mermaid diagrams, markdown and code listings | `./image-viewer` `./diagram` `./markdown` `./code` `./i18n` |
| `widget-ogimage` | Open Graph cards for Next.js apps: one satori renderer, vendored Plus Jakarta Sans, and the brand/content card fabrics every opengraph-image route calls | — |
| `widget-overlay` | Surfaces that sit over the page: a responsive dialog, a scroll spy, a selection toolbar and a product tour | `./responsive-dialog` `./scroll-spy` `./selection-toolbar` `./tour` |
| `widget-player` | One media element that plays audio and video, and the surfaces that borrow it: a footer dock, a route stage, and a transcript row | `./element` `./surfaces` `./model` `./domain` `./i18n` |
| `widget-visual` | Presentation pieces: a colour picker and palette, a marquee, a QR code, an image gallery and a Lottie player | `./color-picker` `./color-palette` `./marquee` `./qr-code` `./gallery` `./lottie-player` |
<!-- GENERATED:end -->

Deliberate variants are omitted from the table above only where the manifest
itself is the better reference: several packages also ship a `/full` entry (the
eagerly-bundled build) and `widget-chat` ships `./testing`.

## Traps

- **`@djangocfg/widget-map` is already the lazy entry.** `LazyMapContainer`
  defers the MapLibre chunk (~800 KB gzipped) until it mounts. Import `./eager`
  only when you have a reason to pay that up front.
- **Every widget component is `'use client'`.** Never render one on the Next.js
  server.
- **Subpath, not root.** `widget-visual`, `widget-code`, `widget-data` and
  `widget-forms` export little from `.`; the feature lives at its subpath.
- **`widget-kit/lazy` is deliberately not in the root.** The root is pure
  TypeScript; `./lazy` pulls React and `ui-core` behind it. Importing
  `formatBytes` must not cost a component tree.
- **Adding a widget costs two edits, both silent when forgotten.** It must join
  `transpilePackages` in **both** `apps/*/next.config.ts` — a missing entry is
  `Unknown module type`, naming the file but not the cause. The Tailwind
  `@source "../node_modules/@djangocfg/widget-*/src"` glob already covers it;
  keep it a glob so this stays one edit, not two.

## Before you hand-roll one

A widget existing is not automatically the right answer, and this workspace has
a documented counter-example: `packages/portal/src/ui/cards/shelf.tsx` is a
scroll container with buttons rather than a carousel, argued in its own header —
native momentum, real links in the document, no hydration layout shift.

The rule is **decide, don't default**. Check the catalogue, then either import it
or write down why not, in the file.
