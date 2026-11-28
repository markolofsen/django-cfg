'use client';

import * as React from 'react';
import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useReducer,
  useRef,
} from 'react';

import type {
  DataGridColumn,
  DataGridFilterState,
  DataGridPaginationState,
  DataGridProps,
  DataGridRowId,
  DataGridSelectionMode,
  DataGridSortState,
  SortDirection,
} from '../types';

// =====================================================================
// Reducer
// =====================================================================

interface State {
  sort: DataGridSortState;
  filters: DataGridFilterState;
  pagination: DataGridPaginationState;
  selected: Set<DataGridRowId>;
}

type Action =
  | { type: 'set-sort'; sort: DataGridSortState }
  | { type: 'set-filter'; key: string; value: string }
  | { type: 'clear-filters' }
  | { type: 'set-page'; page: number }
  | { type: 'set-page-size'; pageSize: number }
  | { type: 'select'; id: DataGridRowId; mode: DataGridSelectionMode }
  | { type: 'select-many'; ids: DataGridRowId[] }
  | { type: 'clear-selection' }
  | { type: 'select-all'; ids: DataGridRowId[] }
  | { type: 'reset-pagination' };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'set-sort':
      return { ...state, sort: action.sort };
    case 'set-filter': {
      const next = { ...state.filters, [action.key]: action.value };
      if (action.value === '') delete next[action.key];
      return { ...state, filters: next, pagination: { ...state.pagination, page: 1 } };
    }
    case 'clear-filters':
      return { ...state, filters: {}, pagination: { ...state.pagination, page: 1 } };
    case 'set-page':
      return { ...state, pagination: { ...state.pagination, page: action.page } };
    case 'set-page-size':
      return {
        ...state,
        pagination: { page: 1, pageSize: action.pageSize },
      };
    case 'select': {
      if (action.mode === 'none') return state;
      if (action.mode === 'single') {
        return { ...state, selected: new Set([action.id]) };
      }
      const next = new Set(state.selected);
      if (next.has(action.id)) next.delete(action.id);
      else next.add(action.id);
      return { ...state, selected: next };
    }
    case 'select-many':
      return { ...state, selected: new Set(action.ids) };
    case 'clear-selection':
      return { ...state, selected: new Set() };
    case 'select-all':
      return { ...state, selected: new Set(action.ids) };
    case 'reset-pagination':
      return { ...state, pagination: { ...state.pagination, page: 1 } };
    default:
      return state;
  }
};

// =====================================================================
// Context value
// =====================================================================

export interface DataGridContextValue<T = unknown> {
  // State
  sort: DataGridSortState;
  filters: DataGridFilterState;
  pagination: DataGridPaginationState;
  selected: ReadonlySet<DataGridRowId>;

  // Processed data
  rows: T[];
  totalRows: number;
  pageCount: number;

  // Actions
  setSort: (key: string) => void;
  setFilter: (key: string, value: string) => void;
  clearFilters: () => void;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  select: (id: DataGridRowId) => void;
  selectMany: (ids: DataGridRowId[]) => void;
  clearSelection: () => void;
  selectAllVisible: () => void;
  isSelected: (id: DataGridRowId) => boolean;

  // Config
  columns: DataGridColumn<T>[];
  getRowId: (row: T) => DataGridRowId;
  selectionMode: DataGridSelectionMode;
  pageSizeOptions: number[];
  loading: boolean;
  emptyMessage: React.ReactNode;
  getRowClassName?: (row: T, index: number) => string;
  onRowClick?: (row: T) => void;
  onRowDoubleClick?: (row: T) => void;
  stickyHeader: boolean;
}

const DataGridContext = createContext<DataGridContextValue<unknown> | null>(null);

export function useDataGridContext<T>(): DataGridContextValue<T> {
  const ctx = React.useContext(DataGridContext);
  if (!ctx) {
    throw new Error('useDataGridContext must be used inside <DataGridProvider>');
  }
  return ctx as DataGridContextValue<T>;
}

// =====================================================================
// Provider
// =====================================================================

export interface DataGridProviderProps<T>
  extends Pick<
    DataGridProps<T>,
    | 'data'
    | 'columns'
    | 'getRowId'
    | 'selectionMode'
    | 'initialSelectedIds'
    | 'onSelectionChange'
    | 'sort'
    | 'onSortChange'
    | 'initialSort'
    | 'filters'
    | 'onFilterChange'
    | 'initialFilters'
    | 'pagination'
    | 'onPaginationChange'
    | 'initialPagination'
    | 'pageSizeOptions'
    | 'loading'
    | 'emptyMessage'
    | 'getRowClassName'
    | 'onRowClick'
    | 'onRowDoubleClick'
    | 'stickyHeader'
  > {
  children: React.ReactNode;
}

const defaultSort: DataGridSortState = { key: null, direction: null };
const defaultPagination: DataGridPaginationState = { page: 1, pageSize: 25 };

export function DataGridProvider<T>(props: DataGridProviderProps<T>) {
  const {
    data,
    columns,
    getRowId,
    selectionMode = 'none',
    initialSelectedIds,
    onSelectionChange,
    sort: controlledSort,
    onSortChange,
    initialSort,
    filters: controlledFilters,
    onFilterChange,
    initialFilters,
    pagination: controlledPagination,
    onPaginationChange,
    initialPagination,
    pageSizeOptions = [10, 25, 50, 100],
    loading = false,
    emptyMessage = 'No data',
    getRowClassName,
    onRowClick,
    onRowDoubleClick,
    stickyHeader = true,
    children,
  } = props;

  const isControlledSort = controlledSort !== undefined;
  const isControlledFilters = controlledFilters !== undefined;
  const isControlledPagination = controlledPagination !== undefined;

  const [state, dispatch] = useReducer(reducer, undefined, () => ({
    sort: initialSort ?? defaultSort,
    filters: initialFilters ?? {},
    pagination: initialPagination ?? defaultPagination,
    selected: new Set(initialSelectedIds ?? []),
  }));

  const effectiveSort = isControlledSort ? controlledSort : state.sort;
  const effectiveFilters = isControlledFilters ? controlledFilters : state.filters;
  const effectivePagination = isControlledPagination
    ? controlledPagination
    : state.pagination;

  // Sorting
  const sortedData = useMemo(() => {
    if (!effectiveSort.key || !effectiveSort.direction) return data;
    const col = columns.find((c) => c.key === effectiveSort.key);
    if (!col || !col.sortable) return data;

    const dir = effectiveSort.direction === 'asc' ? 1 : -1;
    return [...data].sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[effectiveSort.key!];
      const bVal = (b as Record<string, unknown>)[effectiveSort.key!];
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1 * dir;
      if (bVal == null) return -1 * dir;
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return aVal.localeCompare(bVal) * dir;
      }
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return (aVal - bVal) * dir;
      }
      return String(aVal).localeCompare(String(bVal)) * dir;
    });
  }, [data, effectiveSort, columns]);

  // Filtering
  const filteredData = useMemo(() => {
    const entries = Object.entries(effectiveFilters);
    if (entries.length === 0) return sortedData;
    return sortedData.filter((row) => {
      for (const [key, value] of entries) {
        if (!value) continue;
        const col = columns.find((c) => c.key === key);
        if (col?.filterFn) {
          if (!col.filterFn(row, value)) return false;
          continue;
        }
        const cellValue = (row as Record<string, unknown>)[key];
        if (cellValue == null) return false;
        if (!String(cellValue).toLowerCase().includes(value.toLowerCase())) return false;
      }
      return true;
    });
  }, [sortedData, effectiveFilters, columns]);

  // Pagination
  const totalRows = filteredData.length;
  const pageCount = Math.max(1, Math.ceil(totalRows / effectivePagination.pageSize));
  // Clamped at both ends, like `setPage`. A controlled host passing a
  // 0-indexed page makes `start` negative, and `slice(-n, 0)` renders an
  // empty grid while the page count still claims there are rows.
  const safePage = Math.max(1, Math.min(effectivePagination.page, pageCount));

  const paginatedData = useMemo(() => {
    const start = (safePage - 1) * effectivePagination.pageSize;
    return filteredData.slice(start, start + effectivePagination.pageSize);
  }, [filteredData, safePage, effectivePagination.pageSize]);

  // External callbacks via stable refs
  const onSelectionChangeRef = useRef(onSelectionChange);
  const onSortChangeRef = useRef(onSortChange);
  const onFilterChangeRef = useRef(onFilterChange);
  const onPaginationChangeRef = useRef(onPaginationChange);
  onSelectionChangeRef.current = onSelectionChange;
  onSortChangeRef.current = onSortChange;
  onFilterChangeRef.current = onFilterChange;
  onPaginationChangeRef.current = onPaginationChange;

  useEffect(() => {
    onSelectionChangeRef.current?.([...state.selected]);
  }, [state.selected]);

  // Actions
  const setSort = useCallback(
    (key: string) => {
      let nextSort: DataGridSortState;
      if (effectiveSort.key === key) {
        const cycle: SortDirection[] = ['asc', 'desc', null];
        const idx = cycle.indexOf(effectiveSort.direction);
        const nextDirection = cycle[(idx + 1) % cycle.length] ?? 'asc';
        nextSort = { key, direction: nextDirection };
      } else {
        nextSort = { key, direction: 'asc' };
      }
      if (isControlledSort) {
        onSortChangeRef.current?.(nextSort);
      } else {
        dispatch({ type: 'set-sort', sort: nextSort });
      }
    },
    [effectiveSort, isControlledSort],
  );

  const setFilter = useCallback(
    (key: string, value: string) => {
      if (isControlledFilters) {
        const next = { ...effectiveFilters, [key]: value };
        if (value === '') delete next[key];
        onFilterChangeRef.current?.(next);
      } else {
        dispatch({ type: 'set-filter', key, value });
      }
    },
    [isControlledFilters, effectiveFilters],
  );

  const clearFilters = useCallback(() => {
    if (isControlledFilters) {
      onFilterChangeRef.current?.({});
    } else {
      dispatch({ type: 'clear-filters' });
    }
  }, [isControlledFilters]);

  const setPage = useCallback(
    (page: number) => {
      const safe = Math.max(1, Math.min(page, pageCount));
      if (isControlledPagination) {
        onPaginationChangeRef.current?.({ ...effectivePagination, page: safe });
      } else {
        dispatch({ type: 'set-page', page: safe });
      }
    },
    [isControlledPagination, effectivePagination, pageCount],
  );

  const setPageSize = useCallback(
    (pageSize: number) => {
      if (isControlledPagination) {
        onPaginationChangeRef.current?.({ page: 1, pageSize });
      } else {
        dispatch({ type: 'set-page-size', pageSize });
      }
    },
    [isControlledPagination],
  );

  const select = useCallback(
    (id: DataGridRowId) => dispatch({ type: 'select', id, mode: selectionMode }),
    [selectionMode],
  );

  const selectMany = useCallback((ids: DataGridRowId[]) => {
    dispatch({ type: 'select-many', ids });
  }, []);

  const clearSelection = useCallback(() => {
    dispatch({ type: 'clear-selection' });
  }, []);

  const selectAllVisible = useCallback(() => {
    if (selectionMode !== 'multiple') return;
    const ids = paginatedData.map(getRowId);
    dispatch({ type: 'select-all', ids });
  }, [paginatedData, getRowId, selectionMode]);

  const isSelected = useCallback(
    (id: DataGridRowId) => state.selected.has(id),
    [state.selected],
  );

  const value = useMemo<DataGridContextValue<T>>(
    () => ({
      sort: effectiveSort,
      filters: effectiveFilters,
      pagination: { ...effectivePagination, page: safePage },
      selected: state.selected,
      rows: paginatedData,
      totalRows,
      pageCount,
      setSort,
      setFilter,
      clearFilters,
      setPage,
      setPageSize,
      select,
      selectMany,
      clearSelection,
      selectAllVisible,
      isSelected,
      columns,
      getRowId,
      selectionMode,
      pageSizeOptions,
      loading,
      emptyMessage,
      getRowClassName,
      onRowClick,
      onRowDoubleClick,
      stickyHeader,
    }),
    [
      effectiveSort,
      effectiveFilters,
      effectivePagination,
      safePage,
      state.selected,
      paginatedData,
      totalRows,
      pageCount,
      setSort,
      setFilter,
      clearFilters,
      setPage,
      setPageSize,
      select,
      selectMany,
      clearSelection,
      selectAllVisible,
      isSelected,
      columns,
      getRowId,
      selectionMode,
      pageSizeOptions,
      loading,
      emptyMessage,
      getRowClassName,
      onRowClick,
      onRowDoubleClick,
      stickyHeader,
    ],
  );

  return (
    <DataGridContext.Provider value={value as DataGridContextValue<unknown>}>
      {children}
    </DataGridContext.Provider>
  );
}
