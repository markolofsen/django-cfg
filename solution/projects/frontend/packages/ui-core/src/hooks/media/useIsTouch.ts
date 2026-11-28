'use client';

import { useMediaQuery } from './useMediaQuery';

/**
 * Is the primary pointer a touch (coarse) pointer?
 *
 * Reads `(pointer: coarse)` via `matchMedia` — NOT the userAgent. A media
 * query reflects real touchscreens, DevTools device emulation and updates
 * live; UA sniffing misses touch laptops, mis-detects iPadOS, and never
 * reacts to a change. SSR-safe (false until mounted).
 *
 * For "touch OR narrow viewport" (e.g. lock an embedded map to a tap-to-
 * expand affordance), compose with `useMediaQuery`:
 *
 * @example
 * const isTouch = useIsTouch()
 * const isNarrow = useMediaQuery(`(max-width: ${BREAKPOINTS.md - 1}px)`)
 * const isMobileSurface = isTouch || isNarrow
 */
export function useIsTouch(): boolean {
  return useMediaQuery('(pointer: coarse)');
}
