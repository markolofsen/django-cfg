'use client';

/**
 * useQueryState — typed `useState`-style hook backed by ONE URL query key.
 *
 * WHY:
 *   `useQueryParams().get('page')` works, but you re-coerce to number
 *   in every component. `useQueryState('page', parseAsInteger.withDefault(1))`
 *   gives you `[number, setter]` directly, like `useState`. Setting to
 *   the parser's default value clears the key from the URL (no `?page=1`
 *   noise) — toggle off via `clearOnDefault: false`.
 *
 *   Inspired by nuqs (47ng/nuqs) but framework-agnostic via our adapter.
 *
 * @example
 *   const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
 *   const [tab, setTab]   = useQueryState('tab',  parseAsStringEnum(['a','b']).withDefault('a'));
 *   setPage((p) => p + 1);   // functional updater
 *   setPage(null);           // clear the key
 */

import { useCallback, useMemo } from 'react';
import { useRouterAdapter } from './adapter';
import { useLocation } from './useLocation';
import { useNavigate } from './useNavigate';
import type { QueryParser } from './parsers';

export interface UseQueryStateOptions {
  /** Use `replaceState` instead of `pushState`. Default: false. */
  replace?: boolean;
  /** Scroll to top after navigation. Default: false. */
  scroll?: boolean;
  /**
   * Show the top loading bar. Default: false: a query change is not a page
   * transition. Pass `true` when the change loads a heavy server view.
   */
  progress?: boolean;
  /**
   * Write the URL without a navigation: no request to the server, no server
   * components re-rendered, no bar, no scroll (`scroll` and `progress` are ignored).
   * For state only the client needs (a view mode, a zoom, a slider). Default:
   * false. Precedence: the setter call, then the hook, then false.
   */
  shallow?: boolean;
  /**
   * When the new value equals the parser's default, drop the key from
   * the URL instead of writing `?page=1`. Default: true (recommended —
   * keeps URLs clean). Set false if your URLs are linked / bookmarked
   * and you need explicit values.
   */
  clearOnDefault?: boolean;
}

export type QueryStateUpdater<T> = T | null | ((current: T) => T | null);

// Two overloads so the return type narrows on `defaultValue`.
export function useQueryState<T>(
  key: string,
  parser: QueryParser<T> & { defaultValue: T },
  options?: UseQueryStateOptions
): [T, (next: QueryStateUpdater<T>, opts?: UseQueryStateOptions) => void];

export function useQueryState<T>(
  key: string,
  parser: QueryParser<T>,
  options?: UseQueryStateOptions
): [T | null, (next: QueryStateUpdater<T>, opts?: UseQueryStateOptions) => void];

export function useQueryState<T>(
  key: string,
  parser: QueryParser<T>,
  options?: UseQueryStateOptions
): [T | null, (next: QueryStateUpdater<T>, opts?: UseQueryStateOptions) => void] {
  const { pathname, search } = useLocation();
  const { navigate, shallow } = useNavigate();
  const adapter = useRouterAdapter();

  const parse = useCallback(
    (qs: string): T | null => {
      const raw = new URLSearchParams(qs).get(key);
      if (raw === null) return parser.defaultValue ?? null;
      const parsed = parser.parse(raw);
      return parsed === null ? (parser.defaultValue ?? null) : parsed;
    },
    [key, parser]
  );

  const value = useMemo<T | null>(() => parse(search), [search, parse]);

  const setValue = useCallback(
    (next: QueryStateUpdater<T>, callOpts?: UseQueryStateOptions) => {
      // Read the URL as it is now, not as this render saw it: two calls in one tick
      // (or one before the re-render) must both land. The rendered `search` is the fallback on the server.
      const live = typeof window === 'undefined' ? null : adapter.getLocation();
      const currentSearch = live ? live.search : search;
      const currentPathname = live ? live.pathname : pathname;
      const current = live ? parse(currentSearch) : value;

      const resolved =
        typeof next === 'function'
          ? (next as (current: T) => T | null)(
              (current ?? parser.defaultValue) as T
            )
          : next;

      const params = new URLSearchParams(currentSearch);
      const clearOnDefault =
        callOpts?.clearOnDefault ?? options?.clearOnDefault ?? true;

      if (
        resolved === null ||
        (clearOnDefault &&
          parser.defaultValue !== undefined &&
          parser.eq(resolved as T, parser.defaultValue))
      ) {
        params.delete(key);
      } else {
        params.set(key, parser.serialize(resolved as T));
      }

      const qs = params.toString();
      const href = qs ? `${currentPathname}?${qs}` : currentPathname;
      const replace = callOpts?.replace ?? options?.replace ?? false;
      if (callOpts?.shallow ?? options?.shallow ?? false) {
        // The hash goes with the entry, as `pushState` of a bare path would drop it.
        shallow(live?.hash ? `${href}${live.hash}` : href, { replace });
        return;
      }
      navigate(href, {
        replace,
        scroll: callOpts?.scroll ?? options?.scroll ?? false,
        progress: callOpts?.progress ?? options?.progress ?? false,
      });
    },
    [adapter, pathname, search, key, parser, parse, navigate, shallow, options, value]
  );

  return [value, setValue];
}
