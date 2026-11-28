'use client';

/**
 * useRouter — composite facade over the atomic router hooks.
 *
 * WHY:
 *   For consumers who want a single import that "feels like" Next's
 *   `useRouter`. Composes useLocation + useNavigate + useQueryParams +
 *   useBackOrFallback + useUrlBuilder.
 *
 * NOTE on perf and tree-shaking:
 *   This hook subscribes to EVERY URL change (location, search, depth)
 *   because it composes hooks that subscribe to those things. If your
 *   component only needs `navigate` (no location read), prefer the
 *   atomic `useNavigate()` to avoid extra re-renders. Same for
 *   `useQueryParams`, `useUrlBuilder`, etc. The atomic hooks also
 *   tree-shake better — pulling in just `useNavigate` doesn't pay the
 *   cost of the snapshot machinery.
 *
 * @example
 *   const router = useRouter();
 *   router.navigate('/users');
 *   router.query.set({ page: 2 });
 *   router.backOrFallback('/dashboard');
 */

import { useMemo } from 'react';
import { useLocation, type LocationSnapshot } from './useLocation';
import { useNavigate, type UseNavigateReturn } from './useNavigate';
import { useQueryParams, type UseQueryParamsReturn } from './useQueryParams';
import { useBackOrFallback } from './useBackOrFallback';
import { useUrlBuilder, type UseUrlBuilderReturn } from './useUrlBuilder';

export interface UseRouterReturn extends LocationSnapshot, UseNavigateReturn {
  /** Same as `useQueryParams()`. */
  query: UseQueryParamsReturn;
  /** Same as `useUrlBuilder().build`. */
  build: UseUrlBuilderReturn['build'];
  /** Same as `useUrlBuilder().withCurrentParams`. */
  withCurrentParams: UseUrlBuilderReturn['withCurrentParams'];
  /** Same as `useBackOrFallback().back`. */
  backOrFallback: (fallback?: string) => void;
  /** Same as `useBackOrFallback().canGoBack`. */
  canGoBack: boolean;
}

/**
 * Convenience hook that exposes the full router surface.
 * For minimal re-renders / smaller bundles, prefer the atomic hooks.
 */
export function useRouter(): UseRouterReturn {
  const location = useLocation();
  const nav = useNavigate();
  const query = useQueryParams();
  const builder = useUrlBuilder();
  const { back: backOrFallback, canGoBack } = useBackOrFallback();

  return useMemo<UseRouterReturn>(
    () => ({
      // Location snapshot
      pathname: location.pathname,
      search: location.search,
      hash: location.hash,
      href: location.href,
      // Navigation pass-through
      navigate: nav.navigate,
      navigateExternal: nav.navigateExternal,
      shallow: nav.shallow,
      push: nav.push,
      replace: nav.replace,
      back: nav.back,
      forward: nav.forward,
      // Sub-APIs
      query,
      build: builder.build,
      withCurrentParams: builder.withCurrentParams,
      backOrFallback,
      canGoBack,
    }),
    [location, nav, query, builder, backOrFallback, canGoBack]
  );
}
