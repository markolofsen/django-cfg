'use client'

import { useIsTouch, useMediaQuery, MEDIA_BREAKPOINTS } from '@djangocfg/ui-core/hooks'

/**
 * Should the map behave as a "mobile / touch" surface?
 *
 * True when the primary pointer is coarse (a finger) OR the viewport is
 * narrow. Both signals come from ui-core's `matchMedia`-based hooks, NOT
 * the userAgent — so this reflects real touchscreens, DevTools device
 * emulation, narrow windows and tablets, and updates live. (UA sniffing
 * misses touch laptops, mis-detects iPadOS, and won't react to a resize.)
 *
 * @param breakpoint width (px) at/under which the map is treated as mobile
 *   even with a fine pointer. Default 768 (Tailwind `md`).
 */
export function useMapTouchMode(breakpoint: number = MEDIA_BREAKPOINTS.md): boolean {
  const isTouch = useIsTouch()
  const isNarrow = useMediaQuery(`(max-width: ${breakpoint - 1}px)`)
  return isTouch || isNarrow
}
