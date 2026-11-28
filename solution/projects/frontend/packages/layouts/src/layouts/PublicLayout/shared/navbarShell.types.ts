import type { ReactNode } from 'react';

import type {
  PublicDesktopDropdownRenderer,
  PublicNavbarHeight,
  PublicNavbarInsetX,
  PublicNavbarPosition,
  PublicNavbarVariant,
  PublicNavLayout,
} from '../navbarTypes';
import type { NavigationItem, UserMenuConfig } from '../../types';
import type { NavAction } from '../primitives/NavActionItem';

export interface ShapeInputs {
  /** true at scrollY >= threshold */
  scrolled: boolean;
  /** Matches `transparent` flag at the source. */
  transparent: boolean;
  /**
   * true while the mobile drawer is open. A `transparent` bar MUST go opaque
   * here regardless of scroll position: an open drawer means the brand + close
   * button sit over page content, and a see-through bar leaves them floating on
   * whatever is scrolled behind — the "navbar lost its background" bug.
   */
  menuOpen: boolean;
}

export interface NavbarShellProps {
  // ── Surface identity (reported to context) ────────────────────────────────
  variant: PublicNavbarVariant;
  position: PublicNavbarPosition;

  // ── Content ───────────────────────────────────────────────────────────────
  brand?: ReactNode;
  brandHref?: string;
  navigation?: NavigationItem[];
  userMenu?: UserMenuConfig;
  renderDesktopDropdown?: PublicDesktopDropdownRenderer;
  /**
   * Hard cap for how many items to try to fit on desktop. Useful when a
   * consumer wants to force a compact primary row even if more would fit.
   * Defaults to the full list length (let the responsive measurer decide).
   */
  desktopMaxPrimaryItems?: number;

  // ── Layout ────────────────────────────────────────────────────────────────
  navLayout?: PublicNavLayout;
  navbarHeight?: PublicNavbarHeight;
  /** Horizontal inset between outer edge and the inner row.
   *  @default 'sm' */
  insetX?: PublicNavbarInsetX;
  /** Full override for the row container (escape hatch).
   *  When set, wins over `insetX`. */
  innerPadding?: string;

  // ── Scroll behavior ───────────────────────────────────────────────────────
  hideNavOnScroll?: boolean;
  transparent?: boolean;
  transparentThreshold?: number;

  // ── Chrome (per-variant) ──────────────────────────────────────────────────
  /** Classes on the outer wrapper (fixed/sticky, top offset, outer x-padding). */
  outerClassName?: string;
  /** Classes for the `<nav>` element defining the shape (rounding, border, shadow). */
  shapeClassName?: string;
  /** Surface classes (bg, backdrop-blur). Driven by `shapeForState`. */
  shapeForState?: (inputs: ShapeInputs) => string;

  /**
   * Replaces the default actions column (UserMenu + mobile-toggle).
   * Variant owns the mobile toggle too. Receives helpers so it can build the
   * right-hand side however it wants.
   */
  renderActions?: (ctx: NavbarActionsContext) => ReactNode;

  // ── Default-actions slots (only used when `renderActions` is NOT provided) ─
  /** Typed CTA pills (Book a demo / Get started / …) before UserMenu. */
  actions?: NavAction[];
  /** Arbitrary ReactNode between actions and UserMenu. */
  actionsLeadingSlot?: ReactNode;
  /** Arbitrary ReactNode after the mobile toggle. */
  actionsTrailingSlot?: ReactNode;

  // ── Theme + locale controls (rendered next to UserMenu on desktop) ────────
  /** Toggle individual controls. Locale switcher also requires `i18n`. */
  controls?: {
    /** Light / system / dark pill. @default false */
    showThemeSwitcher?: boolean;
    /** Locale dropdown. Requires `i18n`. @default false */
    showLocaleSwitcher?: boolean;
  };

  // ── Props override (used by variants that proxy ctx differently) ──────────
  mobileMenuOpen?: boolean;
  onMobileMenuToggle?: () => void;
}

export interface NavbarActionsContext {
  userMenu?: UserMenuConfig;
  mobileMenuOpen: boolean;
  toggleMobileMenu: () => void;
  toggleMobileLabel: string;
  navLayout: PublicNavLayout;
  /**
   * Pre-built theme/locale controls node. `null` when both toggles are off.
   * Variants with a custom `renderActions` can choose where to place it.
   */
  controls: ReactNode | null;
}
