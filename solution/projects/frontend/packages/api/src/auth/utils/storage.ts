/**
 * Web Storage helpers shared by `useLocalStorage` and `useSessionStorage`.
 *
 * Both hooks carried byte-identical copies of `checkDataSize`, and the quota
 * check was written out four times — twice per hook, on write and on remove.
 * Every copy typed its caught error `any` and then read three properties off
 * it, which is exactly the read `unknown` makes you justify.
 */

import { authLogger } from './logger';

/** Per-item ceiling. Browsers cap the whole origin near 5MB. */
const MAX_ITEM_KB = 1024;

/**
 * Whether a caught error means the storage quota is full.
 *
 * Browsers disagree on how to say it: modern engines throw a `DOMException`
 * named `QuotaExceededError`, older WebKit used code 22, and some report it
 * only in the message. All three are checked because all three are still met
 * in the wild — and because the caller's response (drop old data, retry) is
 * the same for each.
 */
export function isQuotaExceededError(error: unknown): boolean {
  if (typeof error !== 'object' || error === null) return false;

  const { name, code, message } = error as {
    name?: unknown;
    code?: unknown;
    message?: unknown;
  };

  return (
    name === 'QuotaExceededError' ||
    code === 22 ||
    (typeof message === 'string' && message.includes('quota'))
  );
}

/**
 * Whether `data` serialises to something small enough to store.
 *
 * `unknown` rather than a type parameter: this only serialises, so it needs no
 * knowledge of the shape, and a parameter would invite callers to read one.
 * Returns false on a value that cannot be serialised at all — a circular
 * reference is not storable either, and the caller's response is identical.
 */
export function isWithinSizeLimit(data: unknown, key: string): boolean {
  try {
    const sizeInKB = new Blob([JSON.stringify(data)]).size / 1024;

    if (sizeInKB > MAX_ITEM_KB) {
      authLogger.warn(
        `Data size (${sizeInKB.toFixed(2)}KB) exceeds 1MB limit for key "${key}"`,
      );
      return false;
    }

    return true;
  } catch (error) {
    authLogger.error(`Error checking data size for key "${key}":`, error);
    return false;
  }
}
