'use client';

import { useState } from 'react';

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
 * Options for useSessionStorage hook
 */
export interface UseSessionStorageOptions {
  /**
   * Time-to-live in milliseconds.
   * After this time, value is considered expired and initialValue is returned.
   * Data is automatically cleaned up on next read.
   * @example 24 * 60 * 60 * 1000 // 24 hours
   */
  ttl?: number;
  /**
   * Owner for a bare key (`'wizard-step'` → `<owner>.ui.wizard_step`).
   * Default: the nearest `StorageNamespaceProvider`, else `cfg`.
   * A key that already follows `<owner>.<area>.<name>` is used as is.
   */
  namespace?: string;
  /**
   * Accept a stored value only if this returns true; otherwise the key is
   * removed and the initial value is used. Replaces the default shape check.
   */
  validate?: StorageValidator<unknown>;
}

/**
 * Tuple returned by {@link useSessionStorage}.
 *
 * The 4th element (`patch`) shallow-merges a subset of keys when `T` is a
 * plain object — a no-op when nothing changes. Mirrors `useLocalStorage`.
 */
export type UseSessionStorageReturn<T> = readonly [
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
 * Simple sessionStorage hook with better error handling and optional TTL support
 *
 * @param key - Storage key
 * @param initialValue - Default value if key doesn't exist
 * @param options - Optional configuration (ttl for auto-expiration)
 * @returns [value, setValue, removeValue] - Current value, setter function, and remove function
 *
 * @example
 * // Without TTL (backwards compatible)
 * const [value, setValue] = useSessionStorage('key', 'default');
 *
 * @example
 * // With TTL (1 hour)
 * const [value, setValue] = useSessionStorage('key', 'default', {
 *   ttl: 60 * 60 * 1000
 * });
 */
export function useSessionStorage<T>(
  keyInput: string,
  initialValue: T,
  options?: UseSessionStorageOptions
): UseSessionStorageReturn<T> {
  const key = useResolvedStorageKey(keyInput, options?.namespace);
  const ttl = options?.ttl;

  // Get initial value from sessionStorage or use provided initialValue
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.sessionStorage.getItem(key);
      if (item === null) return initialValue;

      const decoded = decodeStored<T>(item, initialValue, options?.validate as StorageValidator<T> | undefined);
      if (decoded.ok) return decoded.value;
      // Expired or not what we expect: heal the key and start from the initial value.
      window.sessionStorage.removeItem(key);
      return initialValue;
    } catch (error) {
      console.error(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

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

  // Drop evictable keys (our scheme, non-personal) when the quota is full.
  // Tokens, drafts and third-party keys are never touched.
  const evict = (fraction: number) => {
    try {
      const names = evictableKeys(window.sessionStorage).filter((name) => name !== key);
      const count = fraction >= 1 ? names.length : Math.ceil(names.length * fraction);
      for (const name of names.slice(0, count)) {
        try {
          window.sessionStorage.removeItem(name);
        } catch {
          // Ignore errors when removing items
        }
      }
    } catch (error) {
      console.error('Error clearing old sessionStorage data:', error);
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

  // Update sessionStorage when value changes
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;

      // Check data size before attempting to save
      if (!checkDataSize(valueToStore)) {
        console.warn(`Data size too large for key "${key}", removing key`);
        // Remove the key if data is too large
        try {
          window.sessionStorage.removeItem(key);
        } catch {
          // Ignore errors when removing
        }
        // Still update the state
        setStoredValue(valueToStore);
        return;
      }

      setStoredValue(valueToStore);

      if (typeof window !== 'undefined') {
        const dataToStore = prepareForStorage(valueToStore);

        // Try to set the value
        try {
          window.sessionStorage.setItem(key, dataToStore);
        } catch (storageError) {
          // If quota exceeded, clear old data and try again
          if (isQuotaExceededError(storageError)) {
            console.warn('sessionStorage quota exceeded, clearing old data...');
            clearOldData();

            // Try again after clearing
            try {
              window.sessionStorage.setItem(key, dataToStore);
            } catch (retryError) {
              console.error(`Failed to set sessionStorage key "${key}" after clearing old data:`, retryError);
              // If still fails, force clear all and try one more time
              try {
                forceClearAll();
                window.sessionStorage.setItem(key, dataToStore);
              } catch (finalError) {
                console.error(`Failed to set sessionStorage key "${key}" after force clearing:`, finalError);
                // If still fails, just update the state without sessionStorage
                setStoredValue(valueToStore);
              }
            }
          } else {
            throw storageError;
          }
        }
      }
    } catch (error) {
      console.error(`Error setting sessionStorage key "${key}":`, error);
      // Still update the state even if sessionStorage fails
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
    }
  };

  // Remove value from sessionStorage
  const removeValue = () => {
    try {
      setStoredValue(initialValue);
      if (typeof window !== 'undefined') {
        try {
          window.sessionStorage.removeItem(key);
        } catch (removeError) {
          // If removal fails due to quota, try to clear some data first
          if (isQuotaExceededError(removeError)) {
            console.warn('sessionStorage quota exceeded during removal, clearing old data...');
            clearOldData();

            try {
              window.sessionStorage.removeItem(key);
            } catch (retryError) {
              console.error(`Failed to remove sessionStorage key "${key}" after clearing:`, retryError);
              // If still fails, force clear all
              forceClearAll();
            }
          } else {
            throw removeError;
          }
        }
      }
    } catch (error) {
      console.error(`Error removing sessionStorage key "${key}":`, error);
    }
  };

  /**
   * Shallow-merge a subset of keys into an object value.
   *
   * Safe by design: a NO-OP when the partial changes nothing (shallow
   * `Object.is` check on the touched keys) — no write, no re-render. When
   * the current value is not a plain object it degrades to `setValue`.
   */
  const patch = (partial: Partial<T>) => {
    const prev = storedValue;
    if (!isPlainObject(prev)) {
      setValue(partial as T);
      return;
    }
    let changed = false;
    for (const k of Object.keys(partial) as Array<keyof T>) {
      if (!Object.is((prev as T)[k], partial[k])) {
        changed = true;
        break;
      }
    }
    if (!changed) return;
    setValue({ ...prev, ...partial } as T);
  };

  return [storedValue, setValue, removeValue, patch] as const;
}
