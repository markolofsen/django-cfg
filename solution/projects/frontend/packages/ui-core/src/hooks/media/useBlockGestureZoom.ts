'use client';

import { useEffect } from 'react';

import { detectDisplayMode, isInstalledMode } from './displayMode';

/**
 * OPT-IN, off by default: blocks iOS pinch/gesture zoom while running as an installed app.
 *
 * Trade-off: it removes the only zoom some people can use (WCAG 1.4.4). The default recipe already disables
 * double-tap zoom with `touch-action: manipulation` and leaves pinch-zoom alone; use this only for an app whose UI is
 * a fixed canvas and say so in its accessibility notes. Only acts in an installed display mode, never in a browser tab.
 */
export function useBlockGestureZoom(enabled = true): void {
  useEffect(() => {
    if (!enabled || typeof document === 'undefined' || !isInstalledMode(detectDisplayMode())) return;
    const block = (event: Event) => event.preventDefault();
    // `gesturestart` is a WebKit-only event; other engines never fire it.
    document.addEventListener('gesturestart', block);
    document.addEventListener('gesturechange', block);
    return () => {
      document.removeEventListener('gesturestart', block);
      document.removeEventListener('gesturechange', block);
    };
  }, [enabled]);
}
