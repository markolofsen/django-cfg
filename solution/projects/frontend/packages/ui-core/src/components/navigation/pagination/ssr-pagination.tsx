'use client';

import React from 'react';

import { useAppT, useI18n } from '@djangocfg/i18n';

import { cn, formatNumber } from '../../../lib';
import { useIsMobile } from '../../../hooks';
import { useLocation, useQueryParams } from '../../../hooks/router';

import {
    Pagination, PaginationContent, PaginationItem, PaginationLink,
    PaginationNext, PaginationPrevious
} from './pagination';

interface SSRPaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  className?: string;
  showInfo?: boolean;
  maxVisiblePages?: number;
  baseUrl?: string;
  pathname?: string;
  preserveQuery?: boolean;
}

function buildSearch(params: Record<string, string | string[]>, page: number, preserveQuery: boolean): string {
  const next = new URLSearchParams();
  if (preserveQuery) {
    for (const [key, value] of Object.entries(params)) {
      if (key === 'page') continue;
      if (Array.isArray(value)) {
        for (const v of value) next.append(key, v);
      } else {
        next.set(key, value);
      }
    }
  }
  if (page !== 1) next.set('page', page.toString());
  return next.toString();
}

export const SSRPagination: React.FC<SSRPaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  hasNextPage,
  hasPreviousPage: _hasPreviousPage,
  className,
  showInfo = true,
  maxVisiblePages = 7,
  baseUrl,
  pathname: propPathname,
  preserveQuery = true,
}) => {
  const queryParams = useQueryParams();
  const { pathname } = useLocation();
  const isMobile = useIsMobile();
  const t = useAppT();
  const { locale } = useI18n();

  /* The URL wins when it carries a page, the prop otherwise.
   *
   * During the server render `useQueryParams()` is empty, so the old
   * `getCurrentPageFromUrl() || currentPage` always resolved to 1 — the
   * fallback to the prop could never run, because the function returned 1
   * rather than a falsy value. Every server-rendered page built its number
   * window around page 1: `/search?page=100` linked 2–6 and the last page,
   * never 99 or 101. Pages 7..N-1 were linked from nowhere in the HTML a
   * crawler reads, which is the only HTML a crawler reads. */
  const getCurrentPageFromUrl = (): number | null => {
    const pageParam = queryParams.get('page');
    if (!pageParam) return null;
    const pageNum = parseInt(pageParam, 10);
    return isNaN(pageNum) || pageNum < 1 ? null : pageNum;
  };

  const actualCurrentPage = getCurrentPageFromUrl() ?? currentPage;
  const actualHasPreviousPage = actualCurrentPage > 1;

  const getPageUrl = (page: number): string => {
    if (baseUrl) {
      return `${baseUrl}?page=${page}`;
    }
    const queryString = buildSearch(queryParams.params, page, preserveQuery);
    const basePath = propPathname || pathname || '';
    return queryString ? `${basePath}?${queryString}` : basePath;
  };

  /* NO "first" / "last" BUTTONS, deliberately.
   *
   * `ui.pagination.first` and `.last` exist in the dictionary and nothing
   * renders them. That is the right outcome, not an omission to finish:
   *
   * - The row ALREADY ENDS IN BOTH. `1` is always pushed first and
   *   `totalPages` always last, so a jump to either end is one click on a
   *   number the reader can already see. A dedicated button would be a third
   *   route to a place two already reach.
   * - "Last" is a destination nobody wants. On a catalogue sorted by date or
   *   price, page 34,781 is the worst match for the query — the control is
   *   cheap to build and answers a question no one asks.
   *
   * Two chevrons and the numbers. Anything more is furniture. */
  /* An ellipsis is a link to the MIDDLE of the pages it hides.
   *
   * It used to be inert text, so the only pages a crawler could reach were the
   * ones in the window, one step at a time: 267 pages took ~90 hops. Linking
   * each gap's midpoint halves the unexplored range with every hop, so any
   * page is ~log2(N) hops from page 1 (8 for 267). A reader gets a "jump
   * roughly there" control, which is what an ellipsis promises anyway. */
  type PageItem = number | { ellipsis: number };

  const getVisiblePages = (): PageItem[] => {
    const mobileMaxVisible = 3;
    const effectiveMaxVisible = isMobile ? mobileMaxVisible : maxVisiblePages;

    if (totalPages <= effectiveMaxVisible) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const pages: PageItem[] = [];
    const halfVisible = Math.floor(effectiveMaxVisible / 2);

    if (isMobile) {
      if (actualCurrentPage > 1) pages.push(actualCurrentPage - 1);
      pages.push(actualCurrentPage);
      if (actualCurrentPage < totalPages) pages.push(actualCurrentPage + 1);
    } else {
      pages.push(1);

      let start = Math.max(2, actualCurrentPage - halfVisible);
      let end = Math.min(totalPages - 1, actualCurrentPage + halfVisible);

      if (actualCurrentPage <= halfVisible + 1) {
        end = Math.min(totalPages - 1, effectiveMaxVisible - 1);
      } else if (actualCurrentPage >= totalPages - halfVisible) {
        start = Math.max(2, totalPages - effectiveMaxVisible + 2);
      }

      if (start > 2) pages.push({ ellipsis: Math.floor((2 + start - 1) / 2) });
      for (let i = start; i <= end; i++) pages.push(i);
      if (end < totalPages - 1) {
        pages.push({ ellipsis: Math.floor((end + 1 + totalPages - 1) / 2) });
      }
      if (totalPages > 1) pages.push(totalPages);
    }

    return pages;
  };

  const visiblePages = getVisiblePages();
  const startItem = (actualCurrentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(actualCurrentPage * itemsPerPage, totalItems);

  if (totalItems === 0) {
    return null;
  }

  return (
    <div className={cn("space-y-4", className)}>
      {showInfo && (
        <div className="text-sm text-muted-foreground text-center">
          {/* Through `ui.pagination.*`, which ships translated in every
              locale this package supports. The figures are grouped with
              `toLocaleString(locale)` rather than the host's default, so a
              German reader sees `1.234` and a French one `1 234`. */}
          {isMobile
            ? `${t('ui.pagination.page', { page: actualCurrentPage })} ${t('ui.pagination.of', { total: totalPages })}`
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
            <PaginationPrevious
              href={actualHasPreviousPage ? getPageUrl(actualCurrentPage - 1) : undefined}
              className={!actualHasPreviousPage ? "pointer-events-none opacity-50" : undefined}
              scroll
            />
          </PaginationItem>

          {visiblePages.map((page, index) => (
            <PaginationItem key={index}>
              {typeof page === 'object' ? (
                <PaginationLink
                  href={getPageUrl(page.ellipsis)}
                  aria-label={t('ui.pagination.page', { page: page.ellipsis })}
                  scroll
                >
                  …
                </PaginationLink>
              ) : (
                <PaginationLink
                  href={getPageUrl(page)}
                  isActive={page === actualCurrentPage}
                  scroll
                >
                  {/* GROUPED, not compacted. `34 781` reads; `34781` is
                      scanned digit by digit. But never `34,8 тыс.` — this is
                      a destination the reader clicks, and a rounded address
                      is not an address. Compaction belongs on counts, never
                      on page numbers. */}
                  {formatNumber(page, locale)}
                </PaginationLink>
              )}
            </PaginationItem>
          ))}

          <PaginationItem>
            <PaginationNext
              href={hasNextPage ? getPageUrl(actualCurrentPage + 1) : undefined}
              className={!hasNextPage ? "pointer-events-none opacity-50" : undefined}
              scroll
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

SSRPagination.displayName = 'SSRPagination';
