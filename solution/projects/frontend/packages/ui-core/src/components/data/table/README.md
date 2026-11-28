# Table

Composable, headless data table built from semantic primitives. The root `Table`
renders a bordered, rounded **`--card`** surface (a contained data panel that reads
correctly in both light and dark), and you assemble the structure from the
sub-components — there is no monolithic `columns`/`data` prop.

All colors come from theme tokens (`--card`, `--border`, `--muted`, `--accent`),
so light/dark is automatic. Don't reach for raw `bg-gray-*` / `border-zinc-*`.

```tsx
import {
  Table, TableHeader, TableBody, TableFooter,
  TableRow, TableHead, TableCell, TableCaption,
} from '@djangocfg/ui-core';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Invoice</TableHead>
      <TableHead className="text-right">Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell className="font-medium">INV001</TableCell>
      <TableCell className="text-right">$250.00</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

## Components

| Component | Element | Notes |
|---|---|---|
| `Table` | `<table>` (wrapped) | Card frame + scroll container. `className` → `<table>`; see `containerClassName` below. |
| `TableHeader` | `<thead>` | Tinted header band. Supports `sticky`. |
| `TableBody` | `<tbody>` | Supports `striped`. |
| `TableFooter` | `<tfoot>` | Tinted band + `font-medium` for totals/summary rows. |
| `TableRow` | `<tr>` | Hover highlight; `data-state="selected"` → accent fill. |
| `TableHead` | `<th>` | Muted, medium-weight column label. |
| `TableCell` | `<td>` | Body cell. |
| `TableCaption` | `<caption>` | Bottom footer strip inside the card frame. |

All forward their ref and spread native attributes. Per-element `className` always wins.

## Custom props

These are the only props beyond native HTML attributes:

| Component | Prop | Type | Default | Description |
|---|---|---|---|---|
| `Table` | `containerClassName` | `string` | — | Class for the **inner scroll `<div>`** (`overflow-auto`), not the `<table>`. Cap its height (e.g. `"max-h-80"`) to get a scrollable body — required for a sticky header to have something to stick within. |
| `TableHeader` | `sticky` | `boolean` | `false` | Pins the header (`sticky top-0 z-10`) and makes the band **fully opaque** (solid `bg-muted` instead of the `/50` tint) so scrolled rows don't bleed through. |
| `TableBody` | `striped` | `boolean` | `false` | Zebra rows via `nth-child(even)` on the body — no need to compute `i % 2` per row. Per-row `className` still overrides. |

## Selected rows

`TableRow` reacts to `data-state="selected"` with an accent fill — drive it from your
own selection state:

```tsx
<TableRow data-state={isSelected ? 'selected' : undefined}>…</TableRow>
```

## Scrollable table with a sticky header

```tsx
<Table containerClassName="max-h-[320px]">
  <TableHeader sticky>…</TableHeader>
  <TableBody>{/* many rows */}</TableBody>
</Table>
```

The height cap goes on the **scroll container** (`containerClassName`), and `sticky`
goes on the header — both are needed together.

Storybook: `apps/storybook/stories/ui-core/data/Table.stories.tsx`
(`Default`, `WithBadges`, `Striped`, `Compact`, `Sortable`, `Selectable`,
`WithFooter`, `StickyHeader`, `Loading`, `Empty`).
