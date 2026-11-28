'use client';

/**
 * Semantic viewport breakpoint hooks.
 *
 * Built on top of useMediaQuery — see useMediaQuery.ts for
 * BREAKPOINTS constants and raw media query usage.
 *
 * @example
 * import { useIsPhone, useIsMobile, useIsTabletOrBelow } from '@djangocfg/ui-core/hooks'
 *
 * const isPhone         = useIsPhone()         // < 640px  (sm)
 * const isMobile        = useIsMobile()        // < 768px  (md)
 * const isTabletOrBelow = useIsTabletOrBelow() // < 1024px (lg)
 */

import { BREAKPOINTS, useMediaQuery } from './useMediaQuery';

export type { Breakpoint } from './useMediaQuery';
export { BREAKPOINTS };

/** True when viewport < 640px (Tailwind sm) — phones only. */
export function useIsPhone(): boolean {
  return useMediaQuery(`(max-width: ${BREAKPOINTS.sm - 1}px)`)
}

/** True when viewport < 768px (Tailwind md) — phones + small tablets. */
export function useIsMobile(): boolean {
  return useMediaQuery(`(max-width: ${BREAKPOINTS.md - 1}px)`)
}

/** True when viewport < 1024px (Tailwind lg) — phones + tablets. */
export function useIsTabletOrBelow(): boolean {
  return useMediaQuery(`(max-width: ${BREAKPOINTS.lg - 1}px)`)
}
