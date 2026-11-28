# @djangocfg/widget-editor

Two TipTap editors and the pieces both are built from.

| Subpath | What | Own docs |
|---|---|---|
| `./markdown` | `MarkdownEditor` — a markdown field with mentions, URL and file-path chips | [`src/markdown/README.md`](src/markdown/README.md) |
| `./notion` | `NotionEditor` — a block editor: slash menu, tables, tasks, code, bookmarks, maps | [`src/notion/README.md`](src/notion/README.md), [`@docs/`](src/notion/@docs/) |
| `./blocks` | The zod schemas for the embeddable block payloads | — |
| `./link-preview` | `LinkPreviewCard` and the `ResolveLinkPreview` seam | — |
| `./chips` | `UrlChip`, `FilePathChip` — the same pills outside an editor | [`src/chips/README.md`](src/chips/README.md) |
| `./tiptap` | `useNodeAttrs` and the node-view helpers | — |

## Install

```bash
pnpm add @djangocfg/widget-editor @djangocfg/ui-core zod
```

`zod` is a peer: the block schemas validate payloads a host also validates, and
two copies would reject each other's instances.

## There is no root barrel worth importing

The root exports a type and nothing else, on purpose. TipTap is sixteen
packages, and the two editors share no consumer — an app wanting the markdown
field must not resolve the Notion editor's tables, drag handle and syntax
highlighter behind it. **Import a subpath.**

## The map block is a real dependency

`NotionEditor`'s `mapBlock` renders `@djangocfg/widget-map`, so the editor
depends on the map widget rather than the other way round. It arrives through
the map's lazy entry, so MapLibre still loads only when a map block mounts.

## Verify

```bash
pnpm --filter @djangocfg/widget-editor check-types test
```
