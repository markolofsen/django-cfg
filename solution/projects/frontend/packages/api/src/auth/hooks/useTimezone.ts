'use client';

import { useCallback, useSyncExternalStore } from 'react';

import { auth } from '../../runtime/auth';

/**
 * Time zone preference. The choice lives on the device (localStorage) and is
 * pushed into the generated auth store, which sends it as `X-Timezone` on every
 * request; Django's TimezoneMiddleware then activates it and mirrors it onto
 * the profile. `null` = automatic (follow the browser).
 */
const STORAGE_KEY = 'djangocfg.timezone';

const listeners = new Set<() => void>();

function read(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY) || null;
  } catch {
    return null;
  }
}

/** Apply the stored choice to the transport before any request goes out. */
function hydrate(): void {
  if (typeof window === 'undefined') return;
  auth.setTimezone(read());
}
hydrate();

function write(timezone: string | null): void {
  try {
    if (timezone) localStorage.setItem(STORAGE_KEY, timezone);
    else localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* storage unavailable — the choice then lasts for this page only */
  }
  auth.setTimezone(timezone);
  listeners.forEach((l) => l());
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export interface UseTimezoneReturn {
  /** Zone in effect: the explicit choice, else the browser's. `null` only where Intl cannot tell. */
  timezone: string | null;
  /** The explicit choice; `null` = automatic. Feed this to `TimezoneSelect`. */
  preference: string | null;
  isAuto: boolean;
  /** Pick a zone, or `null` for automatic. */
  setTimezone: (timezone: string | null) => void;
}

export function useTimezone(): UseTimezoneReturn {
  const preference = useSyncExternalStore(subscribe, read, () => null);
  const setTimezone = useCallback((tz: string | null) => write(tz), []);
  return {
    timezone: preference ?? auth.getTimezone(),
    preference,
    isAuto: preference === null,
    setTimezone,
  };
}
