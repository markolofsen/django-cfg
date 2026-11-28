'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import {
  Table,
  TableBody,
  TableRow,
  TableCell,
} from '@djangocfg/ui-core/components';

import type { DataTableProps } from '../types';
import { DataTableProvider } from '../context/DataTableContext';
import { DataTableHeader } from './DataTableHeader';
import { DataTableRow } from './DataTableRow';
import { DataTablePagination } from './DataTablePagination';

export function DataTable<T>(props: DataTableProps<T>) {
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
    className,
    style,
  } = props;

  return (
    <DataTableProvider<T>
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
    >
      <DataTableShell className={className} style={style} />
    </DataTableProvider>
  );
}
DataTable.displayName = 'DataTable';

function DataTableShell({ className, style }: { className?: string; style?: React.CSSProperties }) {
  return (
    <div
      data-slot="data-table"
      // Single card frame owned by the shell, matching ui-core <Card>:
      // `--radius-popover` corner + `--shadow-card` so a data panel reads the
      // same as every other panel in the app (and gains the soft light-theme
      // lift). The inner <Table> renders `frame={false}` so it doesn't draw a
      // second border/radius inside this one (that produced the visible double
      // border + mismatched corners). `overflow-hidden` clips the header band
      // and the pagination strip to the rounded corners; the pagination's own
      // top border is the only divider between body and footer — no `gap`
      // gutter that reads as a second line.
      className={cn(
        'flex flex-col overflow-hidden rounded-[var(--radius-popover)] border border-border bg-card text-card-foreground [box-shadow:var(--shadow-card)]',
        className
      )}
      style={style}
    >
      <Table frame={false}>
        <DataTableHeader />
        <TableBody>
          <DataTableRows />
        </TableBody>
      </Table>
      <DataTablePagination />
    </div>
  );
}

function DataTableRows() {
  const { rows, getRowId, loading, emptyMessage } = useDataTableContext();

  if (loading) {
    return (
      <TableRow>
        <TableCell colSpan={999} className="p-8 text-center text-muted-foreground">
          Loading…
        </TableCell>
      </TableRow>
    );
  }

  if (rows.length === 0) {
    return (
      <TableRow>
        <TableCell colSpan={999} className="p-8 text-center text-muted-foreground">
          {emptyMessage}
        </TableCell>
      </TableRow>
    );
  }

  return (
    <>
      {rows.map((row, index) => (
        <DataTableRow key={String(getRowId(row))} row={row} index={index} />
      ))}
    </>
  );
}

// Ambient import for JSX usage
import { useDataTableContext } from '../context/DataTableContext';
