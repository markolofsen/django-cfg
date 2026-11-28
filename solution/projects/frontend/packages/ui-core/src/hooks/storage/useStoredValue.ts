'use client';

import { useCallback } from 'react';

import { useLocalStorage } from './useLocalStorage';
import type { StorageValidator } from './storage-decode';
import { useSessionStorage } from './useSessionStorage';

export type StorageType = 'local' | 'session';

export interface UseStoredValueOptions {
  /**
   * 'local' — persists across browser sessions (localStorage)
   * 'session' — cleared when tab is closed (sessionStorage)
   * @default 'local'
   */
  storage?: StorageType;
  /**
   * Time-to-live in milliseconds. After expiry, initialValue is returned.
   * @example ttl: 24 * 60 * 60 * 1000 // 24 hours
   */
  ttl?: number;
  /**
   * Owner for a bare `storageKey`. Default: nearest `StorageNamespaceProvider`, else `cfg`.
   * @see resolveStorageKey
   */
  namespace?: string;
  /** Accept a stored value only if this returns true; otherwise it is dropped and the initial value used. */
  validate?: StorageValidator<unknown>;
}

/**
 * Tuple returned by {@link useStoredValue}.
 *
 * The 4th element (`patch`) shallow-merges a subset of keys when `T` is a
 * plain object — see {@link useLocalStorage}. It is a no-op when no
 * `storageKey` is supplied.
 */
export type UseStoredValueReturn<T> = readonly [
  value: T,
  setValue: (value: T | ((prev: T) => T)) => void,
  removeValue: () => void,
  patch: (partial: Partial<T>) => void,
];

/**
 * Unified storage hook that delegates to useLocalStorage or useSessionStorage.
 *
 * Used by components (Input, Combobox, MultiSelect, Tabs, etc.) to add
 * optional persistence via a single `storageKey` prop.
 *
 * `storageKey` follows the storage-key scheme (see `./storage-namespace`): a full
 * `owner.area.name` key is used as is, a bare name lands under `<owner>.ui.<name>`.
 *
 * When storageKey is undefined the hook is a no-op:
 *   - returns initialValue as current value
 *   - setValue / removeValue / patch are no-ops
 * This means adding storageKey to a component has zero overhead when unused.
 *
 * @example
 * const [value, setValue, removeValue, patch] = useStoredValue('my-key', '', { storage: 'session' });
 */
export function useStoredValue<T>(
  storageKey: string | undefined,
  initialValue: T,
  options?: UseStoredValueOptions,
): UseStoredValueReturn<T> {
  const storageType = options?.storage ?? 'local';
  const ttlOption = { ttl: options?.ttl, namespace: options?.namespace, validate: options?.validate };

  // Both hooks are always called (rules of hooks — no conditional calls).
  // Only one of them is actually used depending on storageType.
  // When storageKey is undefined we pass a dummy key; the result is discarded.
  const dummyKey = 'cfg.ui.noop';

  const localResult = useLocalStorage<T>(
    storageType === 'local' && storageKey ? storageKey : dummyKey,
    initialValue,
    ttlOption,
  );

  const sessionResult = useSessionStorage<T>(
    storageType === 'session' && storageKey ? storageKey : dummyKey,
    initialValue,
    ttlOption,
  );

  const noopSetValue = useCallback((_value: T | ((prev: T) => T)) => {}, []);
  const noopRemove = useCallback(() => {}, []);
  const noopPatch = useCallback((_partial: Partial<T>) => {}, []);

  // No storageKey — pure no-op, no storage reads/writes
  if (!storageKey) {
    return [initialValue, noopSetValue, noopRemove, noopPatch] as const;
  }

  return storageType === 'local' ? localResult : sessionResult;
}
