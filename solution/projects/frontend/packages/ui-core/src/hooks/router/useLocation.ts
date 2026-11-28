'use client';

/**
 * useLocation — reactive snapshot of `window.location`.
 *
 * WHY:
 *   Native `popstate` only fires on back/forward, NOT on `pushState` /
 *   `replaceState`. To make SPA navigations observable we monkey-patch
 *   those two methods once (idempotent) and dispatch a custom
 *   `djc:navigate` event after each call. All router hooks, the default
 *   adapter, and any code that calls history.* APIs anywhere in the page
 *   will trigger this event automatically.
 *
 *   We use `useSyncExternalStore` because that is the React-19-blessed
 *   way to bridge external mutable state (window.location) into React's
 *   render model — it gets concurrent-render and SSR right (via
 *   getServerSnapshot).
 *
 * @example
 *   const { pathname, search, hash, href } = useLocation();
 *   useEffect(() => { analytics.page(pathname); }, [pathname]);
 */

import { useSyncExternalStore } from 'react';

/**
 * Browser-event name we dispatch when pushState/replaceState run.
 * `pushState` and `replaceState` events fire alongside this for consumers
 * that want to distinguish between the two history operations (wouter
 * uses the same convention: separate per-method events PLUS a generic one).
 */
export const NAVIGATE_EVENT = 'djc:navigate';
export const PUSH_STATE_EVENT = 'pushState';
export const REPLACE_STATE_EVENT = 'replaceState';

/** Frozen snapshot returned to React. Identity changes only on URL change. */
export interface LocationSnapshot {
  pathname: string;
  search: string;
  hash: string;
  href: string;
}

const SSR_SNAPSHOT: LocationSnapshot = Object.freeze({
  pathname: '/',
  search: '',
  hash: '',
  href: '/',
});

// Patch-once guard via a Symbol on `window`. We use a Symbol-on-window
// (wouter's pattern) instead of tagging the function because it survives
// other libraries re-patching the methods on top of us — once anybody
// (us or them) has installed a patch, the marker stays until full reload.
const PATCH_KEY = Symbol.for('djc.router.historyPatched');

/**
 * Installs the `pushState`/`replaceState` patch that makes SPA navigations
 * observable, exactly once per document.
 *
 * Exported because `useLocation` is no longer the only subscriber: a hook may
 * listen for `NAVIGATE_EVENT` without reading the location through
 * `useSyncExternalStore` (see `useScrollToTop`), and without this call it
 * would subscribe to an event nothing dispatches — silently doing nothing.
 */
export function patchHistoryOnce(): void {
  if (typeof window === 'undefined') return;
  const w = window as Window & { [PATCH_KEY]?: true };
  if (w[PATCH_KEY]) return;

  const originalPush = window.history.pushState.bind(window.history);
  const originalReplace = window.history.replaceState.bind(window.history);

  // Defer dispatch to a microtask so the events fire AFTER the caller's
  // current commit/insertion phase. Otherwise React fires useInsertionEffect
  // → next/link calls pushState → patched handler synchronously dispatches →
  // useSyncExternalStore subscribers schedule state updates inside the same
  // insertion phase → React throws "useInsertionEffect must not schedule
  // updates". queueMicrotask preserves event ordering relative to other
  // microtasks (Promise resolutions) without yielding to the macrotask queue.
  const dispatchDeferred = (...events: string[]) => {
    queueMicrotask(() => {
      for (const name of events) window.dispatchEvent(new Event(name));
    });
  };

  window.history.pushState = function patchedPushState(
    ...args: Parameters<History['pushState']>
  ) {
    const result = originalPush(...args);
    // Two events: the per-method one (consumers can listen narrowly)
    // and a generic NAVIGATE_EVENT for "any url change" subscribers.
    dispatchDeferred(PUSH_STATE_EVENT, NAVIGATE_EVENT);
    return result;
  };

  window.history.replaceState = function patchedReplaceState(
    ...args: Parameters<History['replaceState']>
  ) {
    const result = originalReplace(...args);
    dispatchDeferred(REPLACE_STATE_EVENT, NAVIGATE_EVENT);
    return result;
  };

  Object.defineProperty(w, PATCH_KEY, { value: true });
}

// Cache the snapshot so getSnapshot returns the same reference between
// notifications. useSyncExternalStore demands referential stability between
// reads — recomputing the object on every call would loop in React 18+.
let cachedSnapshot: LocationSnapshot = SSR_SNAPSHOT;

function readLocation(): LocationSnapshot {
  if (typeof window === 'undefined') return SSR_SNAPSHOT;
  const { pathname, search, hash, href } = window.location;
  // Only mint a new object if something actually changed.
  if (
    cachedSnapshot.pathname === pathname &&
    cachedSnapshot.search === search &&
    cachedSnapshot.hash === hash &&
    cachedSnapshot.href === href
  ) {
    return cachedSnapshot;
  }
  cachedSnapshot = Object.freeze({ pathname, search, hash, href });
  return cachedSnapshot;
}

function subscribe(onChange: () => void): () => void {
  if (typeof window === 'undefined') return () => {};
  patchHistoryOnce();
  // Wrap the callback so both popstate and our custom event refresh
  // the cached snapshot before React re-reads it.
  const handler = () => {
    // Force re-read on next getSnapshot call by resetting the cache.
    // We intentionally don't read here — getSnapshot will compare and
    // return a stable ref if nothing changed (e.g. duplicate events).
    onChange();
  };
  window.addEventListener('popstate', handler);
  window.addEventListener(NAVIGATE_EVENT, handler);
  // hashchange covers programmatic location.hash assignments that bypass
  // pushState. Cheap to subscribe to.
  window.addEventListener('hashchange', handler);
  return () => {
    window.removeEventListener('popstate', handler);
    window.removeEventListener(NAVIGATE_EVENT, handler);
    window.removeEventListener('hashchange', handler);
  };
}

function getServerSnapshot(): LocationSnapshot {
  return SSR_SNAPSHOT;
}

/**
 * Reactive snapshot of the current URL.
 * Re-renders the calling component on every history navigation
 * (pushState / replaceState / back / forward / hashchange).
 *
 * If you only need ONE field (e.g. just pathname), prefer
 * `useLocationProperty(() => location.pathname)` — it subscribes to
 * the same store but lets React skip re-renders when other fields
 * change. Same pattern as `wouter`'s `usePathname` / `useSearch`.
 */
export function useLocation(): LocationSnapshot {
  return useSyncExternalStore(subscribe, readLocation, getServerSnapshot);
}

/**
 * Subscribe to one derived value from `window.location`. React only
 * re-renders when the returned value changes — so a component reading
 * just `pathname` won't re-render on `?page=2` updates.
 *
 * @example
 *   const pathname = useLocationProperty(() => window.location.pathname, () => '/');
 */
export function useLocationProperty<T>(
  getValue: () => T,
  getServerValue: () => T
): T {
  return useSyncExternalStore(subscribe, getValue, getServerValue);
}
