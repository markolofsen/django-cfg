'use client';

import * as React from 'react';

import { useUIPersistStore } from './store';

export interface UseUIPersistedStateOptions<T> {
  /**
   * Optional sanitizer applied to the stored value on load. Use it to
   * clamp numbers into bounds, drop unknown enum values, or migrate
   * shape. Return `undefined` to fall back to default.
   */
  sanitize?: (raw: T) => T | undefined;
}

export interface UseUIPersistedStateResult<T> {
  /** Current value: persisted (post-sanitize) if available, otherwise the default. */
  value: T;
  /** Persist a new value. */
  setValue: (next: T) => void;
  /** Remove the persisted entry. `value` reverts to default on next render. */
  reset: () => void;
  /** True once the persist middleware has rehydrated from storage. */
  hydrated: boolean;
}

/**
 * Read/write a piece of UI state in the centralized persisted store.
 *
 * @param scope  Namespace (e.g. `'drawer-size'`, `'tabs'`). Pick a
 *               stable string per component family.
 * @param key    Per-instance identifier within the scope.
 * @param defaultValue  Used until hydration completes or when no value is stored.
 *
 * @example
 * const { value, setValue, reset } = useUIPersistedState('tabs', 'settings', 'general');
 */
export function useUIPersistedState<T>(
  scope: string,
  key: string,
  defaultValue: T,
  options: UseUIPersistedStateOptions<T> = {},
): UseUIPersistedStateResult<T> {
  const { sanitize } = options;
  const [hydrated, setHydrated] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;
    Promise.resolve(useUIPersistStore.persist.rehydrate()).then(() => {
      if (!cancelled) setHydrated(true);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const stored = useUIPersistStore(
    (s) => s.state[scope]?.[key] as T | undefined,
  );

  const value = React.useMemo(() => {
    if (!hydrated || stored === undefined) return defaultValue;
    if (sanitize) {
      const sanitized = sanitize(stored);
      return sanitized === undefined ? defaultValue : sanitized;
    }
    return stored;
  }, [hydrated, stored, defaultValue, sanitize]);

  const setValue = React.useCallback(
    (next: T) => {
      useUIPersistStore.getState().set(scope, key, next);
    },
    [scope, key],
  );

  const reset = React.useCallback(() => {
    useUIPersistStore.getState().remove(scope, key);
  }, [scope, key]);

  return { value, setValue, reset, hydrated };
}

/**
 * Same as `useUIPersistedState` but trailing-edge throttles writes by
 * `delayMs`. Use for high-frequency updates (live splitter drag, scroll
 * position) where you don't want to hammer storage.
 */
export function useUIPersistedStateThrottled<T>(
  scope: string,
  key: string,
  defaultValue: T,
  delayMs: number,
  options: UseUIPersistedStateOptions<T> = {},
): UseUIPersistedStateResult<T> {
  const base = useUIPersistedState(scope, key, defaultValue, options);
  const timerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingRef = React.useRef<T | null>(null);

  const setValue = React.useCallback(
    (next: T) => {
      pendingRef.current = next;
      if (timerRef.current != null) return;
      timerRef.current = setTimeout(() => {
        timerRef.current = null;
        if (pendingRef.current !== null) {
          base.setValue(pendingRef.current);
          pendingRef.current = null;
        }
      }, delayMs);
    },
    [base, delayMs],
  );

  React.useEffect(
    () => () => {
      if (timerRef.current != null) clearTimeout(timerRef.current);
    },
    [],
  );

  return { ...base, setValue };
}
