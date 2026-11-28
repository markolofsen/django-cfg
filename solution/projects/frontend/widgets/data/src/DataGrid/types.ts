'use client';

import type { ReactNode } from 'react';

export type DataGridRowId = string | number;

export type SortDirection = 'asc' | 'desc' | null;

export interface DataGridColumn<T = unknown> {
  key: string;
  header: ReactNode;
  width?: string | number;
  minWidth?: string | number;
  maxWidth?: string | number;
  sortable?: boolean;
  filterable?: boolean;
  align?: 'left' | 'center' | 'right';
  /** Custom cell renderer. Receives the row data. */
  cell?: (row: T) => ReactNode;
  /** Custom filter predicate for this column. */
  filterFn?: (row: T, filterValue: string) => boolean;
}

export interface DataGridSortState {
  key: string | null;
  direction: SortDirection;
}

export interface DataGridFilterState {
  [columnKey: string]: string;
}

export interface DataGridPaginationState {
  page: number;
  pageSize: number;
}

export type DataGridSelectionMode = 'none' | 'single' | 'multiple';

export interface DataGridProps<T = unknown> {
  /** Row data */
  data: T[];
  /** Column definitions */
  columns: DataGridColumn<T>[];
  /** Unique row id getter */
  getRowId: (row: T) => DataGridRowId;

  /** Selection behaviour. Default: 'none' */
  selectionMode?: DataGridSelectionMode;
  /** Initially selected row ids */
  initialSelectedIds?: DataGridRowId[];
  /** Triggered when selection changes */
  onSelectionChange?: (selectedIds: DataGridRowId[]) => void;

  /** Controlled sort state */
  sort?: DataGridSortState;
  /** Called when sort changes */
  onSortChange?: (sort: DataGridSortState) => void;
  /** Default sort */
  initialSort?: DataGridSortState;

  /** Controlled filter state */
  filters?: DataGridFilterState;
  /** Called when filters change */
  onFilterChange?: (filters: DataGridFilterState) => void;
  /** Default filters */
  initialFilters?: DataGridFilterState;

  /** Controlled pagination */
  pagination?: DataGridPaginationState;
  /** Called when pagination changes */
  onPaginationChange?: (pagination: DataGridPaginationState) => void;
  /** Default pagination */
  initialPagination?: DataGridPaginationState;
  /** Available page sizes. Default: [10, 25, 50, 100] */
  pageSizeOptions?: number[];

  /** Enable column resizing. Default: false */
  resizable?: boolean;
  /** Sticky header. Default: true */
  stickyHeader?: boolean;
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
