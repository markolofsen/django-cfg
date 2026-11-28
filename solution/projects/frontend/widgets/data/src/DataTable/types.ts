'use client';

import type { ReactNode } from 'react';

export type DataTableRowId = string | number;

export type DataTableSortDirection = 'asc' | 'desc' | null;

export interface DataTableColumn<T = unknown> {
  key: string;
  header: ReactNode;
  sortable?: boolean;
  filterable?: boolean;
  align?: 'left' | 'center' | 'right';
  /** Custom cell renderer. Receives the row data. */
  cell?: (row: T) => ReactNode;
  /** Custom filter predicate for this column. */
  filterFn?: (row: T, filterValue: string) => boolean;
}

export interface DataTableSortState {
  key: string | null;
  direction: DataTableSortDirection;
}

export interface DataTableFilterState {
  [columnKey: string]: string;
}

export interface DataTablePaginationState {
  page: number;
  pageSize: number;
}

export type DataTableSelectionMode = 'none' | 'single' | 'multiple';

export interface DataTableProps<T = unknown> {
  /** Row data */
  data: T[];
  /** Column definitions */
  columns: DataTableColumn<T>[];
  /** Unique row id getter */
  getRowId: (row: T) => DataTableRowId;

  /** Selection behaviour. Default: 'none' */
  selectionMode?: DataTableSelectionMode;
  /** Initially selected row ids */
  initialSelectedIds?: DataTableRowId[];
  /** Triggered when selection changes */
  onSelectionChange?: (selectedIds: DataTableRowId[]) => void;

  /** Controlled sort state */
  sort?: DataTableSortState;
  /** Called when sort changes */
  onSortChange?: (sort: DataTableSortState) => void;
  /** Default sort */
  initialSort?: DataTableSortState;

  /** Controlled filter state */
  filters?: DataTableFilterState;
  /** Called when filters change */
  onFilterChange?: (filters: DataTableFilterState) => void;
  /** Default filters */
  initialFilters?: DataTableFilterState;

  /** Controlled pagination */
  pagination?: DataTablePaginationState;
  /** Called when pagination changes */
  onPaginationChange?: (pagination: DataTablePaginationState) => void;
  /** Default pagination */
  initialPagination?: DataTablePaginationState;
  /** Available page sizes. Default: [10, 25, 50, 100] */
  pageSizeOptions?: number[];

  /** Loading state */
  loading?: boolean;
  /** Empty state message */
  emptyMessage?: ReactNode;
  /** Row className getter */
  getRowClassName?: (row: T, index: number) => string;
  /** Called when a row is clicked */
  onRowClick?: (row: T) => void;
  /** Called when a row is double-clicked */
  onRowDoubleClick?: (row: T) => void;

  className?: string;
  style?: React.CSSProperties;
}
