import React from 'react';

import { Link } from '../link';
import {
    Breadcrumb, BreadcrumbEllipsis, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage,
    BreadcrumbSeparator
} from './breadcrumb';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  /**
   * Force render as current page (non-interactive, aria-current="page").
   * By default only the last item without href is treated as current page.
   */
  isCurrentPage?: boolean;
  icon?: React.ReactNode;
}

export interface BreadcrumbNavigationProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  /**
   * Max visible items (excluding the ellipsis slot) before collapsing.
   * Must be >= 2. Defaults to 5.
   */
  maxItems?: number;
  className?: string;
}

type DisplayEntry =
  | { type: 'item'; item: BreadcrumbItem; originalIndex: number }
  | { type: 'ellipsis' };

export const BreadcrumbNavigation: React.FC<BreadcrumbNavigationProps> = ({
  items,
  separator,
  maxItems = 5,
  className,
}) => {
  if (!items || items.length === 0) return null;

  const clampedMax = Math.max(2, maxItems);

  const entries: DisplayEntry[] = (() => {
    if (items.length <= clampedMax) {
      return items.map((item, i) => ({ type: 'item' as const, item, originalIndex: i }));
    }
    const tailCount = Math.max(1, clampedMax - 2);
    const tail = items.slice(-tailCount).map((item, i) => ({
      type: 'item' as const,
      item,
      originalIndex: items.length - tailCount + i,
    }));
    return [
      { type: 'item' as const, item: items[0]!, originalIndex: 0 },
      { type: 'ellipsis' as const },
      ...tail,
    ];
  })();

  const resolveIsCurrentPage = (item: BreadcrumbItem, originalIndex: number): boolean => {
    if (item.isCurrentPage !== undefined) return item.isCurrentPage;
    return originalIndex === items.length - 1;
  };

  const renderItem = (item: BreadcrumbItem, originalIndex: number) => {
    const current = resolveIsCurrentPage(item, originalIndex);

    const content = (
      <>
        {item.icon && <span className="mr-1">{item.icon}</span>}
        {item.label}
      </>
    );

    if (current) {
      return (
        <BreadcrumbItem key={`item-${originalIndex}`}>
          <BreadcrumbPage>{content}</BreadcrumbPage>
        </BreadcrumbItem>
      );
    }

    return (
      <BreadcrumbItem key={`item-${originalIndex}`}>
        {item.href ? (
          <BreadcrumbLink asChild>
            <Link href={item.href}>{content}</Link>
          </BreadcrumbLink>
        ) : (
          <BreadcrumbLink>{content}</BreadcrumbLink>
        )}
      </BreadcrumbItem>
    );
  };

  return (
    <Breadcrumb className={className}>
      <BreadcrumbList>
        {entries.map((entry, displayIndex) => {
          const isFirst = displayIndex === 0;

          if (entry.type === 'ellipsis') {
            return (
              <React.Fragment key="ellipsis">
                <BreadcrumbSeparator>{separator}</BreadcrumbSeparator>
                <BreadcrumbItem>
                  <BreadcrumbEllipsis />
                </BreadcrumbItem>
              </React.Fragment>
            );
          }

          return (
            <React.Fragment key={`fragment-${entry.originalIndex}`}>
              {!isFirst && <BreadcrumbSeparator>{separator}</BreadcrumbSeparator>}
              {renderItem(entry.item, entry.originalIndex)}
            </React.Fragment>
          );
        })}
      </BreadcrumbList>
    </Breadcrumb>
  );
};

BreadcrumbNavigation.displayName = 'BreadcrumbNavigation';
