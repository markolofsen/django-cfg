/**
 * Layout Visual Hook
 *
 * Computes CSS variables and class names for the boxed/full-bleed layout variants.
 */

import { useMemo } from 'react';

import type { LayoutVisualConfig } from '../../types';

/** CSS variables consumed by the boxed `SidebarInset` (margin + radius). */
export function resolveProviderStyle(
  visual: LayoutVisualConfig | undefined,
): React.CSSProperties | undefined {
  if ((visual?.variant ?? 'full-bleed') !== 'boxed') return undefined;
  const inset = normaliseInset(visual?.inset);
  return {
    ['--app-shell-inset-x' as string]: `${inset.x}px`,
    ['--app-shell-inset-y' as string]: `${inset.y}px`,
    ['--app-shell-radius' as string]: BOXED_RADIUS_REM[visual?.radius ?? '2xl'],
  };
}

/**
 * Statically-known Tailwind classes for the boxed inset. Margin and radius are
 * driven by the CSS variables set in `resolveProviderStyle`, so JIT can fully
 * extract these classes at build time.
 */
const BOXED_INSET_CLASS = [
  'flex min-h-0 min-w-0 flex-col',
  'md:peer-data-[variant=inset]:my-[var(--app-shell-inset-y)]',
  'md:peer-data-[variant=inset]:mr-[var(--app-shell-inset-x)]',
  'md:peer-data-[variant=inset]:rounded-[var(--app-shell-radius)]',
  'md:peer-data-[variant=inset]:overflow-hidden',
].join(' ');

const BOXED_INSET_BORDER_CLASS =
  'md:peer-data-[variant=inset]:border md:peer-data-[variant=inset]:border-border/60';

const BOXED_RADIUS_REM: Record<NonNullable<LayoutVisualConfig['radius']>, string> = {
  sm: '0.375rem',
  md: '0.5rem',
  lg: '0.75rem',
  xl: '1rem',
  '2xl': '1.25rem',
  '3xl': '1.75rem',
};

export function resolveInsetClassName(visual: LayoutVisualConfig | undefined): string {
  if ((visual?.variant ?? 'full-bleed') !== 'boxed') return 'flex min-h-0 min-w-0 flex-col';
  const border = visual?.border ?? true;
  return border ? `${BOXED_INSET_CLASS} ${BOXED_INSET_BORDER_CLASS}` : BOXED_INSET_CLASS;
}

/**
 * Background painted *behind* the boxed container on md+. On mobile the
 * canvas tint is dropped because the sidebar is a Drawer — leaking the
 * canvas colour to the whole viewport just makes the page look dim.
 *
 * `bg-sidebar` (the default) overrides shadcn-sidebar's built-in
 * `has-[&_[data-variant=inset]]:bg-sidebar` only at the breakpoint where
 * the inset shape actually exists.
 */
const BOXED_BG_CLASS: Record<NonNullable<LayoutVisualConfig['background']>, string> = {
  sidebar: 'md:!bg-sidebar',
  muted: 'md:!bg-muted',
  card: 'md:!bg-card',
  background: 'md:!bg-background',
};

export function resolveProviderClassName(
  visual: LayoutVisualConfig | undefined,
): string | undefined {
  // h-[var(--app-height)] + overflow-hidden: lock the shell to exactly one viewport height so
  // the inner scroll-area (PrivateContent) is the only scroll surface. Without
  // this, SidebarProvider grows via min-h-svh and the whole page scrolls.
  const base = 'h-[var(--app-height,100svh)] overflow-hidden';
  if ((visual?.variant ?? 'full-bleed') !== 'boxed') return base;
  // `max-md:!bg-background` neutralises shadcn-sidebar's built-in
  // `has-[[data-variant=inset]]:bg-sidebar` below md so the mobile Drawer shell
  // doesn't paint the whole viewport with the canvas tint.
  return `${base} max-md:!bg-background ${BOXED_BG_CLASS[visual?.background ?? 'sidebar']}`;
}

function normaliseInset(inset: LayoutVisualConfig['inset']): { x: number; y: number } {
  if (typeof inset === 'number') return { x: inset, y: inset };
  return { x: inset?.x ?? 12, y: inset?.y ?? 12 };
}

export interface LayoutVisualResult {
  /** CSS variables for the provider */
  providerStyle: React.CSSProperties | undefined;
  /** Class name for the provider */
  providerClassName: string | undefined;
  /** Class name for the inset */
  insetClassName: string;
  /** Sidebar variant for shadcn */
  sidebarVariant: 'sidebar' | 'inset';
}

export function useLayoutVisual(visual: LayoutVisualConfig | undefined): LayoutVisualResult {
  return useMemo(() => {
    const variant = visual?.variant ?? 'full-bleed';
    const sidebarVariant = variant === 'boxed' ? 'inset' : 'sidebar';

    return {
      providerStyle: resolveProviderStyle(visual),
      providerClassName: resolveProviderClassName(visual),
      insetClassName: resolveInsetClassName(visual),
      sidebarVariant,
    };
  }, [visual]);
}
