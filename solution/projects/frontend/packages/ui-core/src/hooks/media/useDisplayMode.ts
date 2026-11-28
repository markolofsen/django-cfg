'use client';

import { useSyncExternalStore } from 'react';

import {
  detectDisplayMode,
  isInstalledMode,
  SERVER_DISPLAY_MODE,
  subscribeDisplayMode,
  type DisplayMode,
} from './displayMode';

/**
 * Current display mode. The server and the hydration render report `'browser'`, the real value
 * arrives right after (same contract as `useMediaQuery`); let CSS decide where a flash matters:
 * `:root[data-display-mode='standalone'] { ... }`.
 */
export function useDisplayMode(): DisplayMode {
  return useSyncExternalStore(subscribeDisplayMode, detectDisplayMode, () => SERVER_DISPLAY_MODE);
}

/** True when the app runs installed (PWA: standalone, fullscreen, minimal-ui, window-controls-overlay). */
export function useIsPwa(): boolean {
  return isInstalledMode(useDisplayMode());
}
