/**
 * The navbar has TWO layouts, not one responsive layout.
 *
 * They are separate components on purpose. Previously a single row carried both
 * behaviours and toggled parts with `lg:hidden` / `hidden lg:flex`, which meant
 * every shared token — horizontal inset, row height, control size, corner
 * radius — had to encode both breakpoints at once. Tuning the phone spacing
 * risked the desktop bar and vice versa; the two designs were entangled in
 * values that looked unrelated to either.
 *
 * Splitting them costs one thing worth stating plainly: both rows are rendered
 * and one is hidden with CSS. That keeps rendering purely CSS-driven — no
 * `useMediaQuery`, no layout shift on hydration, correct SSR output — at the
 * price of the hidden row's markup existing in the DOM. For a navbar (a handful
 * of links) that trade is right; it would not be for a heavy subtree.
 *
 * Config stays SINGLE — callers pass one `navigation`, one `brand`, one
 * `userMenu`. Only the arrangement differs, so the two cannot drift apart.
 */

'use client';

import React, { type ReactNode } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { PublicNavLayout } from '../navbarTypes';

export interface NavbarRowProps {
  brand: ReactNode;
  actions: ReactNode;
  /** Desktop-only: the horizontal link list. */
  desktopNav?: ReactNode;
  navLayout: PublicNavLayout;
  /** Vertical padding classes for this breakpoint. */
  heightClassName: string;
}

/**
 * Desktop row (`lg` and up). Brand, the link list, then actions.
 *
 * `navLayout` only affects where the links sit, so it is read here and nowhere
 * else — the mobile row has no link list to arrange.
 */
export function NavbarRowDesktop({
  brand,
  actions,
  desktopNav,
  navLayout,
  heightClassName,
}: NavbarRowProps) {
  // `split` deliberately renders no link list — the caller wants brand and
  // actions only, with navigation living in the drawer at every width.
  const navAlignment =
    navLayout === 'brand-left'
      ? 'justify-start'
      : 'justify-center';

  return (
    <div className={cn('hidden lg:flex items-center gap-6', heightClassName)}>
      <div className="min-w-0 shrink-0 flex items-center">{brand}</div>

      {navLayout !== 'split' && (
        // `isolate` keeps the dropdown popovers' stacking contained to the nav
        // list instead of competing with the actions column.
        <div className={cn('isolate flex min-w-0 flex-1 items-center gap-1', navAlignment)}>
          {desktopNav}
        </div>
      )}

      {navLayout === 'split' && <div className="flex-1" />}

      <div className="flex shrink-0 items-center gap-3">{actions}</div>
    </div>
  );
}

/**
 * Mobile row (below `lg`). Brand on the left, controls hard right — there is no
 * link list, so it never needs the alignment logic above.
 */
export function NavbarRowMobile({
  brand,
  actions,
  heightClassName,
}: Omit<NavbarRowProps, 'desktopNav' | 'navLayout'>) {
  return (
    <div className={cn('flex lg:hidden items-center justify-between gap-3', heightClassName)}>
      <div className="min-w-0 flex items-center">{brand}</div>
      <div className="flex shrink-0 items-center">{actions}</div>
    </div>
  );
}
