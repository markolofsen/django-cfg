/**
 * MinimalNavbar — borderless, transparent-by-default, eesel-style.
 *
 * Differences from Floating/Flush:
 *  - no shell border/shadow, no rounded chrome
 *  - default container: max-w-[1400px], px-4 lg:px-10
 *  - right-hand side: pill CTAs + UserMenu + mobile toggle (no default UserMenu-only)
 *  - transparent at top of page by default; solid + backdrop-blur after scroll
 */

'use client';

import { Menu, X } from 'lucide-react';
import React, { type ReactNode } from 'react';

import { Button } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { UserMenu } from '../../components/UserMenu';
import { NavActionItem, type NavAction } from '../../primitives/NavActionItem';
import { NavbarShell, type NavbarActionsContext } from '../../shared';
import type {
  PublicDesktopDropdownRenderer,
  PublicNavbarHeight,
  PublicNavbarInsetX,
  PublicNavbarPosition,
  PublicNavLayout,
} from '../../navbarTypes';
import type { NavigationItem, UserMenuConfig } from '../../../types';

import { MinimalMobileDrawer } from './MinimalMobileDrawer';

export interface MinimalNavbarConfig {
  brand?: ReactNode;
  /** @default '/' */
  brandHref?: string;
  navigation?: NavigationItem[];
  userMenu?: UserMenuConfig;
  /** Right-hand CTA pills. Rendered before UserMenu / mobile toggle. */
  actions?: NavAction[];

  /** @default 'sticky' */
  navbarPosition?: PublicNavbarPosition;
  renderDesktopDropdown?: PublicDesktopDropdownRenderer;
  desktopMaxPrimaryItems?: number;
  /** @default 'default' */
  navLayout?: PublicNavLayout;
  /** @default 'md' */
  navbarHeight?: PublicNavbarHeight;
  /** Horizontal inset of the inner row. @default 'sm' */
  insetX?: PublicNavbarInsetX;
  /** @default false */
  hideNavOnScroll?: boolean;
  /**
   * Transparent at page top, opaque after `transparentThreshold`.
   * @default true
   */
  transparent?: boolean;
  /** @default 40 */
  transparentThreshold?: number;

  /**
   * Outer wrapper container classes — e.g. `mx-auto max-w-[1400px] px-4 nav:px-10`.
   * @default 'mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-10'
   */
  containerClassName?: string;
  /**
   * Optional theme + locale controls rendered next to UserMenu on desktop
   * and as a footer row in the mobile drawer. Locale switcher requires
   * `i18n`. Mirrors `DefaultFooter.controls`.
   */
  controls?: {
    /** Light / system / dark pill. @default false */
    showThemeSwitcher?: boolean;
    /** Locale dropdown. Requires `i18n`. @default false */
    showLocaleSwitcher?: boolean;
  };
}

export interface MinimalNavbarProps {
  config: MinimalNavbarConfig;
}

function MinimalActions({
  ctx,
  actions = [],
}: {
  ctx: NavbarActionsContext;
  actions?: NavAction[];
}) {
  return (
    <div className="flex shrink-0 items-center gap-4">
      {actions.length > 0 && (
        <div className="flex shrink-0 items-center gap-1.5">
          {actions.map((a) => (
            <NavActionItem key={`${a.label}-${a.href}`} action={a} />
          ))}
        </div>
      )}

      {ctx.controls && (
        <div className="hidden lg:flex shrink-0 items-center">{ctx.controls}</div>
      )}

      <div className="hidden lg:flex">
        <UserMenu
          variant="desktop"
          groups={ctx.userMenu?.groups}
          authPath={ctx.userMenu?.authPath}
        />
      </div>

      <Button
        variant="ghost"
        size="icon"
        aria-label={ctx.toggleMobileLabel}
        data-mobile-menu-trigger="true"
        className={cn(
          'rounded-full text-foreground/90 hover:bg-foreground/10',
          ctx.navLayout === 'split' ? '' : 'lg:hidden',
        )}
        onClick={ctx.toggleMobileMenu}
      >
        {ctx.mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>
    </div>
  );
}

export function MinimalNavbar({ config }: MinimalNavbarProps) {
  const navigation = config.navigation ?? [];
  const position = config.navbarPosition ?? 'sticky';
  const transparent = config.transparent ?? true;
  const containerClassName = config.containerClassName ?? 'mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-10';

  const outerClassName = cn(
    position === 'fixed' ? 'fixed' : position === 'static' ? 'static' : 'sticky',
    'top-0',
  );

  // No border, no rounding, no shadow. Full-bleed.
  const shapeClassName = 'w-full rounded-none border-0 shadow-none';

  return (
    <>
      <NavbarShell
        variant="minimal"
        position={position}
        brand={config.brand}
        brandHref={config.brandHref}
        navigation={navigation}
        userMenu={config.userMenu}
        renderDesktopDropdown={config.renderDesktopDropdown}
        desktopMaxPrimaryItems={config.desktopMaxPrimaryItems}
        navLayout={config.navLayout}
        navbarHeight={config.navbarHeight}
        insetX={config.insetX}
        hideNavOnScroll={config.hideNavOnScroll}
        transparent={transparent}
        transparentThreshold={config.transparentThreshold}
        controls={config.controls}
        outerClassName={outerClassName}
        shapeClassName={shapeClassName}
        innerPadding={containerClassName}
        shapeForState={({ scrolled, menuOpen }) =>
          cn(
            'transition-[background-color,backdrop-filter] duration-200 ease-out',
            // Transparent only at the top with the drawer closed. `menuOpen`
            // forces the surface back so an open mobile drawer never leaves the
            // bar see-through over page content.
            transparent && !scrolled && !menuOpen
              ? 'bg-transparent backdrop-blur-0'
              : 'bg-background/72 backdrop-blur-[10px] dark:bg-card/80',
          )
        }
        renderActions={(ctx) => <MinimalActions ctx={ctx} actions={config.actions} />}
      />
      <MinimalMobileDrawer
        navigation={navigation}
        userMenu={config.userMenu}
        containerClassName={containerClassName}
        controls={config.controls}
      />
    </>
  );
}
