/**
 * UI Component Types
 *
 * Types for layout UI components (navigation, footer, user menu)
 */

import type { LucideIcon } from 'lucide-react';

// ============================================================================
// Navigation Types
// ============================================================================

export interface NavigationItem {
  label: string;
  href: string;
  icon?: LucideIcon | string;
  badge?: string | number;
  external?: boolean;
  /** Optional nested items for desktop dropdown navigation */
  items?: NavigationItem[];
}

export interface NavigationSection {
  title?: string;
  items: NavigationItem[];
}

// ============================================================================
// Footer Types
// ============================================================================

export interface FooterLink {
  label: string;
  path: string;
  external?: boolean;
}

export interface FooterMenuSection {
  title: string;
  items: FooterLink[];
}

export interface FooterSocialLinks {
  github?: string;
  linkedin?: string;
  twitter?: string;
  telegram?: string;
  youtube?: string;
  facebook?: string;
  instagram?: string;
  whatsapp?: string;
  email?: string;
}

export interface FooterConfig {
  siteName?: string;
  description?: string;
  logo?: string;
  badge?: {
    icon: LucideIcon;
    text: string;
  };
  socialLinks?: FooterSocialLinks;
  links?: FooterLink[];
  menuSections?: FooterMenuSection[];
  copyright?: string;
  credits?: {
    text: string;
    url?: string;
  };
  variant?: 'full' | 'simple';
}

// ============================================================================
// User Menu Types
// ============================================================================

export interface UserMenuItem {
  /** Menu item label */
  label: string;
  /** Link href (optional if onClick is provided) */
  href?: string;
  /** Icon component */
  icon?: LucideIcon;
  /** Visual variant */
  variant?: 'default' | 'destructive';
  /** Click handler (optional if href is provided) */
  onClick?: () => void;
  /** Open link in new tab */
  external?: boolean;
}

export interface UserMenuGroup {
  /** Optional group title (renders DropdownMenuLabel) */
  title?: string;
  /** Menu items in this group */
  items: UserMenuItem[];
}

/** Optional locale switching inside the user menu (submenu on desktop; avoids nested `DropdownMenu` + portal issues). */
export interface UserMenuLocaleConfig {
  locale: string;
  locales: string[];
  onLocaleChange: (locale: string) => void;
}

export interface UserMenuConfig {
  /** Menu groups for authenticated users */
  groups?: UserMenuGroup[];
  /** Auth page path (for sign in button) */
  authPath?: string;
  /** When set, language is rendered inside the user menu (not as a separate nested dropdown). */
  i18n?: UserMenuLocaleConfig;
}
