/**
 * Auth Shell Types
 *
 * UI-specific configuration for auth layout shells.
 * Auth logic types live in ../types.ts (re-exported from @djangocfg/api/auth).
 */

import type { CSSProperties, ReactNode } from 'react';

// ─────────────────────────────────────────────────────────────────────────────
// Shell Variants
// ─────────────────────────────────────────────────────────────────────────────

/**
 * - `centered`  — Apple-style frameless, centered, glow background (default).
 * - `split`     — Floating two-column card: form left, sidebar right on
 *                 desktop; single-column centered on mobile.
 * - `fullsplit` — Full-bleed 50/50: edge-to-edge background image on the left
 *                 (brand + quote overlaid), form on a solid panel on the right.
 *                 Mobile collapses to a plain centered form. The large-SaaS
 *                 look (Vercel / Linear / IBM).
 */
export type AuthShellVariant = 'centered' | 'split' | 'fullsplit';

// ─────────────────────────────────────────────────────────────────────────────
// Background Configuration
// ─────────────────────────────────────────────────────────────────────────────

export interface AuthBackgroundConfig {
  /** Background image URL (loaded via useImageLoader). */
  imageUrl?: string;
  /** CSS gradient fallback when no image or image fails to load. */
  gradient?: string;
  /** Overlay color with opacity (e.g. `color-mix(in oklab, var(--background) 60%, transparent)`). */
  overlay?: string;
  /** Backdrop blur amount (e.g. `8px`). */
  blur?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Shell Props
// ─────────────────────────────────────────────────────────────────────────────

export interface AuthShellProps {
  variant: AuthShellVariant;
  children: ReactNode;
  /** Which side the media half sits on (fullsplit only). @default 'left' */
  mediaSide?: 'left' | 'right';
  /** Background configuration — image, gradient, overlay, blur. */
  background?: AuthBackgroundConfig;
  /** Slot for the right column in split variant (testimonial, branding, etc.). */
  sidebar?: ReactNode;
  /**
   * Pinned to the top of the form column, above the vertically centered form:
   * the way out and the locale (see `AuthTopBar`). Optional so a harness that
   * mounts a shell alone still renders.
   */
  topBar?: ReactNode;
  className?: string;
}

/** Internal props passed from AuthShell orchestrator to variant shells. */
export interface ShellRenderProps {
  children: ReactNode;
  /** See `AuthShellProps.topBar`. */
  topBar?: ReactNode;
  className?: string;
  bgStyle?: CSSProperties;
  overlayStyle?: CSSProperties;
  blurValue?: string;
  /** Which side the media half sits on (fullsplit only). @default 'left' */
  mediaSide?: 'left' | 'right';
  /** True once the background image has finished loading (drives fade-in). */
  bgLoaded?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Shell Context
// ─────────────────────────────────────────────────────────────────────────────

export interface AuthShellContextValue {
  variant: AuthShellVariant;
  /** True when sidebar slot is provided (split variant only). */
  hasSidebar: boolean;
}
