'use client';

import * as React from 'react';
import {
  Button,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@djangocfg/ui-core/components';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

import { useDataTableContext } from '../context/DataTableContext';

export function DataTablePagination() {
  const { pagination, setPage, setPageSize, totalRows, pageCount, pageSizeOptions } =
    useDataTableContext();

  const start = totalRows === 0 ? 0 : (pagination.page - 1) * pagination.pageSize + 1;
  const end = Math.min(pagination.page * pagination.pageSize, totalRows);

  return (
    <div
      data-slot="data-table-pagination"
      className="flex flex-col items-center justify-between gap-2 border-t border-border px-4 py-2 sm:flex-row"
    >
      <span className="text-sm text-muted-foreground">
        {start}-{end} of {totalRows}
      </span>

      <div className="flex items-center gap-2">
        <Select
          value={String(pagination.pageSize)}
          onValueChange={(value) => setPageSize(Number(value))}
        >
          {/* `--radius` is the shared control corner used by ui-core <Button>,
            * so the page-size trigger and the nav buttons round identically. */}
          <SelectTrigger
            className="h-8 w-auto gap-1 rounded-[var(--radius)] px-2 shadow-none"
            aria-label="Rows per page"
          >
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {pageSizeOptions.map((size) => (
              <SelectItem key={size} value={String(size)}>
                {size} / page
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Nav controls reuse the library <Button> (outline/icon) rather than a
          * bespoke button, so hover, disabled, focus-ring and radius all track
          * the rest of the app automatically. `h-8 w-8` shrinks the default
          * icon size (h-9 w-9) to match the compact pagination row.
          * `elevated={false}` drops the variant's shadow so the buttons sit
          * flat against the panel, matching the shadow-less page-size select. */}
        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            elevated={false}
            className="h-8 w-8"
            onClick={() => setPage(1)}
            disabled={pagination.page <= 1}
            aria-label="First page"
          >
            <ChevronsLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            elevated={false}
            className="h-8 w-8"
            onClick={() => setPage(pagination.page - 1)}
            disabled={pagination.page <= 1}
            aria-label="Previous page"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>

          <span className="px-2 text-sm tabular-nums">
            {pagination.page} / {pageCount}
          </span>

          <Button
            variant="outline"
            size="icon"
            elevated={false}
            className="h-8 w-8"
            onClick={() => setPage(pagination.page + 1)}
            disabled={pagination.page >= pageCount}
            aria-label="Next page"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            elevated={false}
            className="h-8 w-8"
            onClick={() => setPage(pageCount)}
            disabled={pagination.page >= pageCount}
            aria-label="Last page"
          >
            <ChevronsRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
DataTablePagination.displayName = 'DataTablePagination';
