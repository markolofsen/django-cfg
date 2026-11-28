'use client';

import { cn } from '@djangocfg/ui-core/lib';

import type { PublicNavbarHeight, PublicNavbarInsetX } from '../navbarTypes';

/**
 * Vertical padding, per breakpoint. Two independent scales rather than one with
 * `sm:` steps inside it: the mobile row's tallest element is the 44px burger,
 * so padding there is pure added height, while the desktop row needs the extra
 * air to keep the link list off the panel edge.
 */
export const heightClsDesktop: Record<PublicNavbarHeight, string> = {
  sm: 'py-2',
  md: 'py-3.5',
  lg: 'py-5',
};

export const heightClsMobile: Record<PublicNavbarHeight, string> = {
  sm: 'py-1.5',
  md: 'py-2',
  lg: 'py-3',
};

/**
 * Token → Tailwind class for the inner-row horizontal padding.
 *
 * Deliberately ASYMMETRIC at every breakpoint (`pl` > `pr`) to correct an
 * optical imbalance, not a measured one. On the left the gutter meets the
 * brand's glyphs directly; on the right it meets a button — an icon square on
 * phones, the Login pill on desktop — whose box carries its own internal
 * padding around the glyph. Equal `px` therefore *looks* lopsided, with a
 * conspicuous moat to the right of the last control.
 *
 * It also stacks with the navbar shell's own outer gutter (`px-3 sm:px-4
 * lg:px-6`), which is why the right side stays small in absolute terms: at
 * `lg` the symmetric version put ~48px between the Login button and the
 * viewport edge.
 */
/** Desktop (`lg`+) horizontal inset. Right stays trimmed — see the note above. */
export const insetXClsDesktop: Record<'none' | 'xs' | 'sm' | 'md' | 'lg', string> = {
  none: '',
  xs: 'lg:pl-4 lg:pr-1.5',
  sm: 'lg:pl-6 lg:pr-2',
  md: 'lg:pl-8 lg:pr-3',
  lg: 'lg:pl-12 lg:pr-5',
};

/** Mobile horizontal inset — tighter, and asymmetric for the same reason. */
export const insetXClsMobile: Record<'none' | 'xs' | 'sm' | 'md' | 'lg', string> = {
  none: '',
  xs: 'pl-3 pr-1',
  sm: 'pl-4 pr-1.5',
  md: 'pl-5 pr-2',
  lg: 'pl-6 pr-3',
};

/**
 * Resolves the inset token into one class string covering both breakpoints.
 *
 * A caller may also pass raw Tailwind instead of a token; that escape hatch is
 * applied verbatim to both rows, since we cannot know how to split it.
 */
export function resolveInsetX(value: PublicNavbarInsetX | undefined): string {
  const token = (value ?? 'sm') as keyof typeof insetXClsMobile;
  if (!(token in insetXClsMobile)) return value as string;
  return cn(insetXClsMobile[token], insetXClsDesktop[token]);
}

