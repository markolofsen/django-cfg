'use client';

/**
 * usePathnameChange — run a callback when the page moves to another PATH.
 *
 * WHY: a surface that covers the page (a sheet, a drawer, a menu) has to go away when the reader navigates
 * (a link inside it, a button that calls `router.push`). It must NOT go away when only the query string or the
 * hash changes: a filter, a tab or a page number written to the URL is a state of the same page.
 *
 * Framework-agnostic like the rest of the router hooks: it listens to `popstate` and to the `pushState` /
 * `replaceState` event of `useLocation`, so it sees every router (Next, React Router, the History API) without
 * being told which one is mounted. The first render is never a change; the baseline is the path at the moment the
 * hook becomes `enabled`.
 *
 * @example
 *   const isMobile = useIsMobile();
 *   usePathnameChange(() => setOpen(false), { enabled: open && isMobile });
 */

import { useEffect, useRef } from 'react';

import { NAVIGATE_EVENT, patchHistoryOnce } from './useLocation';

/** Called with the new path and the one before it. */
export type PathnameChangeHandler = (pathname: string, previous: string) => void;

/**
 * Non-React core: calls `onChange` each time `window.location.pathname` differs from the last one seen, and returns
 * the unsubscribe. Same path (a query or hash change, a repeated `replaceState`) never calls it. No-op on the server.
 */
export function watchPathname(onChange: PathnameChangeHandler): () => void {
  if (typeof window === 'undefined') return () => {};
  patchHistoryOnce();
  let last = window.location.pathname;
  const check = () => {
    const next = window.location.pathname;
    if (next === last) return;
    const previous = last;
    last = next;
    onChange(next, previous);
  };
  window.addEventListener('popstate', check);
  window.addEventListener(NAVIGATE_EVENT, check);
  return () => {
    window.removeEventListener('popstate', check);
    window.removeEventListener(NAVIGATE_EVENT, check);
  };
}

export interface UsePathnameChangeOptions {
  /** Subscribe only while true (for example while a sheet is open). Default: true. */
  enabled?: boolean;
}

/** Runs `handler` after each change of the pathname while `enabled`; query and hash changes are ignored. */
export function usePathnameChange(handler: PathnameChangeHandler, { enabled = true }: UsePathnameChangeOptions = {}): void {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;
  useEffect(() => {
    if (!enabled) return;
    return watchPathname((pathname, previous) => handlerRef.current(pathname, previous));
  }, [enabled]);
}
