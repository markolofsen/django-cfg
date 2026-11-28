/**
 * Where generated operations, the token refresh and the profile guard send requests: one resolver (H0.4).
 *
 * Next.js replaces only the literal text `process.env.NEXT_PUBLIC_NAME` when it builds a page, in every module it
 * compiles, `node_modules` included. Any other read (`globalThis.process.env`, an aliased `process.env`, a read
 * by name) is empty in the browser. So each variable below is read in exactly that literal form, inside its own
 * `try` (where nothing inlined it and `process` does not exist, the read throws), at call time.
 *
 * Browser (`document` exists):
 * 1. an explicit `configureApi` / `setApiOrigin` value;
 * 2. `NEXT_PUBLIC_STATIC_BUILD === 'true'`: same-origin relative;
 * 3. `NEXT_PUBLIC_API_PROXY_URL` when defined at all: its value, and `''` means same-origin relative;
 * 4. `NEXT_PUBLIC_API_URL`;
 * 5. `allowRelative: true`: same-origin relative.
 *
 * Server (no `document`): an explicit absolute value, else `NEXT_PUBLIC_API_URL`. The server never uses the proxy
 * or a relative base: it would be a round trip to itself, and Node's `fetch` cannot take a relative URL.
 *
 * `origin: 'direct'` on a request resolves like the server: it skips the proxy, the static mode and any relative
 * explicit value.
 *
 * Relative modes count as configured. Only when nothing resolves does a request fail with
 * `APIConfigurationError`, before `fetch`, instead of silently going to the page's own origin.
 */

import { APIConfigurationError } from './errors';
import { apiOriginSlot } from './state';

export interface ApiRuntimeConfig {
  /**
   * The API origin: an absolute http(s) URL (`https://api.example.com`, a path prefix is kept), or a same-origin
   * path prefix (`/apix`; `/` for the page origin itself). `null` or `''` clears an earlier value, so the
   * environment decides again. An invalid value is ignored with one console warning.
   */
  apiUrl?: string | null;
  /** Fall back to same-origin relative requests when nothing else is configured. */
  allowRelative?: boolean;
}

export type ApiOriginMode = 'explicit' | 'static' | 'proxy' | 'env' | 'relative';

export interface ApiOriginResolution {
  /** Prepended to the operation path: an absolute origin, a same-origin prefix such as `/apix`, or `''`. */
  base: string;
  mode: ApiOriginMode;
}

export interface ResolveApiOptions {
  /** `'direct'`: skip the proxy, the static mode and relative explicit values; use the API host. */
  origin?: 'direct';
}

const ABSOLUTE = /^https?:\/\//i;

const readApiUrl = (): string | undefined => {
  try { return process.env.NEXT_PUBLIC_API_URL; } catch { return undefined; }
};
const readProxyUrl = (): string | undefined => {
  try { return process.env.NEXT_PUBLIC_API_PROXY_URL; } catch { return undefined; }
};
const readStaticBuild = (): boolean => {
  try { return process.env.NEXT_PUBLIC_STATIC_BUILD === 'true'; } catch { return false; }
};

const isBrowser = (): boolean => typeof document !== 'undefined';

/**
 * Normalize an API origin. Returns an absolute http(s) URL without query, hash or trailing slash (a path prefix is
 * kept), a same-origin prefix without trailing slash (`/apix`, or `''` for `/`), or `null` when the value is empty
 * or not one of those. Never throws.
 */
export function normalizeApiOrigin(origin: string | null | undefined): string | null {
  const value = typeof origin === 'string' ? origin.trim() : '';
  if (!value) return null;
  if (value.startsWith('/') && !value.startsWith('//')) {
    return value.split(/[?#]/, 1)[0]!.replace(/\/+$/, '');
  }
  if (!ABSOLUTE.test(value)) return null;
  try {
    const parsed = new URL(value);
    parsed.search = '';
    parsed.hash = '';
    return parsed.toString().replace(/\/+$/, '');
  } catch {
    return null;
  }
}

const warnInvalid = (value: unknown, source: string): void => {
  const slot = apiOriginSlot();
  const key = `${source}:${String(value)}`;
  const warned = slot.warned ?? (slot.warned = []);
  if (warned.includes(key)) return;
  warned.push(key);
  try {
    console.warn(
      `[@djangocfg/api] ${source}: ignoring API origin ${JSON.stringify(value)}. `
      + 'Use an absolute http(s) URL or a same-origin path such as "/apix".',
    );
  } catch {
    // A console that throws must not break rendering.
  }
};

/** Store an explicit origin. Never throws: an invalid value warns once and leaves the previous one. */
const setExplicit = (value: string | null, source: string): void => {
  const slot = apiOriginSlot();
  if (value === null || (typeof value === 'string' && !value.trim())) {
    slot.origin = undefined;
    return;
  }
  const normalized = typeof value === 'string' ? normalizeApiOrigin(value) : null;
  if (normalized === null) {
    warnInvalid(value, source);
    return;
  }
  slot.origin = normalized;
};

/** The explicit origin, or `undefined` when none is set (`null` from an older copy of the slot counts as none). */
const explicitOrigin = (): string | undefined => {
  const origin = apiOriginSlot().origin;
  return typeof origin === 'string' ? origin : undefined;
};

const resolveDirect = (explicit: string | undefined): ApiOriginResolution | null => {
  if (explicit !== undefined && ABSOLUTE.test(explicit)) return { base: explicit, mode: 'explicit' };
  const env = normalizeApiOrigin(readApiUrl());
  if (env !== null && ABSOLUTE.test(env)) return { base: env, mode: 'env' };
  return null;
};

/** Resolve where a request goes. `null` means nothing is configured for it. */
export function resolveApiOrigin(options: ResolveApiOptions = {}): ApiOriginResolution | null {
  const explicit = explicitOrigin();
  if (options.origin === 'direct' || !isBrowser()) return resolveDirect(explicit);

  if (explicit !== undefined) return { base: explicit, mode: 'explicit' };
  if (readStaticBuild()) return { base: '', mode: 'static' };
  const proxy = readProxyUrl();
  if (proxy !== undefined) {
    if (!proxy.trim()) return { base: '', mode: 'proxy' };
    const normalized = normalizeApiOrigin(proxy);
    if (normalized !== null) return { base: normalized, mode: 'proxy' };
    warnInvalid(proxy, 'NEXT_PUBLIC_API_PROXY_URL');
  }
  const env = normalizeApiOrigin(readApiUrl());
  if (env !== null) return { base: env, mode: 'env' };
  if (apiOriginSlot().allowRelative === true) return { base: '', mode: 'relative' };
  return null;
}

/** Configure the generated client runtime for the current application. Safe to call during render. */
export function configureApi(config: ApiRuntimeConfig = {}): string | null {
  try {
    if (config.apiUrl !== undefined) setExplicit(config.apiUrl, 'configureApi');
    if (typeof config.allowRelative === 'boolean') apiOriginSlot().allowRelative = config.allowRelative;
  } catch {
    // Configuration is advisory: it never takes the page down.
  }
  return getApiOrigin();
}

/** Set an explicit API origin; `null` or `''` clears it. Never throws. */
export function setApiOrigin(origin: string | null): string | null {
  try {
    setExplicit(origin, 'setApiOrigin');
  } catch {
    // See configureApi.
  }
  return getApiOrigin();
}

/** The base requests go to (`''` = same-origin relative), or `null` when nothing is configured. */
export function getApiOrigin(options?: ResolveApiOptions): string | null {
  return resolveApiOrigin(options)?.base ?? null;
}

/** Whether generated operations can run: an origin or a relative mode is configured. */
export function hasApiOrigin(options?: ResolveApiOptions): boolean {
  return resolveApiOrigin(options) !== null;
}

/** Whether same-origin relative requests were explicitly enabled as a fallback (`allowRelative`). */
export function allowsRelativeApiUrl(): boolean {
  return apiOriginSlot().allowRelative === true;
}

/** Resolve a generated relative operation path into the URL to fetch. */
export function resolveApiUrl(url: string, options?: ResolveApiOptions): string {
  if (ABSOLUTE.test(url)) return url;
  const resolved = resolveApiOrigin(options);
  if (resolved === null) {
    throw new APIConfigurationError(
      options?.origin === 'direct'
        ? 'API origin is not configured for a direct request. Set NEXT_PUBLIC_API_URL or call configureApi({ apiUrl }) with an absolute URL.'
        : 'API origin is not configured. Pass apiUrl to AuthProvider or call configureApi({ apiUrl }) before making requests.',
    );
  }
  return `${resolved.base}${url.startsWith('/') ? url : `/${url}`}`;
}
