/**
 * Sidebar header: brand (or workspace switcher) on the left, one control on the
 * right — collapse on desktop, close on the mobile drawer.
 */

'use client';

import React, { memo } from 'react';

import { Link, useSidebar } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { LucideIcon } from '../../../components';
import { usePrivateLayoutContext } from '../context';
import { SIDEBAR_SPACING } from '../geometry';
import { PrivateSidebarTrigger } from './PrivateSidebarTrigger';
import { SidebarBrandSwitcher } from './SidebarBrandSwitcher';

const BRAND_LINK =
  'flex min-w-0 items-center gap-2.5 rounded-lg py-1 pointer-coarse:min-h-11 text-sidebar-foreground no-underline outline-none ring-sidebar-ring transition-opacity hover:no-underline hover:opacity-80 focus-visible:ring-2';

/** Brand name: semibold, one step larger on desktop (18px), 16px on a phone; one line, truncated. */
const BRAND_NAME = 'truncate text-base font-semibold tracking-tight md:text-sm md:font-medium';

function SidebarBrandRaw({ bordered = false }: { bordered?: boolean }) {
  const { header, homeHref, brandTitle, brandMonogram, isMobile } = usePrivateLayoutContext();

  const { isMobile: drawer, setOpenMobile } = useSidebar();
  // On a phone the drawer closes on click, also when the target is the current page (no pathname change).
  const closeDrawer = React.useCallback(() => {
    if (drawer) setOpenMobile(false);
  }, [drawer, setOpenMobile]);

  const customBrand = header?.brand;

  const brand =
    customBrand != null && customBrand !== false ? (
      typeof customBrand === 'string' ? (
        <Link href={homeHref} className={BRAND_LINK} aria-label={customBrand} onClick={closeDrawer}>
          <span className={BRAND_NAME}>{customBrand}</span>
        </Link>
      ) : (
        customBrand
      )
    ) : (
      <Link href={homeHref} className={BRAND_LINK} aria-label={brandTitle || 'Home'} onClick={closeDrawer}>
        <span
          className={cn(
            'flex shrink-0 items-center justify-center rounded-lg bg-sidebar-primary',
            isMobile ? 'size-7' : 'size-6',
          )}
        >
          {header?.brandIcon ? (
            <LucideIcon icon={header.brandIcon} className="size-4 text-sidebar-primary-foreground md:size-4" />
          ) : (
            <span className="text-xs font-bold leading-none md:text-[11px] text-sidebar-primary-foreground">
              {brandMonogram}
            </span>
          )}
        </span>
        {brandTitle ? <span className={BRAND_NAME}>{brandTitle}</span> : null}
      </Link>
    );

  const trailing = header?.switcher ? null : (
    <PrivateSidebarTrigger className="text-sidebar-foreground/60 hover:text-sidebar-foreground" />
  );

  return (
    <div
      data-sidebar="header"
      className={cn(
        'flex shrink-0 items-center gap-2 bg-sidebar shadow-[0_1px_0_0_transparent] transition-shadow',
        bordered && 'shadow-[0_1px_0_0_color-mix(in_oklab,var(--sidebar-border)_60%,transparent)]',
        SIDEBAR_SPACING[isMobile ? 'mobile' : 'desktop'].header)}
    >
      <div className="min-w-0 flex-1">
        {header?.switcher ? <SidebarBrandSwitcher config={header.switcher} showCollapseTrigger /> : brand}
      </div>
      {/* The desktop toggle collapses the pinned sidebar. The phone drawer has none: it closes by backdrop, swipe, Escape, or navigating. */}
      {isMobile ? null : trailing}
    </div>
  );
}

export const SidebarBrand = memo(SidebarBrandRaw);
