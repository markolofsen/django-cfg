/**
 * Display mode of the page: running in a browser tab or as an installed app (PWA).
 *
 * One module-level store, so any number of components share ONE set of media-query listeners.
 * Detection covers the standard `display-mode` media query (standalone, fullscreen, minimal-ui,
 * window-controls-overlay), legacy iOS `navigator.standalone` ("Add to Home Screen" does not always
 * match the media query) and the Android TWA referrer.
 */

export type DisplayMode = 'browser' | 'standalone' | 'fullscreen' | 'minimal-ui' | 'window-controls-overlay';

const MODES = ['window-controls-overlay', 'fullscreen', 'standalone', 'minimal-ui'] as const;

/** Server and hydration value. */
export const SERVER_DISPLAY_MODE: DisplayMode = 'browser';

export function detectDisplayMode(): DisplayMode {
  if (typeof window === 'undefined') return SERVER_DISPLAY_MODE;
  if (window.matchMedia) {
    for (const mode of MODES) {
      if (window.matchMedia(`(display-mode: ${mode})`).matches) return mode;
    }
  }
  if ((window.navigator as Navigator & { standalone?: boolean }).standalone === true) return 'standalone';
  if (typeof document !== 'undefined' && document.referrer.startsWith('android-app://')) return 'standalone';
  return 'browser';
}

/** True for every mode where the browser UI is gone (installed app). */
export function isInstalledMode(mode: DisplayMode): boolean {
  return mode !== 'browser';
}

export function subscribeDisplayMode(onChange: () => void): () => void {
  if (typeof window === 'undefined' || !window.matchMedia) return () => {};
  const lists = MODES.map((m) => window.matchMedia(`(display-mode: ${m})`));
  lists.forEach((l) => l.addEventListener('change', onChange));
  return () => lists.forEach((l) => l.removeEventListener('change', onChange));
}

/** Sets `<html data-display-mode="browser|standalone|…">` so CSS can react without JS. Returns a cleanup. */
export function syncDisplayModeAttribute(): () => void {
  if (typeof document === 'undefined') return () => {};
  const apply = () => document.documentElement.setAttribute('data-display-mode', detectDisplayMode());
  apply();
  return subscribeDisplayMode(apply);
}
