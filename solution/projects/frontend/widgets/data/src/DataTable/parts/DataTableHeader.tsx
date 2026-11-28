'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react';
import {
  TableHeader,
  TableRow,
  TableHead,
} from '@djangocfg/ui-core/components';

import { useDataTableContext } from '../context/DataTableContext';

export function DataTableHeader() {
  const { columns, selectionMode, selectAllVisible, isSelected, rows, getRowId } =
    useDataTableContext();

  const allVisibleSelected = rows.length > 0 && rows.every((r) => isSelected(getRowId(r)));

  return (
    <TableHeader>
      <TableRow>
        {selectionMode === 'multiple' && (
          <TableHead className="w-10">
            <input
              type="checkbox"
              checked={allVisibleSelected}
              onChange={selectAllVisible}
              className="h-4 w-4 rounded border-border accent-primary"
              aria-label="Select all visible rows"
            />
          </TableHead>
        )}
        {selectionMode === 'single' && <TableHead className="w-10" />}
        {columns.map((col) => (
          <DataTableHeaderCell key={col.key} column={col} />
        ))}
      </TableRow>
      <DataTableFilterRow />
    </TableHeader>
  );
}
DataTableHeader.displayName = 'DataTableHeader';

function DataTableHeaderCell({ column }: { column: { key: string; header: React.ReactNode; sortable?: boolean; align?: 'left' | 'center' | 'right' } }) {
  const { sort, setSort } = useDataTableContext();
  const isSorted = sort.key === column.key;

  return (
    <TableHead
      className={cn(
        column.align === 'center' && 'text-center',
        column.align === 'right' && 'text-right',
        column.sortable && 'cursor-pointer select-none'
      )}
      onClick={() => column.sortable && setSort(column.key)}
      data-sort={isSorted ? sort.direction : undefined}
    >
      <span className="inline-flex items-center gap-1">
        {column.header}
        {column.sortable && (
          <span className="inline-flex text-muted-foreground/60">
            {isSorted && sort.direction === 'asc' && <ArrowUp className="h-3.5 w-3.5" />}
            {isSorted && sort.direction === 'desc' && <ArrowDown className="h-3.5 w-3.5" />}
            {!isSorted && <ArrowUpDown className="h-3.5 w-3.5" />}
          </span>
        )}
      </span>
    </TableHead>
  );
}

function DataTableFilterRow() {
  const { columns, filters, setFilter, selectionMode } = useDataTableContext();
  const hasFilterable = columns.some((c) => c.filterable);

  if (!hasFilterable) return null;

  return (
    <TableRow>
      {selectionMode !== 'none' && <TableHead />}
      {columns.map((col) => (
        <TableHead key={col.key}>
          {col.filterable ? (
            <input
              type="text"
              value={filters[col.key] ?? ''}
              onChange={(e) => setFilter(col.key, e.target.value)}
              placeholder="Filter…"
              className={cn(
                'w-full rounded-sm border border-input bg-background px-2 py-1 text-xs',
                'placeholder:text-muted-foreground',
                'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'
              )}
            />
          ) : (
            <span />
          )}
        </TableHead>
      ))}
    </TableRow>
  );
}
