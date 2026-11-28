# @djangocfg/widget-data

The surfaces that put rows, nodes and cards on screen: a file tree, a JSON
viewer, a data grid and table, a kanban, a listbox, a masonry and a timeline.

## Install

```bash
pnpm add @djangocfg/widget-data @djangocfg/ui-core
```

```tsx
import { FinderTree } from '@djangocfg/widget-data/tree';
import '@djangocfg/widget-data/styles';
```

The styles import is not optional: Tailwind v4 does not scan `node_modules`,
so without it every surface here renders unstyled.

## Subpaths

| Subpath | What | Own docs |
|---|---|---|
| `./tree` | `TreeRoot`, `FinderTree` — generic, slot-driven, async, with Finder CRUD | [`src/Tree/README.md`](src/Tree/README.md) |
| `./file-icon` | `FileIcon`, `getFileIcon`, `createFileIconSlot` | — |
| `./json-tree` | `JsonTree` — collapsible JSON with search and copy | [`src/JsonTree/README.md`](src/JsonTree/README.md) |
| `./data-grid` | `DataGrid` — sorting, filtering, pagination, selection | [`src/DataGrid/README.md`](src/DataGrid/README.md) |
| `./data-table` | `DataTable` — the same, as a semantic `<table>` | [`src/DataTable/README.md`](src/DataTable/README.md) |
| `./kanban` | `Kanban` — columns and cards, drag included | — |
| `./listbox` | `Listbox` — a composable selection primitive | — |
| `./masonry` | `Masonry` — a column layout | [`src/Masonry/README.md`](src/Masonry/README.md) |
| `./timeline` | `Timeline` — an ordered event column | — |

Each subpath also exports its `Lazy*` wrapper (`LazyTree`, `LazyDataGrid`, …)
for a surface that should not be in the entry chunk.

**Prefer a subpath to the root.** The root barrel exists and works, but pulls
all nine trees; an app that wants a tree should ask for the tree.

## Grouping

One package rather than nine, because these share a shape rather than a
library: none of them carries a heavy dependency the others would pay for. The
whole external surface is `@dnd-kit/core` (Tree only), three small Radix and
`cva` utilities, and `lucide-react`.

`FileIcon` lives here rather than with the visual widgets because it is a Tree
slot — `createFileIconSlot` types against `TreeRowSlot`, and separating them
would put a package boundary through one component's two halves.

## Verify

```bash
pnpm --filter @djangocfg/widget-data check-types test
```
