'use client';

import { useCallback, useState } from 'react';

import { cfgStorage, type KeySpec } from '../../storage';

/**
 * One framework-owned string in browser storage, as React state.
 *
 * Reads and writes go through `cfgStorage` (the key registry): a blocked or full
 * storage never throws, the page keeps the value in memory until reload, and a
 * key outside the registry cannot be written. It replaces two hand-rolled
 * storage hooks that did their own quota handling, one of which could empty the
 * whole `localStorage` of the origin.
 *
 * The state is a mirror: whoever needs the latest value across components reads
 * `cfgStorage` directly (the redirect manager does).
 *
 * `json: true` for a key whose stored form is a JSON string (the redirect URL is
 * written that way and read by code outside React); the default is the bare string.
 *
 * @example
 * const [email, setEmail, clearEmail] = useCfgStored(CFG_KEYS.email);
 */
export function useCfgStored(spec: KeySpec, options: { json?: boolean } = {}) {
  const json = options.json === true;
  const [value, setValue] = useState<string | null>(() => {
    if (typeof window === 'undefined') return null;
    if (!json) return cfgStorage.read(spec.key, spec.store);
    const parsed = cfgStorage.readJSON<unknown>(spec.key, spec.store);
    return typeof parsed === 'string' ? parsed : null;
  });

  const set = useCallback(
    (next: string) => {
      if (json) cfgStorage.writeJSON(spec.key, next, spec.store);
      else cfgStorage.write(spec.key, next, spec.store);
      setValue(next);
    },
    [spec.key, spec.store, json],
  );

  const clear = useCallback(() => {
    cfgStorage.remove(spec.key, spec.store);
    setValue(null);
  }, [spec.key, spec.store]);

  return [value, set, clear] as const;
}
