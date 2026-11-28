'use client';

export {
  DataTableProvider,
  useDataTableContext,
} from './context/DataTableContext';
export type {
  DataTableContextValue,
  DataTableProviderProps,
} from './context/DataTableContext';

export {
  DataTable,
  DataTableHeader,
  DataTableRow,
  DataTablePagination,
} from './parts';

export type {
  DataTableProps,
  DataTableColumn,
  DataTableSortState,
  DataTableFilterState,
  DataTablePaginationState,
  DataTableSelectionMode,
  DataTableRowId,
  DataTableSortDirection,
} from './types';

// The dynamic-import wrapper. Exported here because the subpath resolves to
// this barrel: in the retired ui-tools `lazy.tsx` was reachable from no declared export,
// so `LazyDataTable` was dead code for every tool but `JsonTree`.
export { LazyDataTable } from './lazy';
