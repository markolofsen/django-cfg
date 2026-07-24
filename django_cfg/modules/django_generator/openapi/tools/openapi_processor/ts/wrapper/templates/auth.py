"""Global auth store + Hey API interceptor installer.

Single source of truth for Bearer token, X-API-Key, Accept-Language,
baseUrl. Exposes `installAuthOnClient(client)` — called by `client.gen.ts`
synchronously right after `createClient()` (post-processed). No circular
import: `auth.ts` does NOT import `client.gen`.

Two render modes (selected per target via `auth_mode`):
  • `render_auth_ts` (jwt, default) — full store: token storage, reactive
    session snapshot (`getSnapshot`/`subscribe` for useSyncExternalStore),
    single write path (`setSession`), cross-store Web-Locks refresh,
    auto-registered refresh handler, terminal-401 `onSessionExpired`, DPoP.
  • `render_auth_public_ts` (public) — token-free minimal store for clients
    that only call public endpoints (no Authorization, no refresh, no DPoP).

Storage modes (jwt store only):
  • 'localStorage' (default) — JS-readable, simple, survives reload.
  • 'sessionStorage'         — JS-readable, cleared when the browser session ends.
  • 'cookie'                 — JS-readable cookie (NOT HttpOnly).
                               Useful when you need SSR to see the
                               token via `cookies()` in Next.js, or
                               share auth across subdomains.

Switch via `auth.setStorageMode('cookie')` early in app bootstrap.
"""

from __future__ import annotations


# ── Shared TS fragments ──────────────────────────────────────────────────────
# Emitted verbatim into BOTH auth stores (JWT + public). Single source for
# every line that must not drift between the two modes. Plain strings —
# single braces — interpolated into the f-string templates below.

_ENV_HELPERS_TS = '''\
/** Detect locale from `NEXT_LOCALE` cookie or `navigator.language`. */
function detectLocale(): string | null {
  try {
    if (typeof document !== 'undefined') {
      const m = document.cookie.match(/(?:^|;\\s*)NEXT_LOCALE=([^;]*)/);
      const locale = m?.[1];
      if (locale !== undefined) return decodeURIComponent(locale);
    }
    if (typeof navigator !== 'undefined' && navigator.language) {
      return navigator.language;
    }
  } catch {}
  return null;
}

/** Default baseUrl.
 *
 * Browser: uses NEXT_PUBLIC_API_PROXY_URL if set (empty string = same-origin
 * Next.js proxy), otherwise falls back to NEXT_PUBLIC_API_URL directly.
 * Set NEXT_PUBLIC_API_PROXY_URL='' in apps that proxy /apix/* via Next.js
 * Route Handler; leave it unset in apps that hit Django directly.
 *
 * Server (SSR / RSC / Edge): use NEXT_PUBLIC_API_URL so server-side fetch
 * reaches Django directly (proxy is a same-origin HTTP round-trip on server).
 */
function defaultBaseUrl(): string {
  if (typeof window !== 'undefined') {
    try {
      if (typeof process !== 'undefined' && process.env) {
        if (process.env.NEXT_PUBLIC_STATIC_BUILD === 'true') return '';
        // NEXT_PUBLIC_API_PROXY_URL='' means same-origin proxy (e.g. /apix/* route handler).
        // Next.js inlines defined vars as their value; undefined means the var was not set.
        if (process.env.NEXT_PUBLIC_API_PROXY_URL !== undefined)
          return process.env.NEXT_PUBLIC_API_PROXY_URL;
        return process.env.NEXT_PUBLIC_API_URL || '';
      }
    } catch {}
    return '';
  }
  try {
    if (typeof process !== 'undefined' && process.env) {
      if (process.env.NEXT_PUBLIC_STATIC_BUILD === 'true') return '';
      return process.env.NEXT_PUBLIC_API_URL || '';
    }
  } catch {}
  return '';
}

/** Default API key fallback from `NEXT_PUBLIC_API_KEY`.
 *
 * Both browser and server: if NEXT_PUBLIC_API_KEY is set it is used as a
 * global fallback (e.g. a public demo key). When not set, returns null so
 * per-request keys passed via options.headers take effect unobstructed.
 */
function defaultApiKey(): string | null {
  try {
    if (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_KEY) {
      return process.env.NEXT_PUBLIC_API_KEY;
    }
  } catch {}
  return null;
}
'''

_HEY_CLIENT_TS = '''\
/**
 * Captured reference to the shared Hey API client. Set exactly once by
 * `installAuthOnClient(client)` (called from client.gen.ts). All `auth.set*`
 * methods that mutate transport config (baseUrl / credentials) push through
 * this reference. Until installed, those mutations are silently buffered as
 * in-memory state — the next request after install will pick them up.
 */
type HeyClient = {
  setConfig(opts: Record<string, unknown>): void;
  interceptors: {
    request: { use(fn: (req: Request) => Request | Promise<Request>): void };
    response: { use(fn: (res: Response, req: Request) => Response | Promise<Response>): void };
    error: { use(fn: (err: unknown, res: Response | undefined, req: Request | undefined, opts: unknown) => unknown): void };
  };
};
let _client: HeyClient | null = null;

function pushClientConfig(): void {
  if (!_client) return;
  _client.setConfig({
    baseUrl: auth.getBaseUrl(),
    credentials: _withCredentials ? 'include' : 'same-origin',
  });
}
'''

# Locale / API-key / timezone / client-time header wiring — the part of the
# request interceptor common to both modes (indented for the interceptor body).
_COMMON_REQUEST_HEADERS_TS = '''\
    const locale = auth.getLocale();
    if (locale) request.headers.set('Accept-Language', locale);

    // Only set X-API-Key from global store if NOT already present on the
    // request — per-request headers take precedence.
    const apiKey = auth.getApiKey();
    if (apiKey && !request.headers.has('X-API-Key')) request.headers.set('X-API-Key', apiKey);

    try {
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      if (tz) request.headers.set('X-Timezone', tz);
    } catch {}
    request.headers.set('X-Client-Time', new Date().toISOString());
'''

# Wrap raw JSON error objects (thrown by hey-api on non-2xx responses) into
# APIError so callers can do `error instanceof APIError` and read
# `error.statusCode` / `error.response` consistently.
_ERROR_INTERCEPTOR_TS = '''\
  client.interceptors.error.use((err, res, req) => {
    if (err instanceof APIError) return err;
    const url = (req as Request | undefined)?.url ?? '';
    const status = (res as Response | undefined)?.status ?? 0;
    const statusText = (res as Response | undefined)?.statusText ?? '';
    return new APIError(status, statusText, err, url);
  });
'''


def render_auth_ts(
    *,
    access_key: str = "cfg.access_token",
    refresh_key: str = "cfg.refresh_token",
    api_key_storage_key: str = "cfg.api_key",
    refresh_path: str | None = "/cfg/accounts/token/refresh/",
) -> str:
    """Render `helpers/auth.ts` — the global auth store + interceptor installer.

    ``refresh_path`` — endpoint of the SimpleJWT refresh view. A default
    refresh handler POSTing to it via raw ``fetch`` is auto-registered at
    import time, so EVERY jwt-mode client refreshes on 401 with no app wiring —
    including targets whose own SDK slice doesn't contain the accounts group
    (the endpoint lives on the server regardless of client slicing). Raw fetch
    also avoids any import cycle with ``sdk.gen``. An app can override via
    ``auth.setRefreshHandler(...)`` (last write wins); pass ``None`` to skip
    emission for non-django_cfg backends.
    """

    auto_refresh_import = ""
    auto_refresh_block = ""
    if refresh_path:
        auto_refresh_block = f'''
// ── Default refresh handler (auto-registered) ──────────────────────────────
//
// POSTs straight to the SimpleJWT refresh endpoint so a 401 transparently
// refreshes and retries. Registered at import time; an app can override it
// afterwards with `auth.setRefreshHandler(...)` (last write wins). Returns the
// ROTATED refresh token so the store persists it — `ROTATE_REFRESH_TOKENS`
// blacklists the old one, so reusing it would 401 on the next refresh.
//
// Raw fetch, NOT the SDK: the endpoint exists on the server even when this
// target's sliced SDK doesn't include the accounts group, and importing
// sdk.gen here would close the cycle auth.ts → sdk.gen → client.gen → auth.ts.
const REFRESH_ENDPOINT = '{refresh_path}';

auth.setRefreshHandler(async (refresh) => {{
  try {{
    const url = `${{auth.getBaseUrl()}}${{REFRESH_ENDPOINT}}`;
    const headers: Record<string, string> = {{ 'Content-Type': 'application/json' }};
    // Bound tokens (`cnf.jkt`) require a DPoP proof on the refresh call too.
    if (dpopEnabled() && typeof window !== 'undefined') {{
      const proof = await _makeDpopProof('POST', url);
      if (proof) headers['DPoP'] = proof;
    }}
    const res = await fetch(url, {{
      method: 'POST',
      headers,
      credentials: auth.getWithCredentials() ? 'include' : 'same-origin',
      body: JSON.stringify({{ refresh }}),
    }});
    if (!res.ok) return null;
    const data = (await res.json()) as {{ access?: string; refresh?: string }} | null;
    return data?.access
      ? {{ access: data.access, refresh: data.refresh ?? refresh }}
      : null;
  }} catch {{
    return null;
  }}
}});
'''

    return f'''\
// AUTO-GENERATED by django_generator / ts_extras.wrapper
// Global auth store. Wired into the shared `client` from `client.gen.ts`
// via `installAuthOnClient(client)` — called synchronously by the
// post-processed bottom of client.gen.ts. No circular import here.
// DO NOT EDIT — re-run `make gen`.

import {{ APIError }} from './errors';
{auto_refresh_import}
const ACCESS_KEY = '{access_key}';
const REFRESH_KEY = '{refresh_key}';
const API_KEY_KEY = '{api_key_storage_key}';

const isBrowser = typeof window !== 'undefined';

export type StorageMode = 'localStorage' | 'sessionStorage' | 'cookie';

// ── Storage backends (browser-only; server-side reads return null) ─────────

interface KVStore {{
  get(key: string): string | null;
  set(key: string, value: string | null): void;
}}

const localStorageBackend: KVStore = {{
  get(key) {{
    if (!isBrowser) return null;
    try {{ return window.localStorage.getItem(key); }} catch {{ return null; }}
  }},
  set(key, value) {{
    if (!isBrowser) return;
    try {{
      if (value === null) window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, value);
    }} catch {{}}
  }},
}};

const sessionStorageBackend: KVStore = {{
  get(key) {{
    if (!isBrowser) return null;
    try {{ return window.sessionStorage.getItem(key); }} catch {{ return null; }}
  }},
  set(key, value) {{
    if (!isBrowser) return;
    try {{
      if (value === null) window.sessionStorage.removeItem(key);
      else window.sessionStorage.setItem(key, value);
    }} catch {{}}
  }},
}};

/** 30 days, matches typical refresh-token lifetime. */
const COOKIE_MAX_AGE = 60 * 60 * 24 * 30;

const cookieBackend: KVStore = {{
  get(key) {{
    if (!isBrowser) return null;
    try {{
      const re = new RegExp(`(?:^|;\\\\s*)${{encodeURIComponent(key)}}=([^;]*)`);
      const m = document.cookie.match(re);
      const value = m?.[1];
      return value === undefined ? null : decodeURIComponent(value);
    }} catch {{ return null; }}
  }},
  set(key, value) {{
    if (!isBrowser) return;
    try {{
      const k = encodeURIComponent(key);
      const secure = window.location.protocol === 'https:' ? '; Secure' : '';
      if (value === null) {{
        document.cookie = `${{k}}=; Path=/; Max-Age=0; SameSite=Lax${{secure}}`;
      }} else {{
        const v = encodeURIComponent(value);
        document.cookie = `${{k}}=${{v}}; Path=/; Max-Age=${{COOKIE_MAX_AGE}}; SameSite=Lax${{secure}}`;
      }}
    }} catch {{}}
  }},
}};

let _storage: KVStore = localStorageBackend;
let _storageMode: StorageMode = 'localStorage';

{_ENV_HELPERS_TS}
// ── In-memory overrides (win over storage / env) ───────────────────────────
let _localeOverride: string | null = null;
let _apiKeyOverride: string | null = null;
let _baseUrlOverride: string | null = null;
let _withCredentials = true;
let _onUnauthorized: ((response: Response) => void) | null = null;

/**
 * User-supplied refresh handler. Receives the current refresh token,
 * must return a fresh access (and optional refresh) pair or null on failure.
 * Set once at app bootstrap via `auth.setRefreshHandler(...)`.
 */
type RefreshResult = {{ access: string; refresh?: string }} | null;
type RefreshHandler = (refreshToken: string) => Promise<RefreshResult>;
let _refreshHandler: RefreshHandler | null = null;

/** Single-flight: every concurrent 401 awaits the same refresh. */
let _refreshInflight: Promise<string | null> | null = null;

/** Marker header — set on retried requests so we never loop on 401. */
const RETRY_MARKER = 'X-Auth-Retry';

// ── Reactive session snapshot ───────────────────────────────────────────────
//
// The store is the single source of truth for "am I logged in". React (or any
// listener) subscribes via `auth.subscribe` + `auth.getSnapshot` — designed to
// plug straight into `useSyncExternalStore`. The snapshot flips automatically
// on: token writes, refresh success/failure, cross-tab storage events, and an
// internal timer armed to the next JWT `exp` boundary.

export type SessionStatus = 'authenticated' | 'anonymous';

export type SessionSnapshot = {{
  /** 'authenticated' = a live access token OR a live refresh token exists. */
  status: SessionStatus;
  /** ms-epoch expiry of the current access token (null: no token / no exp). */
  accessExpiresAt: number | null;
}};

/** Decode a JWT `exp` claim to ms epoch. Null on any malformed input. */
function jwtExpMs(token: string): number | null {{
  try {{
    const payload = token.split('.')[1];
    if (!payload) return null;
    const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')));
    return typeof json.exp === 'number' ? json.exp * 1000 : null;
  }} catch {{ return null; }}
}}

function computeSnapshot(): SessionSnapshot {{
  const access = _storage.get(ACCESS_KEY);
  const refresh = _storage.get(REFRESH_KEY);
  const now = Date.now();
  const accessExp = access ? jwtExpMs(access) : null;
  const accessAlive = access !== null && (accessExp === null || accessExp > now);
  const refreshExp = refresh ? jwtExpMs(refresh) : null;
  const refreshAlive = refresh !== null && (refreshExp === null || refreshExp > now);
  return {{
    status: accessAlive || refreshAlive ? 'authenticated' : 'anonymous',
    accessExpiresAt: accessExp,
  }};
}}

/** Stable object for SSR — `useSyncExternalStore` needs referential equality. */
const SERVER_SNAPSHOT: SessionSnapshot = {{ status: 'anonymous', accessExpiresAt: null }};

/** Same-tab, cross-store sync channel. An app can host several copies of this
 * generated store (separate JS modules) sharing the same storage keys; the
 * `storage` event only fires in OTHER tabs, so a window event bridges them
 * synchronously within the tab (login in one store flips all of them). */
const SESSION_SYNC_EVENT = `cfg-auth:changed:${{ACCESS_KEY}}`;

let _snapshot: SessionSnapshot = computeSnapshot();
const _sessionListeners = new Set<() => void>();
let _expiryTimer: ReturnType<typeof setTimeout> | null = null;
let _storageListenerInstalled = false;

/** Re-arm the timer that flips the snapshot exactly when a token expires. */
function scheduleExpiryFlip(): void {{
  if (!isBrowser) return;
  if (_expiryTimer !== null) {{ clearTimeout(_expiryTimer); _expiryTimer = null; }}
  if (_sessionListeners.size === 0) return;
  const now = Date.now();
  const exps: number[] = [];
  const access = _storage.get(ACCESS_KEY);
  const refresh = _storage.get(REFRESH_KEY);
  const accessExp = access ? jwtExpMs(access) : null;
  const refreshExp = refresh ? jwtExpMs(refresh) : null;
  if (accessExp !== null && accessExp > now) exps.push(accessExp);
  if (refreshExp !== null && refreshExp > now) exps.push(refreshExp);
  if (!exps.length) return;
  // +250ms grace so the token is REALLY expired when we flip; clamp to the
  // max signed-32-bit setTimeout delay (~24.8 days).
  const delay = Math.min(Math.min(...exps) - now + 250, 0x7fffffff);
  _expiryTimer = setTimeout(notifySessionChanged, delay);
}}

/** Recompute the snapshot; notify subscribers only when it actually changed. */
function notifySessionChanged(): void {{
  const next = computeSnapshot();
  const changed =
    next.status !== _snapshot.status ||
    next.accessExpiresAt !== _snapshot.accessExpiresAt;
  if (changed) _snapshot = next;
  scheduleExpiryFlip();
  if (!changed) return;
  for (const listener of Array.from(_sessionListeners)) {{
    try {{ listener(); }} catch {{}}
  }}
  // Wake sibling stores in this tab. Re-entrant but convergent: a store that
  // recomputes to the SAME snapshot doesn't re-dispatch, so the cascade stops
  // after every store has caught up.
  if (isBrowser) {{
    try {{ window.dispatchEvent(new Event(SESSION_SYNC_EVENT)); }} catch {{}}
  }}
}}

/** Cross-tab + cross-store sync — `storage` events only fire in OTHER tabs;
 * the window event covers sibling stores in THIS tab. Either way a login or
 * logout anywhere flips every snapshot reading the same keys. */
function ensureStorageSync(): void {{
  if (!isBrowser || _storageListenerInstalled) return;
  _storageListenerInstalled = true;
  window.addEventListener('storage', (e) => {{
    if (e.key === null || e.key === ACCESS_KEY || e.key === REFRESH_KEY) {{
      notifySessionChanged();
    }}
  }});
  window.addEventListener(SESSION_SYNC_EVENT, () => notifySessionChanged());
}}

/**
 * Terminal-401 subscribers. Unlike the single `onUnauthorized` slot these
 * compose: each registration returns its own unsubscribe, so StrictMode
 * double-mounts and multiple packages can't clobber each other.
 */
type SessionExpiredHandler = (response: Response) => void;
const _sessionExpiredHandlers = new Set<SessionExpiredHandler>();

{_HEY_CLIENT_TS}
/**
 * Global auth/config store. All getters read live state every call —
 * the interceptor below uses these to attach headers per-request.
 *
 * Default storage backend is `localStorage`. Switch to cookies (e.g.
 * for Next.js SSR cookie access) via `auth.setStorageMode('cookie')`
 * early in the app bootstrap.
 *
 * @example
 *   import {{ auth }} from '@your/api';
 *   auth.setToken(jwt);
 *   auth.clearTokens();
 *   auth.setStorageMode('cookie');
 */
export const auth = {{
  // ── Storage mode ──────────────────────────────────────────────────
  getStorageMode(): StorageMode {{ return _storageMode; }},
  setStorageMode(mode: StorageMode): void {{
    _storageMode = mode;
    _storage = mode === 'cookie'
      ? cookieBackend
      : mode === 'sessionStorage'
        ? sessionStorageBackend
        : localStorageBackend;
    notifySessionChanged();
  }},

  // ── Bearer token ──────────────────────────────────────────────────
  getToken(): string | null {{ return _storage.get(ACCESS_KEY); }},
  setToken(token: string | null): void {{
    _storage.set(ACCESS_KEY, token);
    notifySessionChanged();
  }},
  getRefreshToken(): string | null {{ return _storage.get(REFRESH_KEY); }},
  setRefreshToken(token: string | null): void {{
    _storage.set(REFRESH_KEY, token);
    notifySessionChanged();
  }},
  clearTokens(): void {{
    _storage.set(ACCESS_KEY, null);
    _storage.set(REFRESH_KEY, null);
    notifySessionChanged();
  }},
  /** Session-aware: token PRESENT and not past its `exp` (or a live refresh
   * token exists that can mint one). Prefer `getSnapshot().status` in React. */
  isAuthenticated(): boolean {{ return computeSnapshot().status === 'authenticated'; }},

  // ── Session (the ONE write path for login/logout flows) ──────────
  /**
   * Persist a token pair atomically. Every login flow (OTP verify, 2FA,
   * OAuth callback) and the refresh handler should end here — do NOT
   * scatter `setToken`/`setRefreshToken` pairs through app code.
   * `refresh: undefined` keeps the current refresh token (access-only
   * rotation); `refresh: null` explicitly drops it.
   */
  setSession(tokens: {{ access: string; refresh?: string | null }}): void {{
    _storage.set(ACCESS_KEY, tokens.access);
    if (tokens.refresh !== undefined) _storage.set(REFRESH_KEY, tokens.refresh);
    notifySessionChanged();
  }},
  clearSession(): void {{ auth.clearTokens(); }},

  // ── Reactive snapshot (for useSyncExternalStore) ──────────────────
  /**
   * @example React:
   *   const session = useSyncExternalStore(
   *     auth.subscribe, auth.getSnapshot, auth.getServerSnapshot,
   *   );
   *   const isAuthenticated = session.status === 'authenticated';
   */
  getSnapshot(): SessionSnapshot {{ return _snapshot; }},
  getServerSnapshot(): SessionSnapshot {{ return SERVER_SNAPSHOT; }},
  subscribe(listener: () => void): () => void {{
    ensureStorageSync();
    _sessionListeners.add(listener);
    // Sync state & arm the expiry timer now that someone is listening.
    notifySessionChanged();
    return () => {{
      _sessionListeners.delete(listener);
      if (_sessionListeners.size === 0 && _expiryTimer !== null) {{
        clearTimeout(_expiryTimer);
        _expiryTimer = null;
      }}
    }};
  }},

  /**
   * Fired on TERMINAL 401 — after the refresh+retry path is exhausted.
   * The store has already cleared the session before calling back, so
   * handlers only need to route to login (no clear-then-redirect
   * ordering to get wrong). Returns an unsubscribe function; multiple
   * handlers compose (unlike the legacy single-slot `onUnauthorized`).
   */
  onSessionExpired(cb: SessionExpiredHandler): () => void {{
    _sessionExpiredHandlers.add(cb);
    return () => {{ _sessionExpiredHandlers.delete(cb); }};
  }},

  // ── API key ───────────────────────────────────────────────────────
  getApiKey(): string | null {{
    return _apiKeyOverride ?? _storage.get(API_KEY_KEY) ?? defaultApiKey();
  }},
  setApiKey(key: string | null): void {{ _apiKeyOverride = key; }},
  setApiKeyPersist(key: string | null): void {{
    _apiKeyOverride = key;
    _storage.set(API_KEY_KEY, key);
  }},
  clearApiKey(): void {{ _apiKeyOverride = null; _storage.set(API_KEY_KEY, null); }},

  // ── Locale ────────────────────────────────────────────────────────
  getLocale(): string | null {{ return _localeOverride ?? detectLocale(); }},
  setLocale(locale: string | null): void {{ _localeOverride = locale; }},

  // ── Base URL ──────────────────────────────────────────────────────
  getBaseUrl(): string {{
    const url = (_baseUrlOverride ?? defaultBaseUrl());
    return url.replace(/\\/$/, '');
  }},
  setBaseUrl(url: string | null): void {{
    _baseUrlOverride = url ? url.replace(/\\/$/, '') : null;
    pushClientConfig();
  }},

  // ── Credentials toggle ────────────────────────────────────────────
  getWithCredentials(): boolean {{ return _withCredentials; }},
  setWithCredentials(value: boolean): void {{
    _withCredentials = value;
    pushClientConfig();
  }},

  // ── 401 handler ───────────────────────────────────────────────────
  /**
   * Fired when the server returns 401 AND no refresh path recovers it
   * (no refresh token, no refresh handler, refresh failed, or retry
   * still 401). The app should clear local state and redirect to login.
   *
   * NOT fired for 401 that gets transparently recovered by the refresh
   * handler — those are invisible to callers.
   */
  onUnauthorized(cb: ((response: Response) => void) | null): void {{
    _onUnauthorized = cb;
  }},

  /**
   * Register the refresh strategy. The handler receives the current
   * refresh token and must call your refresh endpoint, returning
   * `{{ access, refresh? }}` on success or `null` on failure.
   *
   * @example
   *   auth.setRefreshHandler(async (refresh) => {{
   *     const {{ data }} = await Auth.tokenRefreshCreate({{ body: {{ refresh }} }});
   *     return data ? {{ access: data.access, refresh: data.refresh }} : null;
   *   }});
   */
  setRefreshHandler(fn: RefreshHandler | null): void {{
    _refreshHandler = fn;
  }},

  /**
   * Proactively run the registered refresh handler right now, reusing the
   * SAME single-flight promise as the 401-recovery interceptor. Callers
   * (e.g. an expiry timer / focus / reconnect) get token rotation,
   * de-duplication and rotated-token persistence for free — they must NOT
   * re-implement any of it. Returns the fresh access token, or null if
   * there is no handler / no refresh token / the refresh failed.
   */
  refreshNow(): Promise<string | null> {{
    return tryRefresh();
  }},
}};

/**
 * Run the user-supplied refresh handler, persist the rotated tokens, and
 * return the fresh access token (or null on any failure path).
 *
 * TWO layers of coordination, because a single app can host MULTIPLE copies of
 * this generated store (e.g. `@djangocfg/api` + a locally-generated client +
 * `@djangocfg/monitor`), all sharing the SAME refresh token in storage:
 *
 *   1. Per-store single-flight (`_refreshInflight`) — concurrent 401s WITHIN
 *      this module coalesce onto one promise. Fast path, no lock.
 *   2. Cross-store mutex (`navigator.locks`) keyed on the refresh-token storage
 *      key — serializes refreshes across EVERY store in the app. The refresh
 *      token is re-read INSIDE the lock, so if another store already rotated it
 *      (SimpleJWT `ROTATE_REFRESH_TOKENS` blacklists the old one), the loser
 *      picks up the fresh access token instead of re-POSTing a blacklisted
 *      refresh token and getting a spurious 401 → logout.
 *
 * Web Locks is browser-only; on SSR / older runtimes we degrade gracefully to
 * layer 1 alone (correct whenever at most one store refreshes).
 */
async function tryRefresh(): Promise<string | null> {{
  if (_refreshInflight) return _refreshInflight;
  if (!_refreshHandler) return null;

  // The critical section — re-reads the refresh token every time it runs, so a
  // rotation performed by another store (or by us on a prior attempt) is always
  // observed. Returns the fresh access token, or null on any failure.
  const runRefresh = async (): Promise<string | null> => {{
    const refresh = auth.getRefreshToken();
    if (!refresh) return null;
    const result = await _refreshHandler!(refresh);
    if (!result?.access) return null;
    auth.setToken(result.access);
    if (result.refresh) auth.setRefreshToken(result.refresh);
    return result.access;
  }};

  _refreshInflight = (async () => {{
    try {{
      // Serialize across all stores in this app when Web Locks is available.
      const locks =
        typeof navigator !== 'undefined'
          ? (navigator as Navigator & {{ locks?: LockManager }}).locks
          : undefined;
      if (locks?.request) {{
        return await locks.request(`${{REFRESH_KEY}}:refresh`, runRefresh);
      }}
      return await runRefresh();
    }} catch {{
      return null;
    }} finally {{
      _refreshInflight = null;
    }}
  }})();

  return _refreshInflight;
}}

/**
 * Terminal 401 — no refresh path can recover this session. The store clears
 * its own tokens FIRST (subscribers flip to 'anonymous' via the snapshot),
 * then notifies `onSessionExpired` subscribers and the legacy
 * `onUnauthorized` slot. Apps only route to login; they never own the
 * clear-before-redirect ordering.
 */
function expireSession(response: Response): void {{
  auth.clearTokens();
  for (const cb of Array.from(_sessionExpiredHandlers)) {{
    try {{ cb(response); }} catch {{}}
  }}
  if (_onUnauthorized) {{
    try {{ _onUnauthorized(response); }} catch {{}}
  }}
}}

/**
 * Wire the shared client to the global auth store. Called exactly
 * once from `client.gen.ts` (post-processed) right after
 * `createClient()`. Synchronous — no microtask, no TDZ races.
 *
 * Safe to call from server / SSR: storage backends short-circuit on
 * non-browser environments, so headers populated by the interceptor
 * are simply absent server-side (which is the correct behaviour
 * unless the caller explicitly sets a server-side token).
 *
 * ── How API key auth works ────────────────────────────────────────────────
 *
 * There are three ways to supply X-API-Key, in priority order:
 *
 *   1. Per-request header (highest priority, overrides everything):
 *        SomeApi.someEndpoint({{ headers: {{ 'X-API-Key': userKey }} }})
 *      Use this in playgrounds or any context where the key comes from
 *      user input rather than app config.
 *
 *   2. Global override via auth.setApiKey(key) — applies to every request
 *      from this client until cleared. Good for single-user sessions.
 *
 *   3. NEXT_PUBLIC_API_KEY env var — read by defaultApiKey() on every request.
 *      Use as a public fallback key (e.g. a shared demo key for unauthenticated
 *      visitors). When not set, returns null so per-request keys work freely.
 *
 * ── baseUrl gotcha with proxy packages ───────────────────────────────────
 *
 * If another package (e.g. @carapis/catalog-api/client) calls
 * `auth.setBaseUrl('')` on import, ALL requests from this shared client
 * will go to relative paths (Next.js proxy) instead of hitting Django
 * directly. This is intentional for the public catalog — but breaks any
 * feature that needs to reach Django with a dynamic API key from the
 * browser (e.g. a playground).
 *
 * Fix: pass `baseUrl` explicitly per-call to override the global setting:
 *   SomeApi.someEndpoint({{
 *     baseUrl: process.env.NEXT_PUBLIC_API_URL,
 *     headers: {{ 'X-API-Key': userKey }},
 *   }})
 */
// ── DPoP (RFC 9449) — sender-constrained tokens ────────────────────────────
//
// When NEXT_PUBLIC_DPOP_ENABLED === 'true', the client holds a P-256 keypair
// whose PRIVATE key is non-extractable (Web Crypto `extractable:false`) and
// stored in IndexedDB. JS — including XSS — can sign with it but can NEVER read
// it. Each request carries a fresh `DPoP` proof signed by that key; the backend
// binds the token to the key (`cnf.jkt`) and rejects any request whose proof key
// doesn't match. A stolen token is therefore useless to an attacker.
//
// Dormant unless the env flag is on — bearer-mode apps are unaffected.

function dpopEnabled(): boolean {{
  try {{
    return typeof process !== 'undefined'
      && process.env?.NEXT_PUBLIC_DPOP_ENABLED === 'true';
  }} catch {{ return false; }}
}}

const _DPOP_DB = 'cfg-auth';
const _DPOP_STORE = 'keys';
const _DPOP_KEY_ID = 'dpop-ec-p256';

function _idbOpen(): Promise<IDBDatabase> {{
  return new Promise((resolve, reject) => {{
    const req = indexedDB.open(_DPOP_DB, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(_DPOP_STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  }});
}}

function _idbGet(key: string): Promise<CryptoKeyPair | undefined> {{
  return _idbOpen().then((db) => new Promise((resolve, reject) => {{
    const tx = db.transaction(_DPOP_STORE, 'readonly');
    const req = tx.objectStore(_DPOP_STORE).get(key);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  }}));
}}

function _idbPut(key: string, value: CryptoKeyPair): Promise<void> {{
  return _idbOpen().then((db) => new Promise((resolve, reject) => {{
    const tx = db.transaction(_DPOP_STORE, 'readwrite');
    tx.objectStore(_DPOP_STORE).put(value, key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  }}));
}}

/** Single-flight keypair init — the private key is created non-extractable. */
let _dpopKeyPromise: Promise<CryptoKeyPair> | null = null;

function _getDpopKeyPair(): Promise<CryptoKeyPair> {{
  if (_dpopKeyPromise) return _dpopKeyPromise;
  _dpopKeyPromise = (async () => {{
    const existing = await _idbGet(_DPOP_KEY_ID).catch(() => undefined);
    if (existing) return existing;
    const pair = await crypto.subtle.generateKey(
      {{ name: 'ECDSA', namedCurve: 'P-256' }},
      false, // extractable:false — JS can sign but never export the private key
      ['sign'],
    );
    // CryptoKey is structured-cloneable; IndexedDB persists it across reloads
    // WITHOUT ever exposing raw key bytes to JS.
    await _idbPut(_DPOP_KEY_ID, pair).catch(() => {{}});
    return pair;
  }})();
  return _dpopKeyPromise;
}}

function _b64urlFromBytes(bytes: ArrayBuffer | Uint8Array): string {{
  const arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let s = '';
  for (let i = 0; i < arr.length; i++) s += String.fromCharCode(arr[i] ?? 0);
  return btoa(s).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, '');
}}

function _b64urlFromString(str: string): string {{
  return _b64urlFromBytes(new TextEncoder().encode(str));
}}

/** ECDSA raw signature (r||s) → JOSE base64url (Web Crypto already returns raw). */
async function _publicJwk(pub: CryptoKey): Promise<Record<string, string>> {{
  const jwk = await crypto.subtle.exportKey('jwk', pub);
  // Public components only — required RFC 7638 members for EC.
  return {{ kty: 'EC', crv: 'P-256', x: jwk.x as string, y: jwk.y as string }};
}}

/** Build a DPoP proof JWT for this request (htm/htu/iat/jti), signed in-key. */
async function _makeDpopProof(method: string, url: string): Promise<string | null> {{
  try {{
    const pair = await _getDpopKeyPair();
    const jwk = await _publicJwk(pair.publicKey);
    const header = {{ typ: 'dpop+jwt', alg: 'ES256', jwk }};
    // htu = scheme://authority/path without query/fragment.
    const withoutFragment = url.split('#')[0] ?? url;
    const htu = withoutFragment.split('?')[0] ?? withoutFragment;
    const jti =
      (crypto.randomUUID && crypto.randomUUID()) ||
      _b64urlFromBytes(crypto.getRandomValues(new Uint8Array(16)));
    const payload = {{ htm: method.toUpperCase(), htu, iat: Math.floor(Date.now() / 1000), jti }};
    const signingInput =
      `${{_b64urlFromString(JSON.stringify(header))}}.${{_b64urlFromString(JSON.stringify(payload))}}`;
    const sig = await crypto.subtle.sign(
      {{ name: 'ECDSA', hash: 'SHA-256' }},
      pair.privateKey,
      new TextEncoder().encode(signingInput),
    );
    return `${{signingInput}}.${{_b64urlFromBytes(sig)}}`;
  }} catch {{
    return null; // never break a request because proof generation failed
  }}
}}

export function installAuthOnClient(client: HeyClient): void {{
  if (_client) return; // idempotent
  _client = client;

  client.setConfig({{
    baseUrl: auth.getBaseUrl(),
    credentials: _withCredentials ? 'include' : 'same-origin',
  }});

  client.interceptors.request.use(async (request) => {{
    const token = auth.getToken();
    if (token) request.headers.set('Authorization', `Bearer ${{token}}`);

{_COMMON_REQUEST_HEADERS_TS}
    // DPoP proof — sign a fresh per-request proof with the non-extractable key.
    // Only in a browser, only when enabled. Failure is non-fatal (proof null).
    if (dpopEnabled() && typeof window !== 'undefined') {{
      const proof = await _makeDpopProof(request.method, request.url);
      if (proof) request.headers.set('DPoP', proof);
    }}

    return request;
  }});

{_ERROR_INTERCEPTOR_TS}

  client.interceptors.response.use(async (response, request) => {{
    if (response.status !== 401) return response;

    // Already retried once — give up to avoid loops.
    if (request.headers.get(RETRY_MARKER)) {{
      expireSession(response);
      return response;
    }}

    const newToken = await tryRefresh();
    if (!newToken) {{
      expireSession(response);
      return response;
    }}

    // Retry the original request once with the new token. We mutate a
    // clone so the original Request body (already consumed by the
    // failed call) doesn't trip "body already used".
    const retry = request.clone();
    retry.headers.set('Authorization', `Bearer ${{newToken}}`);
    retry.headers.set(RETRY_MARKER, '1');
    // This retry uses raw fetch() and bypasses the request interceptor, so the
    // DPoP proof must be re-attached here or a bound token would 401 on retry.
    if (dpopEnabled() && typeof window !== 'undefined') {{
      const proof = await _makeDpopProof(retry.method, retry.url);
      if (proof) retry.headers.set('DPoP', proof);
    }}
    try {{
      const retried = await fetch(retry);
      if (retried.status === 401) expireSession(retried);
      return retried;
    }} catch {{
      // Network error on the retry. The refresh SUCCEEDED (we hold a fresh
      // token), so the session is alive — a transient network blip must NOT
      // log the user out. Surface the original 401 to the caller only.
      return response;
    }}
  }});
}}
{auto_refresh_block}
export type Auth = typeof auth;
'''


def render_auth_public_ts() -> str:
    """Render the PUBLIC-mode `helpers/auth.ts` — a token-free minimal store.

    For generated clients that only call public endpoints (e.g. a frontend
    monitor's ingest API). Emits baseUrl / locale / timezone / API-key wiring
    and the APIError interceptor, but NO token storage, NO Authorization
    header, NO refresh machinery, NO DPoP (~450 lines less than JWT mode).

    The `auth` surface keeps the same method NAMES as JWT mode (token methods
    are inert no-ops) so the per-group `class API` facade compiles unchanged.
    A public client also never attaches a logged-in user's Bearer token to
    public requests — even when another JWT-mode store in the same app has
    persisted tokens under the shared storage keys.
    """

    return f'''\
// AUTO-GENERATED by django_generator / ts_extras.wrapper (authMode: public)
// Token-free store for public-endpoint clients: no Authorization header, no
// token storage, no refresh, no DPoP. Wired into the shared `client` from
// `client.gen.ts` via `installAuthOnClient(client)`.
// DO NOT EDIT — re-run `make gen`.

import {{ APIError }} from './errors';

export type StorageMode = 'localStorage' | 'cookie';

{_ENV_HELPERS_TS}
// ── In-memory overrides (win over env) ─────────────────────────────────────
let _localeOverride: string | null = null;
let _apiKeyOverride: string | null = null;
let _baseUrlOverride: string | null = null;
let _withCredentials = true;

{_HEY_CLIENT_TS}
/**
 * Public-mode store. Token/session methods exist for facade compatibility
 * but are inert: this client NEVER reads, writes, or sends tokens — even
 * when a JWT-mode store in the same app has persisted tokens in storage.
 */
export const auth = {{
  // ── Inert token/session surface (public client has no session) ─────
  getStorageMode(): StorageMode {{ return 'localStorage'; }},
  setStorageMode(_mode: StorageMode): void {{}},
  getToken(): string | null {{ return null; }},
  setToken(_token: string | null): void {{}},
  getRefreshToken(): string | null {{ return null; }},
  setRefreshToken(_token: string | null): void {{}},
  clearTokens(): void {{}},
  isAuthenticated(): boolean {{ return false; }},
  onUnauthorized(_cb: ((response: Response) => void) | null): void {{}},
  setRefreshHandler(
    _fn: ((refreshToken: string) => Promise<{{ access: string; refresh?: string }} | null>) | null,
  ): void {{}},
  refreshNow(): Promise<string | null> {{ return Promise.resolve(null); }},

  // ── API key (in-memory override + env fallback; never persisted) ───
  getApiKey(): string | null {{ return _apiKeyOverride ?? defaultApiKey(); }},
  setApiKey(key: string | null): void {{ _apiKeyOverride = key; }},
  setApiKeyPersist(key: string | null): void {{ _apiKeyOverride = key; }},
  clearApiKey(): void {{ _apiKeyOverride = null; }},

  // ── Locale ────────────────────────────────────────────────────────
  getLocale(): string | null {{ return _localeOverride ?? detectLocale(); }},
  setLocale(locale: string | null): void {{ _localeOverride = locale; }},

  // ── Base URL ──────────────────────────────────────────────────────
  getBaseUrl(): string {{
    const url = (_baseUrlOverride ?? defaultBaseUrl());
    return url.replace(/\\/$/, '');
  }},
  setBaseUrl(url: string | null): void {{
    _baseUrlOverride = url ? url.replace(/\\/$/, '') : null;
    pushClientConfig();
  }},

  // ── Credentials toggle ────────────────────────────────────────────
  getWithCredentials(): boolean {{ return _withCredentials; }},
  setWithCredentials(value: boolean): void {{
    _withCredentials = value;
    pushClientConfig();
  }},
}};

export function installAuthOnClient(client: HeyClient): void {{
  if (_client) return; // idempotent
  _client = client;

  client.setConfig({{
    baseUrl: auth.getBaseUrl(),
    credentials: _withCredentials ? 'include' : 'same-origin',
  }});

  client.interceptors.request.use((request) => {{
{_COMMON_REQUEST_HEADERS_TS}
    return request;
  }});

{_ERROR_INTERCEPTOR_TS}}}

export type Auth = typeof auth;
'''


__all__ = ["render_auth_ts", "render_auth_public_ts"]
