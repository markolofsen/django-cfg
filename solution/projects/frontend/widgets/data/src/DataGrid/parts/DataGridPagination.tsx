'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

import { useDataGridContext } from '../context/DataGridContext';

export function DataGridPagination() {
  const { pagination, setPage, setPageSize, totalRows, pageCount, pageSizeOptions } =
    useDataGridContext();

  const start = totalRows === 0 ? 0 : (pagination.page - 1) * pagination.pageSize + 1;
  const end = Math.min(pagination.page * pagination.pageSize, totalRows);

  return (
    <div
      data-slot="data-grid-pagination"
      className="flex flex-col items-center justify-between gap-2 px-4 py-2 sm:flex-row"
    >
      <span className="text-sm text-muted-foreground">
        {start}-{end} of {totalRows}
      </span>

      <div className="flex items-center gap-2">
        <select
          value={pagination.pageSize}
          onChange={(e) => setPageSize(Number(e.target.value))}
          className={cn(
            'h-8 rounded-sm border border-input bg-background px-2 text-sm',
            'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'
          )}
          aria-label="Rows per page"
        >
          {pageSizeOptions.map((size) => (
            <option key={size} value={size}>
              {size} / page
            </option>
          ))}
        </select>

        <div className="flex items-center gap-1">
          <PaginationButton
            onClick={() => setPage(1)}
            disabled={pagination.page <= 1}
            aria-label="First page"
          >
            <ChevronsLeft className="h-4 w-4" />
          </PaginationButton>
          <PaginationButton
            onClick={() => setPage(pagination.page - 1)}
            disabled={pagination.page <= 1}
            aria-label="Previous page"
          >
            <ChevronLeft className="h-4 w-4" />
          </PaginationButton>

          <span className="px-2 text-sm tabular-nums">
            {pagination.page} / {pageCount}
          </span>

          <PaginationButton
            onClick={() => setPage(pagination.page + 1)}
            disabled={pagination.page >= pageCount}
            aria-label="Next page"
          >
            <ChevronRight className="h-4 w-4" />
          </PaginationButton>
          <PaginationButton
            onClick={() => setPage(pageCount)}
            disabled={pagination.page >= pageCount}
            aria-label="Last page"
          >
            <ChevronsRight className="h-4 w-4" />
          </PaginationButton>
        </div>
      </div>
    </div>
  );
}
DataGridPagination.displayName = 'DataGridPagination';

function PaginationButton({
  children,
  onClick,
  disabled,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'inline-flex h-8 w-8 items-center justify-center rounded-sm border border-input bg-background text-sm',
        'hover:bg-accent hover:text-accent-foreground',
        'disabled:pointer-events-none disabled:opacity-50',
        'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'
      )}
      {...props}
    >
      {children}
    </button>
  );
}
