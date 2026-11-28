'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { ScrollArea } from '@djangocfg/ui-core/components';

import type { DataGridProps } from '../types';
import { DataGridProvider } from '../context/DataGridContext';
import { DataGridHeader } from './DataGridHeader';
import { DataGridRow } from './DataGridRow';
import { DataGridPagination } from './DataGridPagination';

export function DataGrid<T>(props: DataGridProps<T>) {
  const {
    data,
    columns,
    getRowId,
    selectionMode,
    initialSelectedIds,
    onSelectionChange,
    sort,
    onSortChange,
    initialSort,
    filters,
    onFilterChange,
    initialFilters,
    pagination,
    onPaginationChange,
    initialPagination,
    pageSizeOptions,
    loading,
    emptyMessage,
    getRowClassName,
    onRowClick,
    onRowDoubleClick,
    stickyHeader = true,
    className,
    style,
  } = props;

  return (
    <DataGridProvider<T>
      data={data}
      columns={columns}
      getRowId={getRowId}
      selectionMode={selectionMode}
      initialSelectedIds={initialSelectedIds}
      onSelectionChange={onSelectionChange}
      sort={sort}
      onSortChange={onSortChange}
      initialSort={initialSort}
      filters={filters}
      onFilterChange={onFilterChange}
      initialFilters={initialFilters}
      pagination={pagination}
      onPaginationChange={onPaginationChange}
      initialPagination={initialPagination}
      pageSizeOptions={pageSizeOptions}
      loading={loading}
      emptyMessage={emptyMessage}
      getRowClassName={getRowClassName}
      onRowClick={onRowClick}
      onRowDoubleClick={onRowDoubleClick}
      stickyHeader={stickyHeader}
    >
      <DataGridShell className={className} style={style} />
    </DataGridProvider>
  );
}
DataGrid.displayName = 'DataGrid';

function DataGridShell({ className, style }: { className?: string; style?: React.CSSProperties }) {
  return (
    <div
      data-slot="data-grid"
      className={cn('flex flex-col gap-2 rounded-sm border border-border bg-background', className)}
      style={style}
    >
      <ScrollArea className="w-full" viewportClassName="max-h-[60vh]">
        <table className="w-full caption-bottom text-sm">
          <DataGridHeader />
          <tbody className="[&_tr:last-child]:border-0">
            <DataGridRows />
          </tbody>
        </table>
      </ScrollArea>
      <DataGridPagination />
    </div>
  );
}

function DataGridRows() {
  const { rows, getRowId, loading, emptyMessage } = useDataGridContext();

  if (loading) {
    return (
      <tr>
        <td colSpan={999} className="p-8 text-center text-muted-foreground">
          Loading…
        </td>
      </tr>
    );
  }

  if (rows.length === 0) {
    return (
      <tr>
        <td colSpan={999} className="p-8 text-center text-muted-foreground">
          {emptyMessage}
        </td>
      </tr>
    );
  }

  return (
    <>
      {rows.map((row, index) => (
        <DataGridRow key={String(getRowId(row))} row={row} index={index} />
      ))}
    </>
  );
}

// Ambient import for JSX usage
import { useDataGridContext } from '../context/DataGridContext';
