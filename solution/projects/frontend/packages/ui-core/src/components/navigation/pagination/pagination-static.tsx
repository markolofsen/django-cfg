/**
 * DRF Static Pagination Component
 *
 * Universal pagination component that works with Django REST Framework pagination format.
 * Manages page state internally and provides callbacks for page changes.
 */

"use client"

import { ChevronLeft, ChevronRight } from 'lucide-react';
import React from 'react';

import { useAppT, useI18n } from '@djangocfg/i18n';

import { cn, formatNumber } from '../../../lib';
import { Button } from '../../forms/button';
import { useIsMobile } from '../../../hooks';

import {
    Pagination, PaginationContent, PaginationEllipsis, PaginationItem
} from './pagination';

export interface DRFPaginatedResponse<T = unknown> {
  count: number;
  page: number;
  pages: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
  next_page?: number | null;
  previous_page?: number | null;
  results: T[];
}

interface StaticPaginationProps {
  data?: DRFPaginatedResponse | null;
  onPageChange: (page: number) => void;
  className?: string;
  showInfo?: boolean;
  maxVisiblePages?: number;
}

export const StaticPagination: React.FC<StaticPaginationProps> = ({
  data,
  onPageChange,
  className,
  showInfo = true,
  maxVisiblePages = 7,
}) => {
  const isMobile = useIsMobile();
  const t = useAppT();
  const { locale } = useI18n();

  if (!data || !('count' in data) || !('page' in data) || !('pages' in data)) {
    return null;
  }

  const {
    count: totalItems,
    page: currentPage,
    pages: totalPages,
    page_size: itemsPerPage,
    has_next: hasNextPage,
    has_previous: hasPreviousPage,
  } = data;

  if (totalPages <= 1) {
    return null;
  }

  const getVisiblePages = (): (number | 'ellipsis')[] => {
    const mobileMaxVisible = 3;
    const effectiveMaxVisible = isMobile ? mobileMaxVisible : maxVisiblePages;

    if (totalPages <= effectiveMaxVisible) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const pages: (number | 'ellipsis')[] = [];
    const halfVisible = Math.floor(effectiveMaxVisible / 2);

    if (isMobile) {
      if (currentPage > 1) {
        pages.push(currentPage - 1);
      }
      pages.push(currentPage);
      if (currentPage < totalPages) {
        pages.push(currentPage + 1);
      }
    } else {
      pages.push(1);

      let start = Math.max(2, currentPage - halfVisible);
      let end = Math.min(totalPages - 1, currentPage + halfVisible);

      if (currentPage <= halfVisible + 1) {
        end = Math.min(totalPages - 1, effectiveMaxVisible - 1);
      } else if (currentPage >= totalPages - halfVisible) {
        start = Math.max(2, totalPages - effectiveMaxVisible + 2);
      }

      if (start > 2) {
        pages.push('ellipsis');
      }

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (end < totalPages - 1) {
        pages.push('ellipsis');
      }

      if (totalPages > 1) {
        pages.push(totalPages);
      }
    }

    return pages;
  };

  const visiblePages = getVisiblePages();
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  const handlePageClick = (page: number) => {
    if (page !== currentPage && page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
  };

  return (
    <div className={cn("space-y-4", className)}>
      {showInfo && (
        <div className="text-sm text-muted-foreground text-center">
          {/* Through `ui.pagination.*`, which ships translated in every
              locale this package supports. The figures are grouped with
              `toLocaleString(locale)` rather than the host's default, so a
              German reader sees `1.234` and a French one `1 234`. */}
          {isMobile
            ? `${t('ui.pagination.page', { page: currentPage })} ${t('ui.pagination.of', { total: totalPages })}`
            : t('ui.pagination.showing', {
                from: formatNumber(startItem, locale),
                to: formatNumber(endItem, locale),
                total: formatNumber(totalItems, locale),
              })}
        </div>
      )}

      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <Button
              variant="ghost"
              size="default"
              onClick={() => handlePageClick(currentPage - 1)}
              disabled={!hasPreviousPage}
              className={cn(
                "gap-1 pl-2.5",
                !hasPreviousPage && "pointer-events-none opacity-50"
              )}
              aria-label={t('ui.pagination.previous')}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </PaginationItem>

          {visiblePages.map((page, index) => (
            <PaginationItem key={index}>
              {page === 'ellipsis' ? (
                <PaginationEllipsis />
              ) : (
                <Button
                  variant={page === currentPage ? "outline" : "ghost"}
                  size="icon"
                  onClick={() => handlePageClick(page)}
                  aria-current={page === currentPage ? "page" : undefined}
                  className={cn(
                    page === currentPage && "pointer-events-none"
                  )}
                >
                  {/* GROUPED, not compacted. `34 781` reads; `34781` is
                      scanned digit by digit. But never `34,8 тыс.` — this is
                      a destination the reader clicks, and a rounded address
                      is not an address. Compaction belongs on counts, never
                      on page numbers. */}
                  {formatNumber(page, locale)}
                </Button>
              )}
            </PaginationItem>
          ))}

          <PaginationItem>
            <Button
              variant="ghost"
              size="default"
              onClick={() => handlePageClick(currentPage + 1)}
              disabled={!hasNextPage}
              className={cn(
                "gap-1 pr-2.5",
                !hasNextPage && "pointer-events-none opacity-50"
              )}
              aria-label={t('ui.pagination.next')}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

StaticPagination.displayName = 'StaticPagination';

export function useDRFPagination(initialPage = 1, initialPageSize = 10) {
  const [page, setPage] = React.useState(initialPage);
  const [pageSize, setPageSize] = React.useState(initialPageSize);

  const handlePageSizeChange = React.useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1);
  }, []);

  const params = React.useMemo(() => ({
    page,
    page_size: pageSize,
  }), [page, pageSize]);

  return {
    page,
    pageSize,
    setPage,
    setPageSize: handlePageSizeChange,
    params,
    reset: () => {
      setPage(initialPage);
      setPageSize(initialPageSize);
    },
  };
}

export function useDRFPaginationInfo(data?: DRFPaginatedResponse | null) {
  return React.useMemo(() => {
    if (!data || !('count' in data) || !('page' in data)) {
      return null;
    }

    return {
      totalItems: data.count,
      currentPage: data.page,
      totalPages: data.pages,
      itemsPerPage: data.page_size,
      hasNext: data.has_next,
      hasPrevious: data.has_previous,
      nextPage: data.next_page,
      previousPage: data.previous_page,
      results: data.results || [],
      resultsCount: data.results?.length || 0,
    };
  }, [data]);
}
