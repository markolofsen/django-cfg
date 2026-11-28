'use client';

import { Menu, X } from 'lucide-react';
import React, { memo, type ReactNode } from 'react';

import { Button } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { UserMenu } from '../components/UserMenu';
import type { UserMenuConfig } from '../../types';

import { NavActionItem, type NavAction } from './NavActionItem';
import { shallowEqualBy } from '../../../utils/shallowEqualBy';

interface NavActionsProps {
  userMenu?: UserMenuConfig;
  mobileMenuOpen: boolean;
  onMobileMenuToggle: () => void;
  toggleMobileLabel: string;
  /** When true, mobile trigger is always visible (not hidden on lg+). Used for `split` layout. */
  forceShowMobileTrigger?: boolean;
  /** Typed CTA pills rendered before UserMenu (desktop only). */
  actions?: NavAction[];
  /** Arbitrary slot rendered between actions and UserMenu (desktop only). */
  leadingSlot?: ReactNode;
  /** Arbitrary slot rendered after the mobile toggle (desktop + mobile). */
  trailingSlot?: ReactNode;
  /**
   * Theme / locale controls rendered right before UserMenu (desktop only).
   * Built by `NavbarShell` from `config.controls` + `config.i18n`.
   */
  controlsSlot?: ReactNode;
  /**
   * Rendered immediately before the burger, on mobile only. Holds the locale
   * flag: language is a top-level choice, so it should not require opening the
   * menu to reach.
   */
  mobileLeadingSlot?: ReactNode;
}

function NavActionsRaw({
  userMenu,
  mobileMenuOpen,
  onMobileMenuToggle,
  toggleMobileLabel,
  forceShowMobileTrigger = false,
  actions,
  leadingSlot,
  trailingSlot,
  controlsSlot,
  mobileLeadingSlot,
}: NavActionsProps) {
  const hasActions = actions && actions.length > 0;

  return (
    <div className="flex items-center gap-4">
      {hasActions && (
        <div className="hidden lg:flex shrink-0 items-center gap-1.5">
          {actions!.map((a) => (
            <NavActionItem key={`${a.label}-${a.href}`} action={a} />
          ))}
        </div>
      )}

      {leadingSlot && <div className="hidden lg:flex shrink-0 items-center">{leadingSlot}</div>}

      {controlsSlot && <div className="hidden lg:flex shrink-0 items-center">{controlsSlot}</div>}

      <div className="hidden lg:flex">
        <UserMenu
          variant="desktop"
          groups={userMenu?.groups}
          authPath={userMenu?.authPath}
          i18n={userMenu?.i18n}
        />
      </div>

      {/* Flag and burger are NOT peers: the burger opens navigation, the flag is
          a rarely-touched setting. Sitting flush at equal size they read as one
          pair of identical pills, so a divider separates them and the burger is
          the larger, 44px touch target the platform guidelines ask for. */}
      <div className="flex items-center gap-1">
        {mobileLeadingSlot && (
          <>
            <div className={forceShowMobileTrigger ? 'shrink-0 flex items-center' : 'shrink-0 flex items-center lg:hidden'}>
              {mobileLeadingSlot}
            </div>
            <span
              aria-hidden
              className={cn(
                // `mx-1` on the rule itself (rather than a wider gap on the
                // row) keeps the spacing symmetrical: a plain `gap` measures
                // from the buttons' 44px boxes, which are wider than their
                // glyphs, and the divider ended up hugging the burger.
                // Full-strength border — at `/70` it vanished in light mode.
                'mx-1 h-6 w-px shrink-0 bg-border',
                forceShowMobileTrigger ? undefined : 'lg:hidden',
              )}
            />
          </>
        )}

        <Button
          variant="ghost"
          size="icon"
          aria-label={toggleMobileLabel}
          data-mobile-menu-trigger="true"
          className={cn(
            // Pill, matching every other BUTTON in the shell (CTAs, Login, the
            // page's own actions). Corner style here is per-element-kind, not
            // one global radius: buttons are pills, while nav rows and menu
            // items use `rounded-control` (`--radius-control`).
            //
            // The 44px box stays (that is the touch target); only the glyph is
            // back to the standard 20px — at 24px it read as an oversized icon
            // rather than a normal control.
            'rounded-full h-11 w-11 [&_svg]:size-5',
            !forceShowMobileTrigger && 'lg:hidden',
          )}
          onClick={onMobileMenuToggle}
        >
          {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      {trailingSlot && <div className="shrink-0 flex items-center">{trailingSlot}</div>}
    </div>
  );
}

/**
 * Shallow equality for NavAction arrays. Compares label, href, variant and
 * external flag so that CTA pills re-render when their content changes, but
 * skip on reference churn from parent re-renders.
 */
function actionsEqual(a?: NavAction[], b?: NavAction[]): boolean {
  return shallowEqualBy(
    a,
    b,
    (ai, bi) =>
      ai.label === bi.label &&
      ai.href === bi.href &&
      ai.variant === bi.variant &&
      ai.external === bi.external,
  );
}

/**
 * Memoised actions column. Re-renders when:
 * - mobile menu open state changes,
 * - actions array content changes (via actionsEqual),
 * - any slot reference changes.
 * Pure parent re-renders with identical props are skipped.
 */
export const NavActions = memo(NavActionsRaw, (prev, next) => {
  return (
    prev.mobileMenuOpen === next.mobileMenuOpen &&
    prev.onMobileMenuToggle === next.onMobileMenuToggle &&
    prev.toggleMobileLabel === next.toggleMobileLabel &&
    prev.forceShowMobileTrigger === next.forceShowMobileTrigger &&
    prev.userMenu === next.userMenu &&
    prev.leadingSlot === next.leadingSlot &&
    prev.trailingSlot === next.trailingSlot &&
    prev.controlsSlot === next.controlsSlot &&
    prev.mobileLeadingSlot === next.mobileLeadingSlot &&
    actionsEqual(prev.actions, next.actions)
  );
});
