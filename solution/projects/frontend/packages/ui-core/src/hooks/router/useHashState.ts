'use client';

/**
 * useHashState — `useState`-style hook bound to `window.location.hash`.
 *
 * WHY A DEDICATED HOOK (and why it bypasses the router adapter):
 *   The URL fragment (`#…`) is the one part of the URL that must NOT go through
 *   the router adapter's `navigate()` / `next.push()`. Under Next.js App Router
 *   — especially with `next-intl` locale prefixing — `router.push('/path#hash')`
 *   where `/path` equals the current pathname resolves the target *relative to
 *   the current URL, including its existing hash*. Pushing `…#b` while the URL
 *   already reads `…#a` yields a doubled `…#a#b`. A `#hash` change also never
 *   needs an RSC refetch / loader / prefetch, so routing it through the
 *   framework router is both wrong (the doubling) and wasteful.
 *
 *   This hook therefore writes the hash via `history.pushState` / `replaceState`
 *   directly, always against the *absolute* URL (`pathname + search + #hash`).
 *   Reads stay reactive through `useLocationProperty` — which observes the same
 *   patched history methods (see `useLocation.ts`), so the round-trip works in
 *   every host (Next.js, Wails, Vite, plain React) with no adapter involved.
 *
 * SHAPE:
 *   The value is the fragment WITHOUT the leading `#`. `''` means "no hash".
 *   Setting `''` or `null` removes the fragment (and the trailing `#`) entirely.
 *
 * @example
 *   const [hash, setHash] = useHashState();
 *   setHash('settings/account');   // → …/private#settings/account (pushState)
 *   setHash('overview', { replace: true }); // no new history entry
 *   setHash((h) => h || 'top');    // functional updater
 *   setHash(null);                 // strip the fragment → …/private
 *
 * @example  // deep-linkable dialog section
 *   const [section, setSection] = useHashState();  // e.g. "settings/usage"
 */

import { useCallback } from 'react';

import { useLocationProperty } from './useLocation';

export interface UseHashStateOptions {
  /** Use `replaceState` instead of `pushState` for writes. Default: false. */
  replace?: boolean;
}

export type HashStateUpdater =
  | string
  | null
  | ((current: string) => string | null);

/** Strip a single leading '#'. `'#a/b'` → `'a/b'`; `''`/`'#'` → `''`. */
function stripHash(raw: string): string {
  if (!raw) return '';
  return raw.startsWith('#') ? raw.slice(1) : raw;
}

/** Current pathname + search, WITHOUT the fragment. SSR-safe. */
function baseUrl(): string {
  if (typeof window === 'undefined') return '/';
  const { pathname, search } = window.location;
  return `${pathname}${search}`;
}

/**
 * `useState`-style binding to the URL fragment. Returns `[hash, setHash]` where
 * `hash` is the fragment without its leading `#` (`''` when absent).
 *
 * Writes go straight to the History API (never the router adapter) so the hash
 * is set absolutely — see the module doc for why that matters under Next.js.
 */
export function useHashState(
  options: UseHashStateOptions = {},
): [string, (next: HashStateUpdater, opts?: UseHashStateOptions) => void] {
  const value = useLocationProperty(
    () => stripHash(window.location.hash),
    () => '',
  );

  const setValue = useCallback(
    (next: HashStateUpdater, callOpts?: UseHashStateOptions) => {
      if (typeof window === 'undefined') return;

      const current = stripHash(window.location.hash);
      const resolved =
        typeof next === 'function'
          ? (next as (current: string) => string | null)(current)
          : next;

      const nextHash = stripHash(resolved ?? '');
      if (nextHash === current) return; // no-op: don't churn history

      const url = nextHash ? `${baseUrl()}#${nextHash}` : baseUrl();
      const replace = callOpts?.replace ?? options.replace ?? false;

      // Preserve any existing history.state (Next stores routing metadata there).
      if (replace) {
        window.history.replaceState(window.history.state, '', url);
      } else {
        window.history.pushState(window.history.state, '', url);
      }
    },
    [options.replace],
  );

  return [value, setValue];
}
