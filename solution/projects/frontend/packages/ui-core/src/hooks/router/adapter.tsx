'use client';

/**
 * Router adapter — pluggable navigation backend.
 *
 * WHY:
 *   `@djangocfg/ui-core` is framework-agnostic, but consumers using Next.js,
 *   TanStack Router, wouter, etc. need SPA navigations to flow through their
 *   own router so server components / data loaders / route guards fire
 *   correctly. The adapter pattern lets the consumer swap the implementation
 *   without changing call-sites inside library components.
 *
 * Default behavior uses `window.history.pushState` + `window.location` (works
 * in any browser, zero deps). When no provider is mounted, the default is
 * silently used.
 *
 * @example
 * // In a Next.js app:
 * import { useRouter as useNextRouter } from 'next/navigation';
 * import { RouterAdapterProvider } from '@djangocfg/ui-core/hooks';
 *
 * function NextAdapter({ children }: { children: React.ReactNode }) {
 *   const next = useNextRouter();
 *   const adapter = useMemo(() => ({
 *     push: (url: string) => next.push(url),
 *     replace: (url: string) => next.replace(url),
 *     back: () => next.back(),
 *     forward: () => next.forward(),
 *     getLocation: () => ({
 *       pathname: window.location.pathname,
 *       search: window.location.search,
 *       hash: window.location.hash,
 *     }),
 *   }), [next]);
 *   return <RouterAdapterProvider value={adapter}>{children}</RouterAdapterProvider>;
 * }
 */

import { createContext, useContext, useMemo, type ReactNode } from 'react';

/**
 * Snapshot of the current URL location.
 * Mirrors the parts of `window.location` we actually use.
 */
export interface RouterLocation {
  pathname: string;
  search: string;
  hash: string;
}

/**
 * Pluggable navigation backend. Implementations must be SSR-safe
 * (mutations should no-op when `typeof window === 'undefined'`).
 */
export interface RouterNavigateOptions {
  /**
   * Scroll to the top after the navigation. Absent: the adapter's own default
   * (Next: its `scroll: true`). `false` keeps the position, e.g. for a filter.
   */
  scroll?: boolean;
  /**
   * Show the top loading bar. Absent: only when the pathname changes (a query or
   * hash change is not a page transition). `true` forces it, `false` suppresses it.
   * Adapters without a bar ignore it.
   */
  progress?: boolean;
}

export interface RouterAdapter {
  /** Push a new entry onto the history stack. */
  push: (url: string, opts?: RouterNavigateOptions) => void;
  /** Replace the current history entry. */
  replace: (url: string, opts?: RouterNavigateOptions) => void;
  /** Go back one entry. */
  back: () => void;
  /** Go forward one entry. */
  forward: () => void;
  /** Read the current location (synchronous). */
  getLocation: () => RouterLocation;
  /**
   * Write the URL without a navigation: no request to the server, no server
   * components re-rendered, no loading bar, no scroll. For state that only the
   * client needs (a view mode, a zoom, a slider). Optional: when an adapter has
   * none, callers fall back to `push`/`replace` with the bar and the scroll off.
   * Implementations must pass `null` as the history state: Next syncs
   * `useSearchParams` only for entries without its own router keys.
   */
  shallow?: (url: string, opts?: { replace?: boolean }) => void;
}

const SSR_LOCATION: RouterLocation = Object.freeze({
  pathname: '/',
  search: '',
  hash: '',
});

/**
 * Default adapter — uses History API + window.location.
 * No-ops on the server. Triggers our internal `djc:navigate` event so
 * `useLocation` reflects the change (see `useLocation.ts`).
 */
export const defaultAdapter: RouterAdapter = Object.freeze({
  push(url: string) {
    if (typeof window === 'undefined') return;
    window.history.pushState(null, '', url);
  },
  replace(url: string) {
    if (typeof window === 'undefined') return;
    window.history.replaceState(null, '', url);
  },
  back() {
    if (typeof window === 'undefined') return;
    window.history.back();
  },
  forward() {
    if (typeof window === 'undefined') return;
    window.history.forward();
  },
  getLocation(): RouterLocation {
    if (typeof window === 'undefined') return SSR_LOCATION;
    return {
      pathname: window.location.pathname,
      search: window.location.search,
      hash: window.location.hash,
    };
  },
  shallow(url: string, opts?: { replace?: boolean }) {
    writeUrlShallow(url, opts?.replace ?? false);
  },
});

/**
 * Write the URL through the History API and nothing else. The state is `null`,
 * never `history.state`: Next marks its own entries (`__NA`, `_N`) and ignores
 * the ones it did not make when it syncs `useSearchParams`/`usePathname`.
 * Our patched `pushState`/`replaceState` tell `useLocation`, so hooks update.
 */
export function writeUrlShallow(url: string, replace: boolean): void {
  if (typeof window === 'undefined') return;
  if (replace) window.history.replaceState(null, '', url);
  else window.history.pushState(null, '', url);
}

/**
 * React context carrying the active adapter. `null` means "use default".
 * Kept intentionally nullable so we don't burn a Provider for the default case.
 */
// Keyed on a global for the same reason as LinkComponentContext: this module is
// reached both from the package root and from the `/adapters/*` subpath, and a
// per-specifier instantiation would leave the provider filling one context while
// every hook reads another — falling back to the History API, which changes the
// URL without telling the host router.
const CONTEXT_KEY = Symbol.for('@djangocfg/ui-core.RouterAdapterContext');
// `typeof globalThis` carries no index signature, but the object genuinely
// accepts symbol keys — this asserts a property the runtime has.
const globalScope = globalThis as Record<symbol, unknown>;

export const RouterAdapterContext =
  (globalScope[CONTEXT_KEY] as ReturnType<typeof createContext<RouterAdapter | null>> | undefined) ??
  (globalScope[CONTEXT_KEY] = createContext<RouterAdapter | null>(null));

export interface RouterAdapterProviderProps {
  /** Adapter implementation. Will be used by every router hook in subtree. */
  value: RouterAdapter;
  children: ReactNode;
}

/**
 * Wrap a subtree to override the navigation backend used by router hooks.
 */
export function RouterAdapterProvider({ value, children }: RouterAdapterProviderProps) {
  // Memoizing here is the consumer's job (the value usually comes from another hook).
  // We don't double-memo — that just adds noise.
  return (
    <RouterAdapterContext.Provider value={value}>
      {children}
    </RouterAdapterContext.Provider>
  );
}

/**
 * Read the active router adapter. Returns the default History API adapter
 * if no provider is mounted.
 */
export function useRouterAdapter(): RouterAdapter {
  const ctx = useContext(RouterAdapterContext);
  // useMemo so consumers can put the returned value in deps without churn.
  return useMemo(() => ctx ?? defaultAdapter, [ctx]);
}
