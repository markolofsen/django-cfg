import { useEffect } from 'react';
import type { Decorator, Preview } from '@storybook/nextjs-vite';

import { syncDisplayModeAttribute } from '@djangocfg/ui-core/hooks';

/**
 * "Installed app" emulation for DESKTOP review. Storybook cannot change the real `display-mode` or
 * `env(safe-area-inset-*)`, so two toolbar globals fake what the PWA code reads:
 *
 *  - `displayMode`: `auto` (default, real: nothing is touched), `browser` or `standalone` (emulated). An emulated
 *    value wraps `window.matchMedia` so `(display-mode: ...)` answers it and fires `change`, and sets
 *    `<html data-display-mode>` (what `UiProviders` sets in a real app).
 *  - `safeArea` (none | iphone | iphone-se): sets `--app-safe-*` on `<html>`; the `--safe-*` tokens in ui-core
 *    `base.css` read them before falling back to `env(...)`. A status bar / island / home-indicator overlay is drawn.
 *
 * On a REAL touch device (coarse pointer + touch points + phone-sized screen) all emulation is ignored, whatever
 * the toolbar or a deep link says: real `env()` and the real display mode apply, so the page can be added to the
 * home screen and reviewed as it truly behaves. `?sb-emulate=1` opts in anyway.
 * Deep link (desktop): `?globals=displayMode:standalone;safeArea:iphone`.
 *
 * `device` is the one-switch shortcut for ALL stories (toolbar "Device", or `?sb-device=off|browser|pwa|auto`):
 * `pwa` = standalone + iPhone insets and island, `browser` = browser display mode without insets, `auto` = real,
 * `off` (default) = nothing forced, the story's own globals decide. Pair with the Viewport toolbar for phone width.
 */

type SafeArea = 'none' | 'iphone' | 'iphone-se';

const SAFE_AREAS: Record<SafeArea, { top: number; right: number; bottom: number; left: number; island: boolean }> = {
  none: { top: 0, right: 0, bottom: 0, left: 0, island: false },
  iphone: { top: 59, right: 0, bottom: 34, left: 0, island: true },
  'iphone-se': { top: 20, right: 0, bottom: 0, left: 0, island: false },
};

export type Device = 'off' | 'browser' | 'pwa' | 'auto';

/** One switch for every story: what the Display mode and Safe area items would otherwise be set to. */
export const deviceGlobalType: NonNullable<Preview['globalTypes']>[string] = {
  description: 'Device emulation for all stories',
  toolbar: {
    title: 'Device',
    icon: 'mobile',
    dynamicTitle: true,
    items: [
      { value: 'off', title: 'Off (story / Display mode + Safe area items decide)' },
      { value: 'browser', title: 'Browser phone (display-mode browser, no insets)' },
      { value: 'pwa', title: 'PWA phone (standalone + iPhone island 59/34)' },
      { value: 'auto', title: 'Auto (real: nothing emulated)' },
    ],
  },
};

/**
 * Effective display mode and safe area. `device` (toolbar, or `?sb-device=off|browser|pwa|auto` in the URL, which
 * wins) overrides the two finer items; `off` leaves them to the story's own globals. Pure, for tests.
 */
export function resolveDevice(
  device: string | undefined,
  urlDevice: string | null,
  displayMode: string | undefined,
  safeArea: string | undefined,
): { displayMode: string | undefined; safeArea: string | undefined } {
  const pick = urlDevice ?? device;
  if (pick === 'browser') return { displayMode: 'browser', safeArea: 'none' };
  if (pick === 'pwa') return { displayMode: 'standalone', safeArea: 'iphone' };
  if (pick === 'auto') return { displayMode: 'auto', safeArea: 'none' };
  return { displayMode, safeArea };
}

export const displayModeGlobalType: NonNullable<Preview['globalTypes']>[string] = {
  description: 'Display mode',
  toolbar: {
    title: 'Display mode',
    icon: 'mobile',
    dynamicTitle: true,
    items: [
      { value: 'auto', title: 'Auto (real)' },
      { value: 'browser', title: 'Browser tab (emulated)' },
      { value: 'standalone', title: 'Installed app (emulated)' },
    ],
  },
};

export const safeAreaGlobalType: NonNullable<Preview['globalTypes']>[string] = {
  description: 'Safe area',
  toolbar: {
    title: 'Safe area',
    icon: 'grid',
    dynamicTitle: true,
    items: [
      { value: 'none', title: 'No safe area' },
      { value: 'iphone', title: 'iPhone (island, top 59 / bottom 34)' },
      { value: 'iphone-se', title: 'iPhone SE (status bar 20)' },
    ],
  },
};

// ─── real-device guard ──────────────────────────────────────────────────────

/** True on a real phone/tablet: emulation is pointless there and would paint over the real browser chrome. */
export function isRealTouchDevice(): boolean {
  if (typeof window === 'undefined' || !window.matchMedia) return false;
  if (new URLSearchParams(window.location.search).get('sb-emulate') === '1') return false;
  const original = (window as W).__sbDisplayMode?.original ?? window.matchMedia.bind(window);
  const coarse = original('(pointer: coarse)').matches;
  const small = Math.min(window.screen.width, window.screen.height) < 820;
  return coarse && small && (navigator.maxTouchPoints ?? 0) > 0;
}

/** The emulated mode to apply, or null for "real" (auto, or a real device). Pure, for tests. */
export function resolveEmulatedMode(global: string | undefined, realDevice: boolean): 'browser' | 'standalone' | null {
  if (realDevice) return null;
  return global === 'browser' || global === 'standalone' ? global : null;
}

// ─── matchMedia wrapper ─────────────────────────────────────────────────────

type W = Window & { __sbDisplayMode?: { mode: string | null; listeners: Set<() => void>; original: typeof window.matchMedia } };

function installMatchMediaPatch(): NonNullable<W['__sbDisplayMode']> {
  const w = window as W;
  if (w.__sbDisplayMode) return w.__sbDisplayMode;
  const state = { mode: null as string | null, listeners: new Set<() => void>(), original: window.matchMedia.bind(window) };
  w.__sbDisplayMode = state;
  window.matchMedia = ((query: string) => {
    const m = /^\(display-mode:\s*([\w-]+)\)$/.exec(query.trim());
    if (!m || state.mode === null) return state.original(query);
    const real = state.original(query);
    const fake = {
      media: query,
      onchange: null,
      get matches() {
        return state.mode === m[1];
      },
      addEventListener: (_: string, l: () => void) => void state.listeners.add(l),
      removeEventListener: (_: string, l: () => void) => void state.listeners.delete(l),
      addListener: (l: () => void) => void state.listeners.add(l),
      removeListener: (l: () => void) => void state.listeners.delete(l),
      dispatchEvent: () => false,
    };
    return Object.assign(Object.create(real), fake) as MediaQueryList;
  }) as typeof window.matchMedia;
  return state;
}

// ─── decorator ──────────────────────────────────────────────────────────────

export const withDisplayMode: Decorator = (Story, context) => {
  const real = isRealTouchDevice();
  const urlDevice = typeof window === 'undefined' ? null : new URLSearchParams(window.location.search).get('sb-device');
  const eff = resolveDevice(
    context.globals.device as string | undefined,
    urlDevice,
    context.globals.displayMode as string | undefined,
    context.globals.safeArea as string | undefined,
  );
  const mode = resolveEmulatedMode(eff.displayMode, real);
  const area = real ? 'none' : ((eff.safeArea as SafeArea | undefined) ?? 'none');
  const insets = SAFE_AREAS[area] ?? SAFE_AREAS.none;

  // Install before children read it (first render), then notify subscribers on change.
  if (typeof window !== 'undefined') installMatchMediaPatch().mode = mode;

  useEffect(() => {
    const state = installMatchMediaPatch();
    state.mode = mode;
    state.listeners.forEach((l) => l());
    if (mode) {
      document.documentElement.setAttribute('data-display-mode', mode);
      return;
    }
    // Real: let the shared helper report the true mode (UiProviders does this in a real app).
    return syncDisplayModeAttribute();
  }, [mode]);

  useEffect(() => {
    const root = document.documentElement;
    const names = ['top', 'right', 'bottom', 'left'] as const;
    names.forEach((n) => {
      if (insets[n] > 0) root.style.setProperty(`--app-safe-${n}`, `${insets[n]}px`);
      else root.style.removeProperty(`--app-safe-${n}`);
    });
    return () => names.forEach((n) => root.style.removeProperty(`--app-safe-${n}`));
  }, [insets]);

  return (
    <>
      <Story />
      {insets.top > 0 && (
        <div
          aria-hidden
          className="pointer-events-none fixed inset-x-0 top-0 flex items-start justify-center"
          style={{ height: insets.top, zIndex: 2147483000, background: 'rgba(0,0,0,0.35)' }}
        >
          {insets.island && <div style={{ marginTop: 11, width: 120, height: 34, borderRadius: 17, background: '#000' }} />}
        </div>
      )}
      {insets.bottom > 0 && (
        <div
          aria-hidden
          className="pointer-events-none fixed inset-x-0 bottom-0 flex items-end justify-center"
          style={{ height: insets.bottom, zIndex: 2147483000, background: 'rgba(0,0,0,0.25)' }}
        >
          <div style={{ marginBottom: 8, width: 134, height: 5, borderRadius: 3, background: 'rgba(255,255,255,0.8)' }} />
        </div>
      )}
    </>
  );
};
