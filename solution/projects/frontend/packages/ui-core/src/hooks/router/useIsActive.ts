'use client';

/**
 * useIsActive — boolean for "current pathname matches this href".
 *
 * WHY:
 *   Highlighting the active item in a navbar / sidebar is the most-copy-
 *   pasted snippet in any SPA: `pathname === href || pathname.startsWith(href + '/')`.
 *   This hook bakes in the right semantics (exact-vs-prefix, trailing-slash
 *   tolerance, query/hash ignoring) so consumers don't have to reinvent them.
 *
 * @example
 *   const isActive = useIsActive('/dashboard');
 *   const isProductsActive = useIsActive('/products', { exact: false });
 *   <Link className={isActive ? 'active' : ''}>...</Link>
 */

import { useMemo } from 'react';
import { useLocation } from './useLocation';

export interface UseIsActiveOptions {
  /**
   * `true` (default) — match only when pathname === href.
   * `false` — match when pathname is href OR a sub-path (`href/...`).
   * Most navbar items want `false`; tab strips usually want `true`.
   */
  exact?: boolean;
  /**
   * Strip a trailing slash from both sides before comparing.
   * Default: true.
   */
  ignoreTrailingSlash?: boolean;
}

function normalize(path: string, ignoreTrailingSlash: boolean): string {
  if (!ignoreTrailingSlash) return path;
  if (path.length > 1 && path.endsWith('/')) return path.slice(0, -1);
  return path;
}

/**
 * Returns `true` if `href` matches the current pathname.
 * Pure path-based — search and hash are ignored.
 */
export function useIsActive(href: string, options?: UseIsActiveOptions): boolean {
  const { pathname } = useLocation();
  const exact = options?.exact ?? false;
  const ignoreTrailingSlash = options?.ignoreTrailingSlash ?? true;

  return useMemo(() => {
    // Strip search/hash from href if the consumer passed a full URL.
    const cleanHref = href.split('?')[0]?.split('#')[0] ?? href;
    const a = normalize(pathname, ignoreTrailingSlash);
    const b = normalize(cleanHref, ignoreTrailingSlash);
    if (a === b) return true;
    if (exact) return false;
    // Sub-path match: prefix + boundary so `/foobar` doesn't match `/foo`.
    return a.startsWith(b + '/');
  }, [pathname, href, exact, ignoreTrailingSlash]);
}
