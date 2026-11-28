'use client';

/**
 * useUrlBuilder — pure URL/querystring assembly.
 *
 * WHY:
 *   Building URLs by hand (template literals + URLSearchParams) is fiddly:
 *   you have to remember to skip empty values, encode keys, handle arrays.
 *   This hook centralizes those rules so callers stay declarative.
 *   Zero side effects — only React-bound thing is `useCallback` for ref
 *   stability inside JSX.
 *
 * @example
 *   const { build, withCurrentParams } = useUrlBuilder();
 *   build('/products', { page: 2, tag: ['a', 'b'], q: '' });
 *   //   '/products?page=2&tag=a&tag=b'
 *   withCurrentParams('/products', { page: 1 });
 *   //   keeps everything in current ?…, overrides `page`
 */

import { useCallback, useMemo } from 'react';
import { useLocation } from './useLocation';

/** Value types accepted by `build`. Empty/null/undefined are stripped. */
export type QueryValue = string | number | boolean | null | undefined;
/** Param map. Arrays become repeated keys (`?tag=a&tag=b`), not csv. */
export type QueryParamsInput = Record<string, QueryValue | QueryValue[]>;

function appendValue(
  params: URLSearchParams,
  key: string,
  value: QueryValue
): void {
  if (value === null || value === undefined) return;
  if (typeof value === 'string' && value === '') return;
  // Booleans serialize as 'true'/'false' — common-sense default.
  params.append(key, String(value));
}

/**
 * Build a query-string fragment (no leading `?`) from a param map.
 * Skips empty / null / undefined values; arrays become repeated keys.
 * Exported standalone so utilities can share the same rules without a hook.
 */
export function buildQueryString(params?: QueryParamsInput): string {
  if (!params) return '';
  const search = new URLSearchParams();
  for (const key of Object.keys(params)) {
    const value = params[key];
    if (Array.isArray(value)) {
      for (const item of value) appendValue(search, key, item);
    } else {
      appendValue(search, key, value);
    }
  }
  return search.toString();
}

/**
 * Build a full path: `path + '?' + qs` (or just `path` if qs is empty).
 * Pure — useful outside React (link generators, server code).
 */
export function buildUrl(path: string, params?: QueryParamsInput): string {
  const qs = buildQueryString(params);
  return qs ? `${path}?${qs}` : path;
}

export interface UseUrlBuilderReturn {
  /** Assemble `path` + serialized params. */
  build: (path: string, params?: QueryParamsInput) => string;
  /**
   * Assemble `path` keeping the current page's querystring,
   * with `overrides` merged on top. Pass `null`/`undefined`/`''` in
   * `overrides` to drop a key.
   */
  withCurrentParams: (
    path: string,
    overrides?: QueryParamsInput
  ) => string;
}

/**
 * Stable URL builder helpers. `withCurrentParams` re-renders when the
 * current querystring changes (it reads `useLocation` internally).
 */
export function useUrlBuilder(): UseUrlBuilderReturn {
  const { search } = useLocation();

  const build = useCallback((path: string, params?: QueryParamsInput): string => {
    return buildUrl(path, params);
  }, []);

  const withCurrentParams = useCallback(
    (path: string, overrides?: QueryParamsInput): string => {
      const next = new URLSearchParams(search);
      if (overrides) {
        for (const key of Object.keys(overrides)) {
          const value = overrides[key];
          // Overrides semantics: drop on empty, replace otherwise.
          next.delete(key);
          if (Array.isArray(value)) {
            for (const item of value) appendValue(next, key, item);
          } else {
            appendValue(next, key, value);
          }
        }
      }
      const qs = next.toString();
      return qs ? `${path}?${qs}` : path;
    },
    [search]
  );

  return useMemo<UseUrlBuilderReturn>(
    () => ({ build, withCurrentParams }),
    [build, withCurrentParams]
  );
}
