# DataTable

Lighter sibling of `DataGrid`. Same sort / filter / pagination / selection model, but no column resizing, no sticky header, no `width`/`minWidth`/`maxWidth` per column — use when you want a plain semantic `<table>` for read-heavy lists. For resizable / sticky-header grids reach for `DataGrid` instead.

```tsx
import { DataTable } from '@djangocfg/ui-tools/data-table';

<DataTable
  data={invoices}
  columns={[
    { key: 'number', header: '#',      sortable: true },
    { key: 'client', header: 'Client', filterable: true },
    { key: 'total',  header: 'Total',  align: 'right' },
  ]}
  getRowId={(inv) => inv.id}
  onRowClick={openInvoice}
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `data` | `T[]` | — | Row data. |
| `columns` | `DataTableColumn<T>[]` | — | Column defs (`key`, `header`, `cell?`, `sortable?`, `filterable?`, `align?`, `filterFn?`). |
| `getRowId` | `(row: T) => string \| number` | — | Stable row id. |
| `selectionMode` | `'none' \| 'single' \| 'multiple'` | `'none'` | Selection behaviour. |
| `initialSelectedIds` / `onSelectionChange` | `RowId[]` / `(ids) => void` | — | Uncontrolled selection. |
| `sort` / `onSortChange` / `initialSort` | `DataTableSortState` | — | Controlled or uncontrolled sort. |
| `filters` / `onFilterChange` / `initialFilters` | `DataTableFilterState` | — | Per-column text filters. |
| `pagination` / `onPaginationChange` / `initialPagination` | `DataTablePaginationState` | — | Controlled or uncontrolled pagination. |
| `pageSizeOptions` | `number[]` | `[10, 25, 50, 100]` | Page-size choices. |
| `loading` | `boolean` | `false` | Loading state. |
| `emptyMessage` | `ReactNode` | — | Rendered when `data` is empty. |
| `getRowClassName` | `(row, i) => string` | — | Per-row class hook. |
| `onRowClick` / `onRowDoubleClick` | `(row) => void` | — | Row event handlers. |

Composable parts (`DataTableProvider`, `DataTableHeader`, `DataTableRow`, `DataTablePagination`) are exported for custom compositions.

---

Adapted from jalcoui (MIT).
