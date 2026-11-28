'use client';

/**
 * useQueryParams — read & write `?key=value` URL state.
 *
 * WHY:
 *   Pagination, filters, sort, search-as-you-type all live in the URL.
 *   This hook gives a typed, ergonomic surface (get/getNumber/getBoolean,
 *   set with merge semantics, remove, clear) so consumers don't reinvent
 *   URLSearchParams plumbing in every component.
 *
 * @example
 *   const { params, get, set, remove } = useQueryParams();
 *   const page = get('page', '1');
 *   set({ page: 2, sort: 'asc' });            // merges
 *   set({ q: 'foo' }, { reset: true });       // drops everything else
 *   set({ q: 'foo' }, { preserve: ['tab'] }); // keeps only `tab`
 *   remove(['page', 'sort']);
 */

import { useCallback, useMemo } from 'react';
import { useLocation } from './useLocation';
import { useNavigate } from './useNavigate';

/** Snapshot of current params. Single value = string, repeated key = string[]. */
export type QueryParamsSnapshot = Record<string, string | string[]>;

/** Value type accepted by `set`. Empty/null/undefined ⇒ delete the key. */
export type QueryParamValue =
  | string
  | number
  | boolean
  | null
  | undefined
  | Array<string | number | boolean>;

export interface QueryParamUpdates {
  [key: string]: QueryParamValue;
}

export interface SetQueryParamsOptions {
  /** Use `replaceState` instead of `pushState`. Default: false. */
  replace?: boolean;
  /**
   * Drop ALL existing params before applying updates.
   * Useful when filters change and pagination should reset.
   */
  reset?: boolean;
  /**
   * If `reset` is true, keep these keys from the current URL.
   * Ignored when `reset` is false.
   */
  preserve?: string[];
  /** Scroll to top after navigation. Default: false (filters/pagination shouldn't jump). */
  scroll?: boolean;
}

function snapshotFromSearch(search: string): QueryParamsSnapshot {
  const out: QueryParamsSnapshot = {};
  if (!search) return out;
  const params = new URLSearchParams(search);
  // Build with multi-value awareness.
  for (const key of new Set(params.keys())) {
    const all = params.getAll(key);
    out[key] = all.length > 1 ? all : (all[0] ?? '');
  }
  return out;
}

function applyUpdates(
  target: URLSearchParams,
  updates: QueryParamUpdates
): void {
  for (const key of Object.keys(updates)) {
    const value = updates[key];
    target.delete(key);
    if (value === null || value === undefined) continue;
    if (Array.isArray(value)) {
      for (const item of value) {
        if (item === '' || item === null || item === undefined) continue;
        target.append(key, String(item));
      }
      continue;
    }
    if (typeof value === 'string' && value === '') continue;
    target.append(key, String(value));
  }
}

export interface UseQueryParamsReturn {
  /** Current params snapshot. Identity changes only on querystring change. */
  params: QueryParamsSnapshot;

  /**
   * Read a single value (first one if repeated).
   * Returns `fallback` (or `undefined`) when the key is missing.
   */
  get: <T extends string = string>(key: string, fallback?: T) => T | undefined;

  /** Read all values for a repeated key. Empty array if missing. */
  getAll: (key: string) => string[];

  /**
   * Read & coerce to number. Returns fallback (or `undefined`) when
   * missing or unparseable. NaN is treated as missing.
   */
  getNumber: (key: string, fallback?: number) => number | undefined;

  /**
   * Read & coerce to boolean. `'true'` / `'1'` / `''` (key present, no value)
   * → true. Anything else → false. Returns fallback when key missing.
   */
  getBoolean: (key: string, fallback?: boolean) => boolean | undefined;

  /** Merge updates into current params and navigate. */
  set: (updates: QueryParamUpdates, opts?: SetQueryParamsOptions) => void;

  /** Drop one or more keys and navigate. */
  remove: (keys: string | string[], opts?: SetQueryParamsOptions) => void;

  /** Drop all params and navigate. */
  clear: (opts?: SetQueryParamsOptions) => void;

  /** Current querystring without leading `?`. */
  toString: () => string;

  /** Build `path?currentSearch` for use in `<a href={...}>`. */
  toUrl: (path: string) => string;
}

/**
 * Reactive read + ergonomic write for `?key=value` URL state.
 * Re-renders only when the search string changes.
 */
export function useQueryParams(): UseQueryParamsReturn {
  const { pathname, search } = useLocation();
  const { navigate } = useNavigate();

  // Snapshot is rebuilt only when `search` changes — useMemo is enough.
  const params = useMemo(() => snapshotFromSearch(search), [search]);

  const get = useCallback(
    <T extends string = string>(key: string, fallback?: T): T | undefined => {
      const value = params[key];
      if (value === undefined) return fallback;
      const first = Array.isArray(value) ? value[0] : value;
      if (first === undefined || first === '') return fallback;
      return first as T;
    },
    [params]
  );

  const getAll = useCallback(
    (key: string): string[] => {
      const value = params[key];
      if (value === undefined) return [];
      return Array.isArray(value) ? value : [value];
    },
    [params]
  );

  const getNumber = useCallback(
    (key: string, fallback?: number): number | undefined => {
      const raw = get(key);
      if (raw === undefined) return fallback;
      const num = Number(raw);
      return Number.isFinite(num) ? num : fallback;
    },
    [get]
  );

  const getBoolean = useCallback(
    (key: string, fallback?: boolean): boolean | undefined => {
      const raw = get(key);
      if (raw === undefined) return fallback;
      // '' means key was present without a value (e.g. ?debug)
      // — treat as truthy. Match URLSearchParams behavior.
      if (raw === '' || raw === 'true' || raw === '1') return true;
      return false;
    },
    [get]
  );

  const navigateWithSearch = useCallback(
    (next: URLSearchParams, opts?: SetQueryParamsOptions) => {
      const qs = next.toString();
      const href = qs ? `${pathname}?${qs}` : pathname;
      navigate(href, {
        replace: opts?.replace ?? false,
        scroll: opts?.scroll ?? false,
      });
    },
    [pathname, navigate]
  );

  const set = useCallback(
    (updates: QueryParamUpdates, opts?: SetQueryParamsOptions) => {
      let next: URLSearchParams;
      if (opts?.reset) {
        next = new URLSearchParams();
        if (opts.preserve && opts.preserve.length > 0) {
          const current = new URLSearchParams(search);
          for (const key of opts.preserve) {
            const all = current.getAll(key);
            for (const item of all) next.append(key, item);
          }
        }
      } else {
        next = new URLSearchParams(search);
      }
      applyUpdates(next, updates);
      navigateWithSearch(next, opts);
    },
    [search, navigateWithSearch]
  );

  const remove = useCallback(
    (keys: string | string[], opts?: SetQueryParamsOptions) => {
      const next = new URLSearchParams(search);
      const list = Array.isArray(keys) ? keys : [keys];
      for (const key of list) next.delete(key);
      navigateWithSearch(next, opts);
    },
    [search, navigateWithSearch]
  );

  const clear = useCallback(
    (opts?: SetQueryParamsOptions) => {
      navigateWithSearch(new URLSearchParams(), opts);
    },
    [navigateWithSearch]
  );

  const toString = useCallback((): string => {
    // search includes the leading '?', strip it.
    return search.startsWith('?') ? search.slice(1) : search;
  }, [search]);

  const toUrl = useCallback(
    (path: string): string => {
      const qs = toString();
      return qs ? `${path}?${qs}` : path;
    },
    [toString]
  );

  return useMemo<UseQueryParamsReturn>(
    () => ({
      params,
      get,
      getAll,
      getNumber,
      getBoolean,
      set,
      remove,
      clear,
      toString,
      toUrl,
    }),
    [params, get, getAll, getNumber, getBoolean, set, remove, clear, toString, toUrl]
  );
}
