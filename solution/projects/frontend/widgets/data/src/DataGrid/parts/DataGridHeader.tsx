'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react';

import { useDataGridContext } from '../context/DataGridContext';

export function DataGridHeader() {
  const { columns, selectionMode, selectAllVisible, isSelected, rows, getRowId, stickyHeader } =
    useDataGridContext();

  const allVisibleSelected = rows.length > 0 && rows.every((r) => isSelected(getRowId(r)));

  return (
    <thead
      className={cn(
        '[&_tr]:border-b',
        stickyHeader && 'sticky top-0 z-10 bg-background'
      )}
    >
      <tr className="border-b transition-colors hover:bg-muted/50">
        {selectionMode === 'multiple' && (
          <th className="h-10 px-2 text-left align-middle font-medium text-muted-foreground w-10">
            <input
              type="checkbox"
              checked={allVisibleSelected}
              onChange={selectAllVisible}
              className="h-4 w-4 rounded border-border accent-primary"
              aria-label="Select all visible rows"
            />
          </th>
        )}
        {selectionMode === 'single' && <th className="w-10" />}
        {columns.map((col) => (
          <DataGridHeaderCell key={col.key} column={col} />
        ))}
      </tr>
      <DataGridFilterRow />
    </thead>
  );
}
DataGridHeader.displayName = 'DataGridHeader';

function DataGridHeaderCell({ column }: { column: { key: string; header: React.ReactNode; sortable?: boolean; align?: 'left' | 'center' | 'right'; width?: string | number; minWidth?: string | number; maxWidth?: string | number } }) {
  const { sort, setSort } = useDataGridContext();
  const isSorted = sort.key === column.key;

  const style: React.CSSProperties = {};
  if (column.width) style.width = column.width;
  if (column.minWidth) style.minWidth = column.minWidth;
  if (column.maxWidth) style.maxWidth = column.maxWidth;

  return (
    <th
      className={cn(
        'h-10 px-2 text-left align-middle font-medium text-muted-foreground',
        column.align === 'center' && 'text-center',
        column.align === 'right' && 'text-right',
        column.sortable && 'cursor-pointer select-none'
      )}
      style={style}
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
    </th>
  );
}

function DataGridFilterRow() {
  const { columns, filters, setFilter, selectionMode } = useDataGridContext();
  const hasFilterable = columns.some((c) => c.filterable);

  if (!hasFilterable) return null;

  return (
    <tr className="border-b transition-colors">
      {selectionMode !== 'none' && <td className="p-2" />}
      {columns.map((col) => (
        <td key={col.key} className="p-2">
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
        </td>
      ))}
    </tr>
  );
}
