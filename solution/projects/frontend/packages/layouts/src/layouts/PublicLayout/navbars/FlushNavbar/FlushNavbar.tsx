/**
 * FlushNavbar — edge-to-edge bar with a subtle bottom border.
 *
 * Pairs with FlushMobileDrawer (no rounding/shadow).
 */

'use client';

import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { NavAction } from '../../primitives/NavActionItem';
import { NavbarShell } from '../../shared';
import type {
  PublicDesktopDropdownRenderer,
  PublicNavbarHeight,
  PublicNavbarInsetX,
  PublicNavbarPosition,
  PublicNavbarShellConfig,
  PublicNavLayout,
} from '../../navbarTypes';
import type { NavigationItem, UserMenuConfig } from '../../../types';

import { FlushMobileDrawer } from './FlushMobileDrawer';

export interface FlushNavbarConfig {
  shell?: PublicNavbarShellConfig;
  brand?: React.ReactNode;
  /** @default '/' */
  brandHref?: string;
  navigation?: NavigationItem[];
  userMenu?: UserMenuConfig;
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
  /** @default false */
  transparent?: boolean;
  /** @default 40 */
  transparentThreshold?: number;
  /** Typed CTA pills (Book a demo / Get started / …) before UserMenu. */
  actions?: NavAction[];
  /** Arbitrary ReactNode between actions and UserMenu. */
  actionsLeadingSlot?: React.ReactNode;
  /** Arbitrary ReactNode after the mobile toggle. */
  actionsTrailingSlot?: React.ReactNode;
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

export interface FlushNavbarProps {
  config: FlushNavbarConfig;
}

export function FlushNavbar({ config }: FlushNavbarProps) {
  const navigation = config.navigation ?? [];
  const containerClassName = config.shell?.className;
  const position = config.navbarPosition ?? 'sticky';

  const outerClassName = cn(
    position === 'fixed' ? 'fixed' : position === 'static' ? 'static' : 'sticky',
    'top-0',
  );

  const shapeClassName = cn(
    'mx-auto w-full',
    'rounded-none border-x-0 border-t-0 border-b border-border/40 dark:border-border/70 shadow-none',
    containerClassName,
  );

  return (
    <>
      <NavbarShell
        variant="flush"
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
        transparent={config.transparent}
        transparentThreshold={config.transparentThreshold}
        actions={config.actions}
        actionsLeadingSlot={config.actionsLeadingSlot}
        actionsTrailingSlot={config.actionsTrailingSlot}
        controls={config.controls}
        outerClassName={outerClassName}
        shapeClassName={shapeClassName}
        shapeForState={({ scrolled, transparent, menuOpen }) =>
          cn(
            transparent && 'transition-[background-color,backdrop-filter] duration-200 ease-out',
            // Opaque unless we're a transparent bar sitting at the top with the
            // mobile drawer closed. `menuOpen` forces the surface back so an
            // open drawer never leaves the bar see-through over page content.
            !transparent || scrolled || menuOpen
              ? 'bg-background/72 backdrop-blur-[10px] dark:bg-card/80'
              : 'bg-transparent backdrop-blur-0 dark:bg-transparent',
          )
        }
      />
      <FlushMobileDrawer
        navigation={navigation}
        userMenu={config.userMenu}
        containerClassName={containerClassName}
        controls={config.controls}
      />
    </>
  );
}
