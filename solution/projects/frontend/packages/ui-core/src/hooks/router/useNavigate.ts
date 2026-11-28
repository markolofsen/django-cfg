'use client';

/**
 * useNavigate — programmatic navigation primitive.
 *
 * WHY:
 *   Wraps the active adapter's push/replace and adds the small ergonomics
 *   we want on every nav: optional scroll-to-top, replace flag, and a
 *   distinct `navigateExternal` for full-reload flows (logout, OAuth,
 *   cross-origin redirects) where SPA navigation would be wrong.
 *
 *   No `useTransition` here — that's a Next/React-internal concern; if
 *   the consumer wants pending state they wrap our calls themselves.
 *
 * @example
 *   const { navigate, navigateExternal } = useNavigate();
 *   navigate('/dashboard');
 *   navigate('/dashboard', { replace: true, scroll: false });
 *   navigateExternal('/api/auth/logout');
 */

import { useCallback, useMemo } from 'react';
import { useRouterAdapter, type RouterNavigateOptions } from './adapter';

export interface NavigateOptions {
  /** Use `replaceState` instead of `pushState`. Default: false. */
  replace?: boolean;
  /**
   * Scroll to top after navigation. Default: false.
   *
   * Most SPA flows (filter/pagination/tab switches) shouldn't jump,
   * which is why this is opt-in. Pass `true` for top-level page
   * transitions where you want the user back at the masthead.
   */
  scroll?: boolean;
  /**
   * Show the top loading bar. Default: only when the pathname changes.
   * `true` forces it, `false` suppresses it.
   */
  progress?: boolean;
}

export interface UseNavigateReturn {
  /**
   * SPA navigation through the active adapter.
   * Default: pushState, and NO scroll — pass `scroll: true` for a transition
   * that should land the visitor at the top.
   */
  navigate: (href: string, opts?: NavigateOptions) => void;
  /**
   * Hard navigation via `window.location.assign` — full page reload.
   * Use for logout, OAuth, or any cross-origin handoff.
   */
  navigateExternal: (href: string) => void;
  /**
   * Write the URL without a navigation (no server request, no bar, no scroll), see
   * `RouterAdapter.shallow`. Falls back to `push`/`replace` with bar and scroll off
   * when the adapter has no shallow write.
   */
  shallow: (href: string, opts?: { replace?: boolean }) => void;
  /** Pass-through: adapter.push */
  push: (url: string, opts?: RouterNavigateOptions) => void;
  /** Pass-through: adapter.replace */
  replace: (url: string, opts?: RouterNavigateOptions) => void;
  /** Pass-through: adapter.back */
  back: () => void;
  /** Pass-through: adapter.forward */
  forward: () => void;
}

/**
 * Returns stable navigation functions backed by the active router adapter.
 * Safe to put returned functions in deps arrays.
 */
export function useNavigate(): UseNavigateReturn {
  const adapter = useRouterAdapter();

  const navigate = useCallback(
    (href: string, opts?: NavigateOptions) => {
      const replace = opts?.replace ?? false;
      const scroll = opts?.scroll ?? false;
      const adapterOpts = { scroll: opts?.scroll, progress: opts?.progress };
      if (replace) {
        adapter.replace(href, adapterOpts);
      } else {
        adapter.push(href, adapterOpts);
      }
      if (scroll && typeof window !== 'undefined') {
        window.scrollTo(0, 0);
      }
    },
    [adapter]
  );

  const shallow = useCallback(
    (href: string, opts?: { replace?: boolean }) => {
      if (adapter.shallow) {
        adapter.shallow(href, opts);
        return;
      }
      const fallback = { scroll: false, progress: false };
      if (opts?.replace) adapter.replace(href, fallback);
      else adapter.push(href, fallback);
    },
    [adapter]
  );

  const navigateExternal = useCallback((href: string) => {
    if (typeof window === 'undefined') return;
    window.location.assign(href);
  }, []);

  const push = useCallback((url: string, opts?: RouterNavigateOptions) => adapter.push(url, opts), [adapter]);
  const replace = useCallback((url: string, opts?: RouterNavigateOptions) => adapter.replace(url, opts), [adapter]);
  const back = useCallback(() => adapter.back(), [adapter]);
  const forward = useCallback(() => adapter.forward(), [adapter]);

  return useMemo<UseNavigateReturn>(
    () => ({ navigate, navigateExternal, shallow, push, replace, back, forward }),
    [navigate, navigateExternal, shallow, push, replace, back, forward]
  );
}
