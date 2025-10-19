import React from 'react';
import Link from 'next/link';
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbPage,
  BreadcrumbSeparator,
  BreadcrumbEllipsis,
} from './breadcrumb';
import { cn } from '../lib/utils';

export interface BreadcrumbItem {
  /** Display text for the breadcrumb */
  label: string;
  /** URL to navigate to. If not provided, item will be rendered as current page */
  href?: string;
  /** Whether this item is the current page (will be rendered as BreadcrumbPage) */
  isCurrentPage?: boolean;
  /** Optional icon to display before the label */
  icon?: React.ReactNode;
}

export interface BreadcrumbNavigationProps {
  /** Array of breadcrumb items */
  items: BreadcrumbItem[];
  /** Custom separator between items */
  separator?: React.ReactNode;
  /** Maximum number of items to show before collapsing with ellipsis */
  maxItems?: number;
  /** Custom className for the breadcrumb container */
  className?: string;
  /** Whether to use Next.js Link component for navigation */
  useNextLink?: boolean;
}

export const BreadcrumbNavigation: React.FC<BreadcrumbNavigationProps> = ({
  items,
  separator,
  maxItems = 5,
  className,
  useNextLink = true,
}) => {
  // Handle empty or single item cases
  if (!items || items.length === 0) {
    return null;
  }

  // Determine which items to show based on maxItems
  const shouldCollapse = items.length > maxItems;
  let displayItems: BreadcrumbItem[] = items;

  if (shouldCollapse && items.length > 0) {
    // Show first item, ellipsis, and last few items
    if(items.length > 0) {
        const firstItem = items[0]!;
        const lastItems = items.slice(-(maxItems - 2)).filter(Boolean);
        displayItems = [firstItem, ...lastItems];
    }
  }

  const renderBreadcrumbItem = (item: BreadcrumbItem, index: number, isLast: boolean) => {
    const isCurrentPage = item.isCurrentPage || isLast || !item.href;

    const content = (
      <>
        {item.icon && <span className="mr-1">{item.icon}</span>}
        {item.label}
      </>
    );

    if (isCurrentPage) {
      return (
        <BreadcrumbItem key={`${item.label}-${index}`}>
          <BreadcrumbPage>{content}</BreadcrumbPage>
        </BreadcrumbItem>
      );
    }

    return (
      <BreadcrumbItem key={`${item.label}-${index}`}>
        <BreadcrumbLink asChild={useNextLink}>
          {useNextLink ? (
            <Link href={item.href!}>{content}</Link>
          ) : (
            <a href={item.href!}>{content}</a>
          )}
        </BreadcrumbLink>
      </BreadcrumbItem>
    );
  };

  return (
    <Breadcrumb className={className}>
      <BreadcrumbList>
        {displayItems.map((item, index) => {
          const isLast = index === displayItems.length - 1;
          const isFirst = index === 0;
          
          // Show ellipsis after first item if we collapsed items
          if (shouldCollapse && isFirst && displayItems.length > 2) {
            return (
              <React.Fragment key={`fragment-${index}`}>
                {renderBreadcrumbItem(item, index, isLast)}
                <BreadcrumbSeparator>{separator}</BreadcrumbSeparator>
                <BreadcrumbItem>
                  <BreadcrumbEllipsis />
                </BreadcrumbItem>
                {!isLast && <BreadcrumbSeparator>{separator}</BreadcrumbSeparator>}
              </React.Fragment>
            );
          }

          return (
            <React.Fragment key={`fragment-${index}`}>
              {renderBreadcrumbItem(item, index, isLast)}
              {!isLast && <BreadcrumbSeparator>{separator}</BreadcrumbSeparator>}
            </React.Fragment>
          );
        })}
      </BreadcrumbList>
    </Breadcrumb>
  );
};

BreadcrumbNavigation.displayName = 'BreadcrumbNavigation';
