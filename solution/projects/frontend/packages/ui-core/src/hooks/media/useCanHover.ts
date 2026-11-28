'use client';

import { useMediaQuery } from './useMediaQuery';

/**
 * Can the primary input hover (a mouse or trackpad), as opposed to a finger or a pen-less tablet?
 *
 * Reads `(hover: hover) and (pointer: fine)` via `matchMedia`, not the userAgent, so a touch laptop with a trackpad counts, an iPad does not, and DevTools device
 * emulation updates live. SSR-safe (false until mounted). The tooltip of `Button` / `ButtonLink` is drawn only when this is true: there is nothing to hover on a phone,
 * and a hint that needs a long press is noise. Hover hints are also the ones that name a keyboard shortcut, which a phone has none of.
 */
export function useCanHover(): boolean {
  return useMediaQuery('(hover: hover) and (pointer: fine)');
}
