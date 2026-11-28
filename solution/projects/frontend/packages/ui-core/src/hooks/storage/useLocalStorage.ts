'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import { isQuotaExceededError } from './storage-quota';
import { decodeStored, type StorageValidator } from './storage-decode';
import { evictableKeys, useResolvedStorageKey } from './storage-namespace';

/**
 * Storage wrapper format with metadata
 * Used when TTL is specified
 */
interface StorageWrapper<T> {
  _meta: {
    createdAt: number;
    ttl: number;
  };
  _value: T;
}

/**
 * Options for useLocalStorage hook
 */
export interface UseLocalStorageOptions {
  /**
   * Time-to-live in milliseconds.
   * After this time, value is considered expired and initialValue is returned.
   * Data is automatically cleaned up on next read.
   * @example 24 * 60 * 60 * 1000 // 24 hours
   */
  ttl?: number;
  /**
   * Owner for a bare key (`'sidebar-width'` → `<owner>.ui.sidebar_width`).
   * Default: the nearest `StorageNamespaceProvider`, else `cfg`.
   * A key that already follows `<owner>.<area>.<name>` is used as is.
   */
  namespace?: string;
  /**
   * Accept a stored value only if this returns true. Replaces the default shape
   * check (same `typeof` as the initial value, same keys for an object). A value
   * that fails is dropped, the key is removed and the initial value is used: a
   * stale or hand-edited entry can never reach the component.
   */
  validate?: StorageValidator<unknown>;
}

/**
 * Tuple returned by {@link useLocalStorage}.
 *
 * The 4th element (`patch`) is always present at runtime, but it only does
 * something useful when `T` is a plain object — for primitive `T` it falls
 * back to a plain `setValue` of the partial. See the `patch` JSDoc below.
 */
export type UseLocalStorageReturn<T> = readonly [
  value: T,
  setValue: (value: T | ((prev: T) => T)) => void,
  removeValue: () => void,
  patch: (partial: Partial<T>) => void,
];

/** True for a plain object (eligible for shallow-merge `patch`). */
function isPlainObject(v: unknown): v is Record<string, unknown> {
  return v !== null && typeof v === 'object' && !Array.isArray(v);
}

/**
 * Same-tab cross-instance pub/sub.
 *
 * `window`'s native `storage` event only fires in OTHER tabs — two
 * `useLocalStorage` hooks on the same key in the SAME tab would never see
 * each other's writes. This module-level registry closes that gap: every
 * write notifies all live hook instances for that key so they re-render
 * with the fresh value. Other-tab sync still rides the `storage` event.
 */
const keyListeners = new Map<string, Set<(raw: string | null) => void>>();

function subscribeKey(key: string, fn: (raw: string | null) => void): () => void {
  let set = keyListeners.get(key);
  if (!set) {
    set = new Set();
    keyListeners.set(key, set);
  }
  set.add(fn);
  return () => {
    set!.delete(fn);
    if (set!.size === 0) keyListeners.delete(key);
  };
}

/** Notify every same-tab hook instance bound to `key` (skips `self`). */
function broadcastKey(
  key: string,
  raw: string | null,
  self: (raw: string | null) => void,
): void {
  const set = keyListeners.get(key);
  if (!set) return;
  for (const fn of set) {
    if (fn !== self) fn(raw);
  }
}

/**
 * Simple localStorage hook with better error handling and optional TTL support.
 *
 * IMPORTANT: To prevent hydration mismatch, this hook:
 * - Always returns initialValue on first render (same as SSR)
 * - Reads from localStorage only after component mounts
 *
 * Synchronization (added):
 * - Same-tab: a module-level pub/sub keyed by storage key — two hooks on the
 *   same key in one tab stay in sync (the native `storage` event does NOT
 *   fire in the originating tab, so this is required).
 * - Cross-tab: the `window` `storage` event keeps other tabs in sync.
 *
 * Write coalescing (added):
 * - State updates synchronously (React stays consistent within the tick),
 *   but the actual `localStorage.setItem` is flushed once via
 *   `queueMicrotask`. N `patch`/`setValue` calls in one tick collapse into a
 *   single write + a single broadcast — no localStorage thrash, no storm of
 *   `storage` events.
 *
 * @param key - Storage key
 * @param initialValue - Default value if key doesn't exist
 * @param options - Optional configuration (ttl for auto-expiration)
 * @returns `[value, setValue, removeValue, patch]`
 *   - `patch(partial)` shallow-merges a subset of keys into an object value.
 *     It is a NO-OP when the partial changes nothing (shallow-equal on the
 *     touched keys) — no write, no re-render, no `storage` event.
 *
 * @example
 * // Without TTL (backwards compatible)
 * const [value, setValue] = useLocalStorage('key', 'default');
 *
 * @example
 * // With TTL (24 hours)
 * const [value, setValue] = useLocalStorage('key', 'default', {
 *   ttl: 24 * 60 * 60 * 1000
 * });
 *
 * @example
 * // Partial / grouped updates on an object value
 * const [prefs, , , patch] = useLocalStorage('prefs', { a: 1, b: 2 });
 * patch({ b: 3 }); // merges → { a: 1, b: 3 }, only writes if it changed
 */
export function useLocalStorage<T>(
  keyInput: string,
  initialValue: T,
  options?: UseLocalStorageOptions
): UseLocalStorageReturn<T> {
  const key = useResolvedStorageKey(keyInput, options?.namespace);
  const ttl = options?.ttl;
  // Always start with initialValue to match SSR
  const [storedValue, setStoredValue] = useState<T>(initialValue);
  const [_isHydrated, setIsHydrated] = useState(false);
  const isInitialized = useRef(false);

  // Latest value, readable synchronously by setValue/patch updaters without
  // adding them to dependency arrays (avoids stale closures across coalesced
  // calls in the same tick).
  const valueRef = useRef<T>(initialValue);
  valueRef.current = storedValue;

  // Pending write: the value to flush to localStorage at the next microtask.
  // `hasPending` guards against scheduling more than one flush per tick.
  const pendingRef = useRef<{ value: T } | null>(null);
  const flushScheduledRef = useRef(false);

  /**
   * Parse a raw localStorage string into a value of T, honoring TTL.
   * Returns `{ value }` or `null` when the entry is absent / expired.
   */
  const validate = options?.validate as StorageValidator<T> | undefined;
  const validateRef = useRef(validate);
  validateRef.current = validate;
  const initialForParse = useRef<T>(initialValue);
  initialForParse.current = initialValue;

  const parseRaw = useCallback(
    (raw: string | null): { value: T } | null => {
      if (raw === null) return null;
      const decoded = decodeStored<T>(raw, initialForParse.current, validateRef.current);
      if (decoded.ok) return { value: decoded.value };
      // Expired or not what we expect: heal the key so the next read is clean.
      try {
        window.localStorage.removeItem(key);
      } catch {
        // ignore
      }
      return null;
    },
    [key],
  );

  // Read from localStorage after mount (avoids hydration mismatch)
  useEffect(() => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    try {
      const item = window.localStorage.getItem(key);
      const parsed = parseRaw(item);
      if (parsed) setStoredValue(parsed.value);
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
    }

    setIsHydrated(true);
  }, [key, parseRaw]);

  // Identity used to skip self when broadcasting. The sync effect below owns
  // the real listener; this ref just lets `broadcastKey` exclude it.
  const onLocalRef = useRef<(raw: string | null) => void>(() => {});

  // Latest initialValue, read by the sync listener for the removal fallback
  // without making the effect re-subscribe on every inline-literal render.
  const initialValueRef = useRef<T>(initialValue);
  initialValueRef.current = initialValue;

  // Cross-instance (same tab) + cross-tab sync.
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Same-tab: re-read whenever a sibling hook on this key writes.
    // The native `storage` event does NOT fire in the originating tab, so
    // without this two hooks on one key in one tab would drift apart.
    const onLocal = (raw: string | null) => {
      const parsed = parseRaw(raw);
      setStoredValue(parsed ? parsed.value : initialValueRef.current);
    };
    onLocalRef.current = onLocal;
    const unsubscribe = subscribeKey(key, onLocal);

    // Other tabs: the native `storage` event (never fires in this tab).
    const onStorage = (e: StorageEvent) => {
      if (e.key !== key || e.storageArea !== window.localStorage) return;
      const parsed = parseRaw(e.newValue);
      setStoredValue(parsed ? parsed.value : initialValueRef.current);
    };
    window.addEventListener('storage', onStorage);

    return () => {
      unsubscribe();
      window.removeEventListener('storage', onStorage);
    };
  }, [key, parseRaw]);

  // Check data size and limit
  const checkDataSize = (data: unknown): boolean => {
    try {
      const jsonString = JSON.stringify(data);
      const sizeInBytes = new Blob([jsonString]).size;
      const sizeInKB = sizeInBytes / 1024;

      // Limit to 1MB per item
      if (sizeInKB > 1024) {
        console.warn(`Data size (${sizeInKB.toFixed(2)}KB) exceeds 1MB limit for key "${key}"`);
        return false;
      }

      return true;
    } catch (error) {
      console.error(`Error checking data size for key "${key}":`, error);
      return false;
    }
  };

  // Clear old data when localStorage is full
  // Drop evictable keys (our scheme, non-personal) when the quota is full.
  // Tokens, drafts and third-party keys are never touched.
  const evict = (fraction: number) => {
    try {
      const names = evictableKeys(window.localStorage).filter((name) => name !== key);
      const count = fraction >= 1 ? names.length : Math.ceil(names.length * fraction);
      for (const name of names.slice(0, count)) {
        try {
          window.localStorage.removeItem(name);
        } catch {
          // Ignore errors when removing items
        }
      }
    } catch (error) {
      console.error('Error clearing old localStorage data:', error);
    }
  };
  const clearOldData = () => evict(0.2);
  const forceClearAll = () => evict(1);

  // Prepare data for storage (with or without TTL wrapper)
  const prepareForStorage = (value: T): string => {
    if (ttl) {
      // Wrap with _meta for TTL support
      const wrapped: StorageWrapper<T> = {
        _meta: {
          createdAt: Date.now(),
          ttl,
        },
        _value: value,
      };
      return JSON.stringify(wrapped);
    }
    // Old format (no wrapper) - for strings, store directly
    if (typeof value === 'string') {
      return value;
    }
    return JSON.stringify(value);
  };

  // Low-level write: persist `dataToStore`, with quota recovery. Returns the
  // raw string actually written (so siblings can be notified with it).
  const writeRaw = useCallback(
    (dataToStore: string): void => {
      try {
        window.localStorage.setItem(key, dataToStore);
      } catch (storageError) {
        if (isQuotaExceededError(storageError)) {
          console.warn('localStorage quota exceeded, clearing old data...');
          clearOldData();
          try {
            window.localStorage.setItem(key, dataToStore);
          } catch (retryError) {
            console.error(
              `Failed to set localStorage key "${key}" after clearing old data:`,
              retryError,
            );
            try {
              forceClearAll();
              window.localStorage.setItem(key, dataToStore);
            } catch (finalError) {
              console.error(
                `Failed to set localStorage key "${key}" after force clearing:`,
                finalError,
              );
            }
          }
        } else {
          throw storageError;
        }
      }
    },
    [key],
  );

  /**
   * Schedule a single coalesced flush of the pending value to localStorage.
   *
   * Why: a feature may fire several `patch`/`setValue` calls in one tick.
   * State is updated immediately (React stays correct), but the I/O —
   * `setItem` + the cross-instance broadcast — is deferred to a microtask
   * so N updates in one tick become exactly ONE write and ONE broadcast.
   */
  const scheduleFlush = useCallback(() => {
    if (flushScheduledRef.current) return;
    flushScheduledRef.current = true;

    queueMicrotask(() => {
      flushScheduledRef.current = false;
      const pending = pendingRef.current;
      pendingRef.current = null;
      if (!pending) return;
      if (typeof window === 'undefined') return;

      if (!checkDataSize(pending.value)) {
        console.warn(`Data size too large for key "${key}", removing key`);
        try {
          window.localStorage.removeItem(key);
        } catch {
          // ignore
        }
        broadcastKey(key, null, onLocalRef.current);
        return;
      }

      const dataToStore = prepareForStorage(pending.value);
      try {
        writeRaw(dataToStore);
        // Keep sibling hooks on this key in sync within the same tab.
        broadcastKey(key, dataToStore, onLocalRef.current);
      } catch (error) {
        console.error(`Error setting localStorage key "${key}":`, error);
      }
    });
    // prepareForStorage / checkDataSize close over `ttl` + `key`; both stable
    // enough for this callback's purpose.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, writeRaw]);

  // Commit a new value: update React state now, queue the write.
  const commit = useCallback(
    (next: T) => {
      setStoredValue(next);
      valueRef.current = next;
      pendingRef.current = { value: next };
      scheduleFlush();
    },
    [scheduleFlush],
  );

  // Update localStorage when value changes
  const setValue = useCallback(
    (value: T | ((val: T) => T)) => {
      const next =
        value instanceof Function ? value(valueRef.current) : value;
      commit(next);
    },
    [commit],
  );

  /**
   * Shallow-merge a subset of keys into an object value.
   *
   * Safe by design: when every key in `partial` already equals the stored
   * value (shallow `Object.is` check) this is a NO-OP — no state update, no
   * write, no `storage` event, no re-render. This makes it cheap to call
   * `patch` defensively from effects / event handlers.
   *
   * When the current value is not a plain object, `patch` degrades to a
   * plain `setValue(partial as T)` so the call is still well-defined.
   */
  const patch = useCallback(
    (partial: Partial<T>) => {
      const prev = valueRef.current;

      if (!isPlainObject(prev)) {
        commit(partial as T);
        return;
      }

      // Skip the write entirely when nothing actually changes.
      let changed = false;
      for (const k of Object.keys(partial) as Array<keyof T>) {
        if (!Object.is((prev as T)[k], partial[k])) {
          changed = true;
          break;
        }
      }
      if (!changed) return;

      commit({ ...prev, ...partial } as T);
    },
    [commit],
  );

  // Remove value from localStorage
  const removeValue = useCallback(() => {
    try {
      setStoredValue(initialValue);
      valueRef.current = initialValue;
      // Drop any queued write — it would resurrect the removed entry.
      pendingRef.current = null;
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.removeItem(key);
        } catch (removeError) {
          if (isQuotaExceededError(removeError)) {
            console.warn('localStorage quota exceeded during removal, clearing old data...');
            clearOldData();
            try {
              window.localStorage.removeItem(key);
            } catch (retryError) {
              console.error(
                `Failed to remove localStorage key "${key}" after clearing:`,
                retryError,
              );
              forceClearAll();
            }
          } else {
            throw removeError;
          }
        }
        broadcastKey(key, null, onLocalRef.current);
      }
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
    // `initialValue` excluded for the inline-literal reason above.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return [storedValue, setValue, removeValue, patch] as const;
}
