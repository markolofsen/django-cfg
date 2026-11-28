/**
 * Shared navbar types — consumed by all navbar variants and PublicLayout main offset.
 */

import type { ReactNode } from 'react';

import type { NavigationItem } from '../types';

/**
 * Navbar chrome variant used for main-content top spacing.
 * - `floating` — rounded, inset shell (extra top offset for main).
 * - `flush`    — edge-to-edge bar with bottom border.
 * - `minimal`  — no shell at all (eesel-style): transparent, borderless.
 */
export type PublicNavbarVariant = 'floating' | 'flush' | 'minimal';

export type PublicNavbarPosition = 'sticky' | 'fixed' | 'static';

/**
 * Desktop nav layout variant.
 * - `default`     — brand left | nav **centered** (absolute) | actions right
 * - `brand-left`  — brand left | nav immediately after brand | actions pushed right
 * - `centered`    — brand + nav + actions all centered in one row
 * - `split`       — brand left | actions right | no desktop nav (drawer only)
 */
export type PublicNavLayout = 'default' | 'brand-left' | 'centered' | 'split';

/**
 * Navbar vertical padding / height.
 * - `sm` → py-2
 * - `md` → py-3.5  (default)
 * - `lg` → py-5
 */
export type PublicNavbarHeight = 'sm' | 'md' | 'lg';

/**
 * Horizontal inset between the navbar's outer edge and its inner row
 * (brand + nav + actions). Tuned per breakpoint so wide screens get a
 * bit more breathing room than mobile.
 *
 * - `none` → no padding (edge-to-edge, e.g. embedded app shells)
 * - `xs`   → `px-2 sm:px-3 lg:px-4`
 * - `sm`   → `px-3 sm:px-4 lg:px-6`  (default — symmetric, compact)
 * - `md`   → `px-4 sm:px-6 lg:px-8`
 * - `lg`   → `px-6 sm:px-8 lg:px-12`
 *
 * Pass a string instead to use any Tailwind class (escape hatch).
 */
export type PublicNavbarInsetX = 'none' | 'xs' | 'sm' | 'md' | 'lg' | (string & {});

export interface PublicNavbarSurface {
  variant: PublicNavbarVariant;
  position: PublicNavbarPosition;
}

/** Outer shell (rounding, centering). Used by `floating` / `flush` navbars. */
export interface PublicNavbarShellConfig {
  /** Tailwind rounding class (e.g. `rounded-3xl`). */
  rounding?: string;
  /** Strip + drawer wrapper (e.g. `mx-auto max-w-7xl`). */
  className?: string;
}

// ─── Desktop dropdown renderer ───────────────────────────────────────────────

export interface PublicDesktopDropdownRenderProps {
  item: NavigationItem;
  isOpen: boolean;
  isActive: boolean;
  close: () => void;
  defaultPopover: ReactNode;
  defaultItems: ReactNode;
}

export type PublicDesktopDropdownRenderer = (props: PublicDesktopDropdownRenderProps) => ReactNode;
