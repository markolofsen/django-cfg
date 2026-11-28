'use client';

import { ChevronDown } from 'lucide-react';
import React, { memo } from 'react';

import { Button, Link } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import type { NavigationItem } from '../../types';
import { navItemsShallowEqual } from '../../../utils/navItemsShallowEqual';
import type { UseDropdownMenuReturn } from '../hooks/useDropdownMenu';
import { useResponsiveOverflow } from '../hooks/useResponsiveOverflow';
import type { PublicDesktopDropdownRenderer } from '../navbarTypes';
import { DesktopDropdownPortal } from './DesktopDropdownPortal';
import { labelCls, navItemActiveCls, navItemCls, popoverCls, subMenuLinkCls } from './navDesktopStyles';

interface NavDesktopItemsProps {
  /** Full ordered item list; overflow is computed responsively. */
  items: NavigationItem[];
  /** Optional hard cap — measurer will never show more than this. */
  maxVisible?: number;
  isActivePath: (href: string) => boolean;
  isGroupActive: (item: NavigationItem) => boolean;
  dropdown: UseDropdownMenuReturn;
  renderDesktopDropdown?: PublicDesktopDropdownRenderer;
}

function NavDesktopItemsRaw({
  items,
  maxVisible,
  isActivePath,
  isGroupActive,
  dropdown,
  renderDesktopDropdown,
}: NavDesktopItemsProps) {
  const { openDropdownKey, scheduleOpen, scheduleClose, closeDropdown } = dropdown;
  const [portalAnchor, setPortalAnchor] = React.useState<{ key: string; element: HTMLElement } | null>(null);

  const { visibleCount, containerRef, itemRef, measured } = useResponsiveOverflow({
    total: items.length,
    moreWidth: 88,
    gap: 4,
  });

  const effectiveCount = measured
    ? Math.min(visibleCount, maxVisible ?? visibleCount)
    : (maxVisible ?? items.length);
  const primaryItems = items.slice(0, effectiveCount);
  const overflowItems = measured ? items.slice(effectiveCount) : [];

  const renderItem = (item: NavigationItem) => {
    if (item.items && item.items.length > 0) {
      const key = `${item.label}-${item.href}`;
      const isOpen = openDropdownKey === key;
      const isActive = isGroupActive(item);

      const defaultItems = (
        <>
          {item.items.map((sub) => {
            const subActive = isActivePath(sub.href);
            return (
              <div key={`${item.label}-${sub.href}`} className="rounded-control">
                {sub.external ? (
                  <a
                    href={sub.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={subMenuLinkCls(subActive)}
                  >
                    <span className="min-w-0 truncate" title={sub.label}>{sub.label}</span>
                  </a>
                ) : (
                  <Link href={sub.href} className={subMenuLinkCls(subActive)}>
                    <span className="min-w-0 truncate" title={sub.label}>{sub.label}</span>
                  </Link>
                )}
              </div>
            );
          })}
        </>
      );

      const defaultPopover = (
        <div
          className={popoverCls}
          onMouseEnter={() => { scheduleOpen(key); }}
          onMouseLeave={() => scheduleClose(key)}
        >
          {defaultItems}
        </div>
      );

      const defaultPortalPopover = isOpen && portalAnchor?.key === key ? (
        <DesktopDropdownPortal
          anchor={portalAnchor.element}
          onMouseEnter={() => { scheduleOpen(key); }}
          onMouseLeave={() => scheduleClose(key)}
        >
          {defaultItems}
        </DesktopDropdownPortal>
      ) : null;

      return (
        <div
          key={key}
          className="relative"
          onMouseEnter={(event) => {
            setPortalAnchor({ key, element: event.currentTarget });
            scheduleOpen(key);
          }}
          onMouseLeave={() => scheduleClose(key)}
        >
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              'group h-auto min-h-9 max-w-[15rem] gap-1 shadow-none [&_svg]:size-3.5 [&_svg]:shrink-0',
              navItemCls,
              (isOpen || isActive) && navItemActiveCls,
            )}
          >
            <span className={labelCls} title={item.label}>{item.label}</span>
            <span className="inline-flex size-3.5 shrink-0 items-center justify-center" aria-hidden>
              <ChevronDown
                className={cn(
                  'size-3.5 origin-center text-muted-foreground transition-transform duration-200 ease-out will-change-transform',
                  isOpen && 'rotate-180',
                )}
              />
            </span>
          </Button>

          {isOpen && (
            renderDesktopDropdown
              ? renderDesktopDropdown({ item, isOpen, isActive, close: closeDropdown, defaultPopover, defaultItems })
              : defaultPortalPopover
          )}
        </div>
      );
    }

    const active = isActivePath(item.href);
    return (
      <Link
        key={item.href}
        href={item.href}
        className={cn(navItemCls, active && navItemActiveCls)}
      >
        <span className={labelCls} title={item.label}>{item.label}</span>
      </Link>
    );
  };

  const hasOverflow = overflowItems.length > 0;
  const isMoreOpen = openDropdownKey === '__overflow-more';
  const moreActive = isMoreOpen || overflowItems.some((i) => isGroupActive(i));

  return (
    <div
      ref={containerRef as React.Ref<HTMLDivElement>}
      className="relative flex min-w-0 flex-1 items-center justify-center gap-1"
    >
      {/* Measurement layer: invisible, absolutely positioned, holds width-only copies. */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-y-0 left-0 flex items-center gap-1 opacity-0"
        style={{ visibility: 'hidden', whiteSpace: 'nowrap' }}
      >
        {items.map((item, i) => (
          <span
            key={`m-${item.label}-${item.href}`}
            ref={itemRef(i) as React.Ref<HTMLSpanElement>}
            className={cn(navItemCls, 'pointer-events-none')}
          >
            <span className={labelCls}>{item.label}</span>
            {item.items && item.items.length > 0 && (
              <span className="inline-flex size-3.5 shrink-0 items-center justify-center">
                <ChevronDown className="size-3.5" />
              </span>
            )}
          </span>
        ))}
      </div>

      {/* Live row — renders all items on SSR, overflow splits after measurement. */}
      <div className="flex min-w-0 items-center gap-1">
        {primaryItems.map(renderItem)}

        {hasOverflow && (
          <div
            className="relative"
            onMouseEnter={() => scheduleOpen('__overflow-more')}
            onMouseLeave={() => scheduleClose('__overflow-more')}
          >
            <Button
              variant="ghost"
              size="sm"
              className={cn(
                'group h-auto min-h-9 max-w-[15rem] gap-1 shadow-none [&_svg]:size-3.5 [&_svg]:shrink-0',
                navItemCls,
                moreActive && navItemActiveCls,
              )}
            >
              <span className={labelCls}>More</span>
              <span className="inline-flex size-3.5 shrink-0 items-center justify-center" aria-hidden>
                <ChevronDown
                  className={cn(
                    'size-3.5 origin-center text-muted-foreground transition-transform duration-200 ease-out will-change-transform',
                    isMoreOpen && 'rotate-180',
                  )}
                />
              </span>
            </Button>

            {isMoreOpen && (
              <div
                className={cn(popoverCls, 'left-auto right-0')}
                onMouseEnter={() => { scheduleOpen('__overflow-more'); }}
                onMouseLeave={() => scheduleClose('__overflow-more')}
              >
                {overflowItems.map((item) => {
                  const active = isGroupActive(item);
                  return (
                    <div key={`overflow-${item.href}`} className="rounded-control">
                      <Link href={item.href} className={subMenuLinkCls(active)}>
                        <span className="min-w-0 truncate" title={item.label}>{item.label}</span>
                      </Link>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Memoised desktop navigation row. Re-renders only when:
 * - the items array content changes (via navItemsShallowEqual),
 * - dropdown state object changes,
 * - maxVisible or renderDesktopDropdown changes.
 * Parent re-renders with identical navigation data are skipped entirely.
 */
export const NavDesktopItems = memo(NavDesktopItemsRaw, (prev, next) => {
  return (
    prev.maxVisible === next.maxVisible &&
    prev.isActivePath === next.isActivePath &&
    prev.isGroupActive === next.isGroupActive &&
    prev.dropdown === next.dropdown &&
    prev.renderDesktopDropdown === next.renderDesktopDropdown &&
    navItemsShallowEqual(prev.items, next.items)
  );
});
