'use client';

export {
  DataGridProvider,
  useDataGridContext,
} from './context/DataGridContext';
export type {
  DataGridContextValue,
  DataGridProviderProps,
} from './context/DataGridContext';

export {
  DataGrid,
  DataGridHeader,
  DataGridRow,
  DataGridCell,
  DataGridPagination,
} from './parts';

export type {
  DataGridProps,
  DataGridColumn,
  DataGridSortState,
  DataGridFilterState,
  DataGridPaginationState,
  DataGridSelectionMode,
  DataGridRowId,
  SortDirection,
} from './types';

// The dynamic-import wrapper. Exported here because the subpath resolves to
// this barrel: in the retired ui-tools `lazy.tsx` was reachable from no declared export,
// so `LazyDataGrid` was dead code for every tool but `JsonTree`.
export { LazyDataGrid } from './lazy';
