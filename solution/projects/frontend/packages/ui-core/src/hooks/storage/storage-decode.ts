/**
 * Reading a stored value without trusting it.
 *
 * What sits in `localStorage` was written by an earlier build of the app, by
 * another tab, by a browser extension or by hand. A value of the wrong shape must
 * never reach a component: it is treated as absent, the key is healed (removed),
 * and the caller falls back to its initial value. Losing a stale preference is
 * always cheaper than crashing on it.
 *
 * Shared by `useLocalStorage` and `useSessionStorage`, so both heal the same way.
 */

interface StorageWrapper<T> {
  _meta: { createdAt: number; ttl: number };
  _value: T;
}

export type StorageValidator<T> = (value: unknown) => value is T;

function isWrapped<T>(data: unknown): data is StorageWrapper<T> {
  return (
    data !== null &&
    typeof data === 'object' &&
    '_meta' in data &&
    '_value' in data &&
    typeof (data as StorageWrapper<T>)._meta === 'object' &&
    typeof (data as StorageWrapper<T>)._meta.createdAt === 'number'
  );
}

function isPlainObject(v: unknown): v is Record<string, unknown> {
  return v !== null && typeof v === 'object' && !Array.isArray(v);
}

/**
 * Does `value` have the same shape as `initial`?
 *
 * - `null` / `undefined` initial: anything goes (the caller declared no shape).
 * - primitives: same `typeof`.
 * - arrays: an array.
 * - plain objects: an object whose keys that exist in both have the same
 *   `typeof` (an object field that was a string and is now a number is a stale
 *   shape). Keys missing from the stored value are fine: they are filled from
 *   `initial`, which is how a field added in a later release arrives.
 */
function conforms(value: unknown, initial: unknown): boolean {
  if (initial === null || initial === undefined) return true;
  if (Array.isArray(initial)) return Array.isArray(value);
  if (isPlainObject(initial)) {
    if (!isPlainObject(value)) return false;
    for (const key of Object.keys(initial)) {
      if (!(key in value)) continue;
      const a = initial[key];
      const b = value[key];
      if (a === null || a === undefined || b === null || b === undefined) continue;
      if (Array.isArray(a) !== Array.isArray(b)) return false;
      if (typeof a !== typeof b) return false;
    }
    return true;
  }
  return typeof value === typeof initial;
}

export type DecodeResult<T> = { ok: true; value: T } | { ok: false; reason: 'absent' | 'expired' | 'invalid' };

/**
 * Turn a raw stored string into a `T`, or say why not. Never throws.
 *
 * `bareStrings`: whether a non-JSON string is a valid stored string (the hooks that
 * write strings without quotes) or corruption (the hook that always JSON-encodes).
 *
 * `validate` replaces the shape check when a caller knows better (a union, an
 * enum, a range). It is guarded: a validator that throws counts as "invalid".
 */
export function decodeStored<T>(
  raw: string | null,
  initial: T,
  validate?: StorageValidator<T>,
  bareStrings = true,
): DecodeResult<T> {
  if (raw === null) return { ok: false, reason: 'absent' };

  let value: unknown;
  try {
    value = JSON.parse(raw);
  } catch {
    // Not JSON. Strings are stored bare, so for a string value this IS the value;
    // for anything else it is garbage and must not be cast into a `T`.
    value = bareStrings && typeof initial === 'string' ? raw : undefined;
    if (value === undefined) return { ok: false, reason: 'invalid' };
  }

  if (isWrapped<unknown>(value)) {
    const { createdAt, ttl } = value._meta;
    if (ttl && Date.now() - createdAt > ttl) return { ok: false, reason: 'expired' };
    value = value._value;
  }

  try {
    if (validate) return validate(value) ? { ok: true, value } : { ok: false, reason: 'invalid' };
    if (!conforms(value, initial)) return { ok: false, reason: 'invalid' };
  } catch {
    return { ok: false, reason: 'invalid' };
  }

  if (isPlainObject(initial) && isPlainObject(value) && !validate) {
    return { ok: true, value: { ...initial, ...value } as T };
  }
  return { ok: true, value: value as T };
}
