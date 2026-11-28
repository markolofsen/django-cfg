/**
 * FloatingNavbar — rounded, inset shell with soft shadow.
 *
 * Pairs with FloatingMobileDrawer (matching rounding + shadow).
 */

'use client';

import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { publicFloatingChromeClassName } from '../../publicShellShadow';
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

import { FloatingMobileDrawer } from './FloatingMobileDrawer';

export interface FloatingNavbarConfig {
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

export interface FloatingNavbarProps {
  config: FloatingNavbarConfig;
}

export function FloatingNavbar({ config }: FloatingNavbarProps) {
  const navigation = config.navigation ?? [];
  const rounding = config.shell?.rounding;
  const containerClassName = config.shell?.className;
  const position = config.navbarPosition ?? 'sticky';

  const outerClassName = cn(
    position === 'fixed' ? 'fixed' : position === 'static' ? 'static' : 'sticky',
    'top-3 px-3 sm:px-4 lg:px-6',
  );

  const shapeClassName = cn(
    'mx-auto w-full',
    rounding ?? 'rounded-2xl',
    publicFloatingChromeClassName,
    containerClassName,
  );

  return (
    <>
      <NavbarShell
        variant="floating"
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
      <FloatingMobileDrawer
        navigation={navigation}
        userMenu={config.userMenu}
        containerClassName={containerClassName}
        rounding={rounding}
        controls={config.controls}
      />
    </>
  );
}
