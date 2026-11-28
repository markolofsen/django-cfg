# DataGrid

Headless data grid with built-in sort / filter / pagination / selection and column resizing. Composable: `<DataGrid>` is the all-in-one entry point, while `DataGridProvider` + `DataGridHeader` / `DataGridRow` / `DataGridCell` / `DataGridPagination` let you swap individual parts. Pure React, no `@tanstack/react-table` dependency.

```tsx
import { DataGrid } from '@djangocfg/ui-tools/data-grid';

<DataGrid
  data={users}
  columns={[
    { key: 'name',  header: 'Name',  sortable: true, filterable: true },
    { key: 'email', header: 'Email', sortable: true },
    { key: 'role',  header: 'Role',  align: 'right' },
  ]}
  getRowId={(u) => u.id}
  selectionMode="multiple"
  onSelectionChange={setSelected}
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `data` | `T[]` | — | Row data. |
| `columns` | `DataGridColumn<T>[]` | — | Column defs (`key`, `header`, `cell?`, `sortable?`, `filterable?`, `width?`, `align?`, `filterFn?`). |
| `getRowId` | `(row: T) => string \| number` | — | Stable row id. |
| `selectionMode` | `'none' \| 'single' \| 'multiple'` | `'none'` | Selection behaviour. |
| `initialSelectedIds` / `onSelectionChange` | `RowId[]` / `(ids) => void` | — | Uncontrolled selection. |
| `sort` / `onSortChange` / `initialSort` | `DataGridSortState` | — | Controlled or uncontrolled sort. |
| `filters` / `onFilterChange` / `initialFilters` | `DataGridFilterState` | — | Per-column text filters. |
| `pagination` / `onPaginationChange` / `initialPagination` | `DataGridPaginationState` | — | Controlled or uncontrolled pagination. |
| `pageSizeOptions` | `number[]` | `[10, 25, 50, 100]` | Page-size choices. |
| `resizable` | `boolean` | `false` | Enable column resizing. |
| `stickyHeader` | `boolean` | `true` | Sticky header row. |
| `loading` | `boolean` | `false` | Loading state. |
| `emptyMessage` | `ReactNode` | — | Rendered when `data` is empty. |
| `getRowClassName` | `(row, i) => string` | — | Per-row class hook. |
| `onRowClick` / `onRowDoubleClick` | `(row) => void` | — | Row event handlers. |

## Notes

- No virtualization — for >10k rows pair with pagination or use a virtualized list above the grid.
- All state slots support both controlled (`sort` + `onSortChange`) and uncontrolled (`initialSort`) usage.

---

Adapted from jalcoui (MIT).
