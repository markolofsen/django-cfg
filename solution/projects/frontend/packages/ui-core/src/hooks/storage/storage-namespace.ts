'use client';

/**
 * Storage namespaces for the state hooks.
 *
 * Every key we write to the browser follows one scheme (full rules:
 * `@djangocfg/api` → `@docs/STORAGE_KEYS.md`):
 *
 *   `<owner>.<area>.<name>[.<id>]`   e.g. `cfg.ui.sidebar_width`, `kino.player.volume`
 *
 * The hooks (`useLocalStorage`, `useSessionStorage`, `useStoredValue`) enforce
 * it by resolving the key you pass:
 *
 *   1. A key that already follows the scheme (`kino.player.volume`) is used as is.
 *   2. A bare name (`sidebar-width`, `Last Volume`) is folded to `snake_case` and
 *      placed under the active namespace: `<owner>.ui.sidebar_width`.
 *
 * The active owner is, in order: the hook's `namespace` option, the nearest
 * `<StorageNamespaceProvider owner="…">`, then `cfg` (the framework default).
 * An app sets its owner once at the root and forgets about it.
 */

import { createContext, createElement, useContext, type ReactNode } from 'react';
import {
  CFG_FAMILIES,
  CFG_KEYS,
  createStorage,
  normalizeSegment,
  type GuardedStorage,
} from '@djangocfg/api/storage';

/** The framework's owner. Used when nothing else is declared. */
export const DEFAULT_STORAGE_NAMESPACE = 'cfg';

/** Area given to a bare key. Hook-level state is UI state unless the caller names the area. */
export const DEFAULT_STORAGE_AREA = 'ui';

const OWNER_RE = /^[a-z][a-z0-9_]*$/;
const SCHEME_RE = /^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$/;

const NamespaceContext = createContext<string>(DEFAULT_STORAGE_NAMESPACE);

export interface StorageNamespaceProviderProps {
  /** Short lower-case owner for every key written below: `kino`, `mls`, `crm`. */
  owner: string;
  children?: ReactNode;
}

/**
 * Declares the owner of every bare storage key in the subtree.
 * Place it once, near the root of an app.
 */
export function StorageNamespaceProvider({ owner, children }: StorageNamespaceProviderProps) {
  if (!OWNER_RE.test(owner)) {
    throw new TypeError(`StorageNamespaceProvider: owner "${owner}" must match ${OWNER_RE}`);
  }
  return createElement(NamespaceContext.Provider, { value: owner }, children);
}

/** The owner the hooks use here (the provider's, or `cfg`). */
export function useStorageNamespace(): string {
  return useContext(NamespaceContext);
}

/** True when `key` already follows `<owner>.<area>.<name>`. */
export function isSchemeKey(key: string): boolean {
  return SCHEME_RE.test(key);
}

/**
 * Pure resolver behind the hooks: scheme keys pass through, bare names are
 * folded and prefixed with `<owner>.ui.`. Throws when nothing usable is left.
 */
export function resolveStorageKey(key: string, owner: string = DEFAULT_STORAGE_NAMESPACE): string {
  if (isSchemeKey(key)) return key;
  const name = normalizeSegment(key);
  if (!name) throw new TypeError(`storage key "${key}" is empty after normalisation`);
  return `${owner}.${DEFAULT_STORAGE_AREA}.${name}`;
}

/** Hook form: owner = option → provider → `cfg`. */
export function useResolvedStorageKey(key: string, namespace?: string): string {
  const fromContext = useStorageNamespace();
  return resolveStorageKey(key, namespace ?? fromContext);
}

// ---- eviction (shared by the quota-recovery paths of the hooks) -------------

const PERSONAL_KEYS: Set<string> = new Set(
  Object.values(CFG_KEYS)
    .filter((spec) => spec.personal)
    .map((spec) => spec.key),
);
const PERSONAL_PREFIXES = Object.values(CFG_FAMILIES)
  .filter((spec) => spec.personal)
  .map((spec) => spec.prefix);

/**
 * May the quota-recovery code drop this key? Only keys that follow our scheme
 * and are not personal (tokens, profile, drafts). Third-party keys such as
 * `NEXT_LOCALE` and everything signed-in-user related are never evicted.
 */
export function isEvictableKey(key: string): boolean {
  if (!isSchemeKey(key)) return false;
  if (key.startsWith('cfg.auth.') || PERSONAL_KEYS.has(key)) return false;
  return !PERSONAL_PREFIXES.some((prefix) => key.startsWith(prefix));
}

/** Names in `storage` that the quota recovery is allowed to remove. */
export function evictableKeys(storage: Storage): string[] {
  const out: string[] = [];
  for (let i = 0; i < storage.length; i += 1) {
    const name = storage.key(i);
    if (name && isEvictableKey(name)) out.push(name);
  }
  return out;
}

// ---- inspection / reset ------------------------------------------------------

export type StorageArea = 'local' | 'session';

function nativeArea(area: StorageArea): Storage | null {
  if (typeof window === 'undefined') return null;
  try {
    return area === 'session' ? window.sessionStorage : window.localStorage;
  } catch {
    return null;
  }
}

/** Every key an owner holds in one store (`cfg` by default). */
export function listStorageKeys(owner: string = DEFAULT_STORAGE_NAMESPACE, area: StorageArea = 'local'): string[] {
  const native = nativeArea(area);
  if (!native) return [];
  const prefix = `${owner}.`;
  const out: string[] = [];
  for (let i = 0; i < native.length; i += 1) {
    const name = native.key(i);
    if (name?.startsWith(prefix)) out.push(name);
  }
  return out.sort();
}

export interface ClearStorageOptions {
  /** Store to clear. Default: both. */
  area?: StorageArea;
  /** Also remove personal keys (tokens, profile, drafts). Default false: preferences only. */
  includePersonal?: boolean;
}

/**
 * Removes the keys of one owner. By default personal keys survive, so a
 * "reset preferences" button never signs the user out.
 * Hooks mounted on a removed key keep their in-memory value until they write.
 */
export function clearStorageNamespace(
  owner: string = DEFAULT_STORAGE_NAMESPACE,
  { area, includePersonal = false }: ClearStorageOptions = {},
): string[] {
  const areas: StorageArea[] = area ? [area] : ['local', 'session'];
  const removed: string[] = [];
  for (const a of areas) {
    const native = nativeArea(a);
    if (!native) continue;
    for (const name of listStorageKeys(owner, a)) {
      if (!includePersonal && owner === DEFAULT_STORAGE_NAMESPACE && !isEvictableKey(name)) continue;
      try {
        native.removeItem(name);
        removed.push(name);
      } catch {
        /* ignore */
      }
    }
  }
  return removed;
}

// ---- an app's namespace -------------------------------------------------------

export interface StorageNamespace {
  readonly owner: string;
  /** `kino.player.volume` from `('player', 'volume')`; parts are folded to snake_case. */
  key(...parts: string[]): string;
  /** Guarded non-React access (`read`, `write`, `readJSON`, `onChange`, `clearAll`…). */
  readonly storage: GuardedStorage;
  keys(area?: StorageArea): string[];
  clear(options?: ClearStorageOptions): string[];
}

/**
 * Declares an app's namespace in one place:
 *
 * ```ts
 * // lib/storage.ts
 * export const kinoStorage = createStorageNamespace('kino');
 * export const PLAYER_VOLUME = kinoStorage.key('player', 'volume'); // kino.player.volume
 *
 * // component
 * const [volume, setVolume] = useLocalStorage(PLAYER_VOLUME, 1);
 * ```
 *
 * and wraps the app root in `<StorageNamespaceProvider owner="kino">` so bare
 * `storageKey` props on ui-core components land under `kino.ui.*`.
 */
export function createStorageNamespace(owner: string): StorageNamespace {
  const storage = createStorage(owner);
  return {
    owner,
    key: (...parts) => storage.key(...parts),
    storage,
    keys: (area = 'local') => listStorageKeys(owner, area),
    clear: (options) => clearStorageNamespace(owner, options),
  };
}
