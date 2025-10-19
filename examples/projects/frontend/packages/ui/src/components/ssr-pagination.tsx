import React from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { cn } from '../lib/utils';
import { useIsMobile } from '../hooks';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
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
  prefetch?: boolean;
}

export const SSRPagination: React.FC<SSRPaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  hasNextPage,
  hasPreviousPage,
  className,
  showInfo = true,
  maxVisiblePages = 7,
  baseUrl,
  pathname,
  preserveQuery = true,
  prefetch = true,
}) => {
  const router = useRouter();
  const isMobile = useIsMobile();

  // Get current page from URL if available, otherwise use prop
  const getCurrentPageFromUrl = (): number => {
    const pageParam = router.query.page;
    if (pageParam && typeof pageParam === 'string') {
      const pageNum = parseInt(pageParam, 10);
      return isNaN(pageNum) ? 1 : pageNum;
    }
    return 1;
  };

  const actualCurrentPage = router.isReady ? getCurrentPageFromUrl() : currentPage;

  // Calculate actual navigation state based on current page from URL
  const actualHasPreviousPage = actualCurrentPage > 1;
  
  // Smart total pages calculation - if we're on a page higher than totalPages,
  // extend totalPages to include current page + some extra
  const smartTotalPages = Math.max(
    totalPages,
    actualCurrentPage + (hasNextPage ? 5 : 0)
  );
  
  const actualHasNextPage = hasNextPage;

  // Generate URL for a specific page
  const getPageUrl = (page: number): string => {
    if (baseUrl) {
      return `${baseUrl}?page=${page}`;
    }

    // Use current route with updated page parameter
    const query: Record<string, string | string[]> = {};
    if (preserveQuery) {
      Object.entries(router.query).forEach(([key, value]) => {
        if (value !== undefined) {
          query[key] = value;
        }
      });
    }
    query.page = page.toString();

    // Remove page=1 from URL to keep URLs clean
    if (page === 1) {
      delete query.page;
    }

    const queryString = new URLSearchParams(
      Object.entries(query).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null) {
          acc[key] = Array.isArray(value) ? value.join(',') : value.toString();
        }
        return acc;
      }, {} as Record<string, string>)
    ).toString();

    const basePath = pathname || router.pathname || '';
    return queryString ? `${basePath}?${queryString}` : basePath;
  };

  // Generate array of page numbers to display
  const getVisiblePages = (): (number | 'ellipsis')[] => {
    // On mobile, show fewer pages
    const mobileMaxVisible = 3;
    const effectiveMaxVisible = isMobile ? mobileMaxVisible : maxVisiblePages;
    
    if (smartTotalPages <= effectiveMaxVisible) {
      return Array.from({ length: smartTotalPages }, (_, i) => i + 1);
    }

    const pages: (number | 'ellipsis')[] = [];
    const halfVisible = Math.floor(effectiveMaxVisible / 2);

    if (isMobile) {
      // Mobile: Show only current page and adjacent pages
      if (actualCurrentPage > 1) {
        pages.push(actualCurrentPage - 1);
      }
      pages.push(actualCurrentPage);
      if (actualCurrentPage < smartTotalPages) {
        pages.push(actualCurrentPage + 1);
      }
    } else {
      // Desktop: Full pagination logic
      // Always show first page
      pages.push(1);

      let start = Math.max(2, actualCurrentPage - halfVisible);
      let end = Math.min(smartTotalPages - 1, actualCurrentPage + halfVisible);

      // Adjust range if we're near the beginning or end
      if (actualCurrentPage <= halfVisible + 1) {
        end = Math.min(smartTotalPages - 1, effectiveMaxVisible - 1);
      } else if (actualCurrentPage >= smartTotalPages - halfVisible) {
        start = Math.max(2, smartTotalPages - effectiveMaxVisible + 2);
      }

      // Add ellipsis after first page if needed
      if (start > 2) {
        pages.push('ellipsis');
      }

      // Add middle pages
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      // Add ellipsis before last page if needed
      if (end < smartTotalPages - 1) {
        pages.push('ellipsis');
      }

      // Always show last page (if more than 1 page)
      if (smartTotalPages > 1) {
        pages.push(smartTotalPages);
      }
    }

    return pages;
  };

  // Don't render if there's only one page or no pages
  if (smartTotalPages <= 1) {
    return null;
  }

  const visiblePages = getVisiblePages();
  const startItem = (actualCurrentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(actualCurrentPage * itemsPerPage, totalItems);

  return (
    <div className={cn("space-y-4", className)}>
      {/* Pagination Info */}
      {showInfo && (
        <div className="text-sm text-muted-foreground text-center">
          {isMobile ? (
            `Page ${actualCurrentPage} of ${smartTotalPages}`
          ) : (
            `Showing ${startItem.toLocaleString()} to ${endItem.toLocaleString()} of ${totalItems.toLocaleString()} results`
          )}
        </div>
      )}

      {/* Pagination Controls */}
      <Pagination>
        <PaginationContent>
          {/* Previous Button */}
          <PaginationItem>
            {actualHasPreviousPage ? (
              <Link href={getPageUrl(actualCurrentPage - 1)} prefetch={prefetch} passHref legacyBehavior>
                <PaginationPrevious />
              </Link>
            ) : (
              <PaginationPrevious 
                href="#" 
                className="pointer-events-none opacity-50"
                onClick={(e) => e.preventDefault()}
              />
            )}
          </PaginationItem>

          {/* Page Numbers */}
          {visiblePages.map((page, index) => (
            <PaginationItem key={index}>
              {page === 'ellipsis' ? (
                <PaginationEllipsis />
              ) : (
                <Link href={getPageUrl(page)} prefetch={prefetch} passHref legacyBehavior>
                  <PaginationLink isActive={page === actualCurrentPage}>
                    {page}
                  </PaginationLink>
                </Link>
              )}
            </PaginationItem>
          ))}

          {/* Next Button */}
          <PaginationItem>
            {hasNextPage ? (
              <Link href={getPageUrl(actualCurrentPage + 1)} prefetch={prefetch} passHref legacyBehavior>
                <PaginationNext />
              </Link>
            ) : (
              <PaginationNext 
                href="#" 
                className="pointer-events-none opacity-50"
                onClick={(e) => e.preventDefault()}
              />
            )}
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

SSRPagination.displayName = 'SSRPagination';
