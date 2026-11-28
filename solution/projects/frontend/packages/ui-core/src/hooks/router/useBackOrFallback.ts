'use client';

/**
 * useBackOrFallback — smart "go back" that doesn't escape the app.
 *
 * WHY:
 *   `history.back()` on the first entry of a tab takes the user out of
 *   the app (or does nothing in some browsers). For in-app Back buttons
 *   we want: go back if there's in-app history, otherwise navigate to
 *   a sensible fallback.
 *
 *   We track app-internal entries by stamping a monotonically growing
 *   serial into `history.state` on every navigation. On click we compare
 *   the current serial to the entry serial — if current > 0, there's
 *   an earlier app entry to go back to. This is bullet-proof against
 *   forward/back jitter (unlike a depth counter that can drift) and
 *   against `replace`-style navigations (they preserve the serial).
 *
 * @example
 *   const { back } = useBackOrFallback();
 *   <button onClick={() => back('/dashboard')}>Back</button>
 */

import { useCallback, useEffect, useMemo } from 'react';
import { useNavigate } from './useNavigate';
import { NAVIGATE_EVENT } from './useLocation';
import { CFG_KEYS } from '@djangocfg/api/storage';

const SERIAL_KEY = '__djcSerial';
const COUNTER_KEY = CFG_KEYS.uiRouterSerial.key;

interface SerialState {
  [SERIAL_KEY]?: number;
}

function readCounter(): number {
  if (typeof window === 'undefined') return 0;
  try {
    const raw = window.sessionStorage.getItem(COUNTER_KEY);
    if (!raw) return 0;
    const parsed = Number.parseInt(raw, 10);
    return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
  } catch {
    return 0;
  }
}

function writeCounter(value: number): void {
  if (typeof window === 'undefined') return;
  try {
    window.sessionStorage.setItem(COUNTER_KEY, String(Math.max(0, value)));
  } catch {
    // sessionStorage can throw in privacy modes — degrade silently.
  }
}

function readEntrySerial(): number {
  if (typeof window === 'undefined') return 0;
  const state = window.history.state as SerialState | null;
  return typeof state?.[SERIAL_KEY] === 'number' ? state[SERIAL_KEY] : 0;
}

function stampEntrySerial(value: number): void {
  if (typeof window === 'undefined') return;
  const current = (window.history.state ?? {}) as SerialState;
  // Don't double-stamp the same entry — `djc:navigate` can fire twice
  // if a custom adapter wraps push too.
  if (current[SERIAL_KEY] === value) return;
  try {
    window.history.replaceState(
      { ...current, [SERIAL_KEY]: value },
      '',
      window.location.href
    );
  } catch {
    // Some sandboxes disallow replaceState — skip.
  }
}

// Module-level guard: a single listener stamps every new app entry.
let serialListenerAttached = false;

function attachSerialListener(): void {
  if (serialListenerAttached) return;
  if (typeof window === 'undefined') return;
  serialListenerAttached = true;

  const onNavigate = () => {
    // If the current entry already has a serial (e.g. `replace`), keep it.
    // Otherwise stamp a fresh one and bump the counter.
    if (readEntrySerial() > 0) return;
    const next = readCounter() + 1;
    writeCounter(next);
    stampEntrySerial(next);
  };

  // Stamp the very first entry so popstate-only flows still work.
  if (readEntrySerial() === 0) {
    const next = readCounter() + 1;
    writeCounter(next);
    stampEntrySerial(next);
  }

  window.addEventListener(NAVIGATE_EVENT, onNavigate);
}

export interface UseBackOrFallbackReturn {
  /**
   * Go back if we have in-app history, otherwise navigate to `fallback`.
   * @param fallback - Where to go when there's no app history. Defaults to `/`.
   */
  back: (fallback?: string) => void;
  /** True when there's an earlier app entry to go back to. */
  canGoBack: boolean;
}

/**
 * Smart "back" that falls back to a route when the user landed
 * directly on the current page (no in-app history).
 */
export function useBackOrFallback(): UseBackOrFallbackReturn {
  const { back: adapterBack, navigate } = useNavigate();

  useEffect(() => {
    attachSerialListener();
  }, []);

  const back = useCallback(
    (fallback: string = '/') => {
      // Serial > 1 means at least one earlier app entry exists.
      if (readEntrySerial() > 1) {
        adapterBack();
      } else {
        navigate(fallback, { replace: true });
      }
    },
    [adapterBack, navigate]
  );

  // Snapshot once per render — back/forward changes the serial on the
  // entry we're sitting on, so we'll get a fresh value next render
  // anyway via React's normal re-render cycle.
  const canGoBack = readEntrySerial() > 1;

  return useMemo(() => ({ back, canGoBack }), [back, canGoBack]);
}
