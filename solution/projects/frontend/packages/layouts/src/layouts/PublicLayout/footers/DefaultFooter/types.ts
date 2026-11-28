/**
 * Default Footer types.
 */

import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

import type { FooterLink, FooterMenuSection, FooterSocialLinks } from '../../../types';

export type { FooterLink, FooterMenuSection, FooterSocialLinks };

export interface DefaultFooterConfig {
  variant?: 'full' | 'compact' | 'simple';
  shell?: {
    className?: string;
  };
  brand?: {
    /** Custom brand column (`ReactNode`) */
    slot?: ReactNode;
    description?: string;
    showColumn?: boolean;
    badge?: {
      icon: LucideIcon;
      text: string;
    };
    /**
     * Logo node displayed in the locale-switcher dialog header.
     * Falls back to a generic Globe glyph when omitted.
     */
    logo?: ReactNode;
    /**
     * Project name displayed beside the logo in the locale-switcher dialog.
     */
    name?: string;
  };
  menus?: {
    sections?: FooterMenuSection[];
    columnMinWidth?: number;
    maxColumns?: number;
  };
  links?: FooterLink[];
  meta?: {
    copyright?: string;
    credits?: {
      text: string;
      url?: string;
    };
  };
  social?: FooterSocialLinks;
  /**
   * Full (`variant: 'full'`) footer only — bottom row with theme and/or locale
   * controls. The locale switcher reads its plumbing from `LayoutI18nProvider`
   * (mounted by `BaseApp`); when the provider is empty, the switcher hides
   * itself regardless of this flag.
   */
  controls?: {
    /** Light / system / dark toggle. @default true */
    showThemeSwitcher?: boolean;
    /** @default true */
    showLocaleSwitcher?: boolean;
  };
  /**
   * Arbitrary ReactNode slots for custom content (newsletter, status badges,
   * extra CTAs …). Only rendered in the `full` variant.
   */
  slots?: {
    /** Rendered above the brand/menus grid. Full width. */
    aboveMenus?: ReactNode;
    /** Rendered between the menus grid and the bottom row. Full width. */
    belowMenus?: ReactNode;
    /** Rendered in the bottom row, next to the copyright. */
    bottomStart?: ReactNode;
    /** Rendered in the bottom row, next to controls. */
    bottomEnd?: ReactNode;
  };
}

export interface DefaultFooterProps {
  config: DefaultFooterConfig;
}
