import { CFG_KEYS, cfgStorage } from './keys';
import { getApiOrigin, resolveApiUrl, setApiOrigin } from './api-origin';
import { APIError, NetworkError, isTransientRefreshError } from './errors';
import { sharedAuthState, type Listener, type RefreshHandler, type SharedAuthState } from './state';
import { storeTrace } from './store-trace';

export type RealtimeCidProvider = () => string | null;

const REALTIME_CID_SLOT = Symbol.for('djangocfg.realtime.cid');
type CidSlotHolder = { [REALTIME_CID_SLOT]?: RealtimeCidProvider | null };

/** Install the current WebSocket connection id for write requests. */
export function setRealtimeCidProvider(provider: RealtimeCidProvider | null): void {
  (globalThis as CidSlotHolder)[REALTIME_CID_SLOT] = provider;
}

export function getRealtimeCid(): string | null {
  try {
    const provider = (globalThis as CidSlotHolder)[REALTIME_CID_SLOT];
    return provider ? provider() : null;
  } catch {
    return null;
  }
}

export type SessionStatus = 'anonymous' | 'authenticated';

export interface SessionSnapshot {
  /** `authenticated`: a live access token, or a live refresh token that can mint one. */
  status: SessionStatus;
  isAuthenticated: boolean;
  accessToken: string | null;
}

export interface RefreshResult {
  access: string;
  refresh?: string;
}

const REFRESH_PATH = '/cfg/accounts/token/refresh/';
/** Web Locks name: one refresh at a time across every tab and copy of the origin (H1.2). */
const REFRESH_LOCK = 'djangocfg.api.refresh';
/** The expiry timer fires this long after `exp`, so the token is really dead when the snapshot flips. */
const EXPIRY_GRACE_MS = 250;
const MAX_TIMEOUT_MS = 0x7fffffff;

const hasWindow = () => typeof window !== 'undefined';
const hasDocument = () => typeof document !== 'undefined';
const browserTimezone = () => {
  try { return Intl.DateTimeFormat().resolvedOptions().timeZone || null; }
  catch { return null; }
};
const browserLocale = (): string | null => {
  try {
    if (typeof document === 'undefined') return null;
    const match = document.cookie.match(/(?:^|;\s*)NEXT_LOCALE=([^;]*)/);
    if (match?.[1] !== undefined) return decodeURIComponent(match[1]);
    return typeof navigator !== 'undefined' && navigator.language ? navigator.language : null;
  } catch { return null; }
};
const newClientId = (): string => {
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID();
    }
  } catch {
    // Fall through to the portable implementation below.
  }
  return `c-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
};
/** The build-time API key. The literal read is what Next inlines; where nothing did and `process` is absent, it throws. */
const defaultApiKey = (): string | null => {
  try {
    return process.env.NEXT_PUBLIC_API_KEY || null;
  } catch {
    return null;
  }
};

/** A JWT's `exp` in ms since epoch; `null` for a token without one (it then counts as live while present). */
const expiryOf = (token: string | null): number | null => {
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const claims = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/'))) as { exp?: unknown };
    return typeof claims.exp === 'number' ? claims.exp * 1000 : null;
  } catch {
    return null;
  }
};
const isExpired = (token: string | null, now = Date.now()): boolean => {
  const exp = expiryOf(token);
  return exp !== null && exp <= now;
};
const isLive = (s: SharedAuthState, token: string | null): boolean =>
  Boolean(token) && (s.clockSkewed || !isExpired(token));
/** Live access, or a live refresh token that can mint one. A dead pair is signed out. */
const sessionAlive = (s: SharedAuthState): boolean => isLive(s, s.accessToken) || isLive(s, s.refreshToken);

/**
 * The token cookie exactly as the browser holds it, without `cfgStorage`'s in-memory fallback: that fallback
 * belongs to one copy of the module, so another copy would read a rejected write as "signed out".
 */
const readTokenCookie = (key: string): string | null => {
  try {
    const encoded = `${encodeURIComponent(key)}=`;
    const part = document.cookie.split('; ').find((entry) => entry.startsWith(encoded));
    return part ? decodeURIComponent(part.slice(encoded.length)) : null;
  } catch {
    return null;
  }
};
const readTokenCookies = () => ({
  access: readTokenCookie(CFG_KEYS.accessToken.key),
  refresh: readTokenCookie(CFG_KEYS.refreshToken.key),
});

/** Runs once per page, for the copy that creates the shared slot. */
const loadStored = (state: SharedAuthState): void => {
  if (!hasWindow()) return;
  if (hasDocument()) {
    const cookies = readTokenCookies();
    state.cookieSeen = cookies;
    state.accessToken = cookies.access;
    state.refreshToken = cookies.refresh;
  } else {
    state.accessToken = cfgStorage.read(CFG_KEYS.accessToken.key, 'cookie');
    state.refreshToken = cfgStorage.read(CFG_KEYS.refreshToken.key, 'cookie');
  }
  state.apiKey = cfgStorage.read(CFG_KEYS.apiKey.key, 'local');
  updateSnapshot(state);
};

const state = (): SharedAuthState => sharedAuthState(loadStored);

/** Replace the cached snapshot only when the session changed; returns whether it did. */
function updateSnapshot(s: SharedAuthState): boolean {
  const isAuthenticated = sessionAlive(s);
  const current = s.snapshot;
  if (current.isAuthenticated === isAuthenticated && current.accessToken === s.accessToken) return false;
  s.snapshot = {
    status: isAuthenticated ? 'authenticated' : 'anonymous',
    isAuthenticated,
    accessToken: s.accessToken,
  };
  return true;
}

const callListeners = (s: SharedAuthState): void => {
  for (const listener of Array.from(s.listeners)) listener();
};

/** Notify on a microtask: a change found while reading (a read can run during render) never calls back inline. */
const queueNotify = (s: SharedAuthState): void => {
  if (s.notifyQueued) return;
  s.notifyQueued = true;
  queueMicrotask(() => {
    s.notifyQueued = false;
    callListeners(s);
  });
};

/**
 * Re-read the session at the next token `exp` while someone listens, so the snapshot turns anonymous when the last
 * live token dies (H1.1). Browser only.
 */
const armExpiryTimer = (s: SharedAuthState): void => {
  if (s.expiryTimer !== null) {
    clearTimeout(s.expiryTimer);
    s.expiryTimer = null;
  }
  if (!hasWindow() || s.clockSkewed || s.listeners.size === 0) return;
  const now = Date.now();
  const upcoming = [expiryOf(s.accessToken), expiryOf(s.refreshToken)]
    .filter((exp): exp is number => exp !== null && exp > now);
  if (!upcoming.length) return;
  const delay = Math.min(Math.min(...upcoming) - now + EXPIRY_GRACE_MS, MAX_TIMEOUT_MS);
  s.expiryTimer = setTimeout(() => {
    const live = state();
    live.expiryTimer = null;
    if (updateSnapshot(live)) {
      storeTrace('store.expiry', { status: live.snapshot.status });
      callListeners(live);
    }
    armExpiryTimer(live);
  }, delay);
};

/** Tell other tabs to re-read the cookies: a localStorage write raises `storage` there. Carries no token. */
const signalOtherTabs = (): void => {
  if (!hasWindow()) return;
  cfgStorage.write(CFG_KEYS.sessionSignal.key, `${Date.now()}.${Math.random().toString(36).slice(2, 8)}`, 'local');
};

/** After a write by this store: new snapshot, listeners, timer, other tabs. */
const emit = (s: SharedAuthState): void => {
  updateSnapshot(s);
  callListeners(s);
  armExpiryTimer(s);
  signalOtherTabs();
};

/**
 * Adopt a token cookie that changed outside this store: another tab, another subdomain, or an older copy of the
 * package that does not use the shared slot. Only a cookie that differs from what the store last saw counts, so a
 * cookie write the browser rejected never reads as a sign-out. Returns whether the session changed.
 */
const syncFromCookies = (s: SharedAuthState): boolean => {
  if (!hasDocument()) return false;
  const cookies = readTokenCookies();
  const seen = s.cookieSeen;
  if (seen && seen.access === cookies.access && seen.refresh === cookies.refresh) return false;
  s.cookieSeen = cookies;
  if (!seen || seen.access !== cookies.access) s.accessToken = cookies.access;
  if (!seen || seen.refresh !== cookies.refresh) s.refreshToken = cookies.refresh;
  if (!updateSnapshot(s)) return false;
  queueNotify(s);
  armExpiryTimer(s);
  return true;
};

/** The state after picking up any outside change to the token cookies. */
const synced = (): SharedAuthState => {
  const s = state();
  syncFromCookies(s);
  return s;
};

/**
 * Listen for a session change made elsewhere, once per page (H1.1): `storage` (another tab's signal, or a token key
 * an older build kept in localStorage), focus and visibility (cookies raise no event, so a sign-in on another
 * subdomain is seen when the page is looked at again), and `cookieStore` where the browser has it. Same-page copies
 * need no event: they share the slot and its listeners.
 */
const installSync = (s: SharedAuthState): void => {
  if (s.syncInstalled || !hasWindow() || !hasDocument()) return;
  s.syncInstalled = true;
  const resync = (source: string) => {
    if (syncFromCookies(state())) storeTrace('store.sync', { source });
  };
  const watched = new Set<string>([CFG_KEYS.sessionSignal.key, CFG_KEYS.accessToken.key, CFG_KEYS.refreshToken.key]);
  try {
    window.addEventListener('storage', (event) => {
      if (event.key === null || watched.has(event.key)) resync('storage');
    });
    window.addEventListener('focus', () => resync('focus'));
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') resync('visible');
    });
    (window as unknown as { cookieStore?: EventTarget }).cookieStore?.addEventListener('change', () => resync('cookie'));
  } catch {
    // A page that refuses listeners still reads the cookies on every store access.
  }
};

/** Write or remove one token cookie under the page-wide cookie-domain policy. */
const persistToken = (s: SharedAuthState, key: string, value: string | null): void => {
  if (s.cookieDomain !== undefined) cfgStorage.setCookieDomain(s.cookieDomain);
  if (value) cfgStorage.write(key, value, 'cookie');
  else cfgStorage.remove(key, 'cookie');
};
/** Record what the cookies hold after this store wrote them. */
const markCookiesSeen = (s: SharedAuthState): void => {
  if (hasDocument()) s.cookieSeen = readTokenCookies();
};
/**
 * A token the server has just issued is never expired by the server's clock. If it is by this device's, the
 * clock is off: stop trusting `exp` on this page rather than sign the user out or refresh on every request.
 */
const checkClock = (s: SharedAuthState, issued: string | null): void => {
  if (s.clockSkewed || !issued || !isExpired(issued)) return;
  s.clockSkewed = true;
  storeTrace('store.clock', { skewed: true });
};

const warnOnce = (s: SharedAuthState, key: string, message: string): void => {
  if (s.warned.includes(key)) return;
  s.warned.push(key);
  try { console.warn(`[@djangocfg/api] ${message}`); } catch { /* never break the caller */ }
};

const browserClientId = (s: SharedAuthState): string | null => {
  if (!hasWindow()) return null;
  if (s.clientId) return s.clientId;
  const stored = cfgStorage.read(CFG_KEYS.clientId.key, 'local');
  if (stored) {
    s.clientId = stored;
    return stored;
  }
  const created = newClientId();
  s.clientId = created;
  cfgStorage.write(CFG_KEYS.clientId.key, created, 'local');
  return created;
};

/**
 * POST the refresh token to django-cfg's SimpleJWT endpoint, through the same origin resolver as every operation.
 * Throws `NetworkError` when the host cannot be reached and `APIError` for a non-2xx answer; returns an empty
 * `access` for a 2xx body without one. `refreshNow` decides which of those end the session.
 */
const defaultRefresh: RefreshHandler = async (refresh) => {
  const url = resolveApiUrl(REFRESH_PATH);
  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST',
      credentials: state().withCredentials ? 'include' : 'same-origin',
      headers: {
        ...auth.clientHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh }),
    });
  } catch (error) {
    throw new NetworkError('Session refresh could not reach the API', { cause: error }, url);
  }
  const body = await response.json().catch(() => null) as { access?: unknown; refresh?: unknown } | null;
  if (!response.ok) throw new APIError(response.status, body, url, undefined, response.statusText);
  return {
    access: typeof body?.access === 'string' ? body.access : '',
    refresh: typeof body?.refresh === 'string' ? body.refresh : refresh,
  };
};

class SessionRefreshRejected extends Error {
  readonly name = 'SessionRefreshRejected';
}

const expire = (s: SharedAuthState, why: string): void => {
  storeTrace('store.expire', { why, handlers: s.expiryListeners.size });
  auth.clearSession();
  s.unauthorized?.();
  for (const listener of Array.from(s.expiryListeners)) listener();
};

const webLocks = (): LockManager | null => {
  try {
    const locks = typeof navigator !== 'undefined' ? (navigator as Navigator & { locks?: LockManager }).locks : undefined;
    return locks && typeof locks.request === 'function' ? locks : null;
  } catch {
    return null;
  }
};

const traceRefreshFailure = (error: unknown, kept: boolean): void => {
  const { name, statusCode } = (error ?? {}) as { name?: unknown; statusCode?: unknown };
  storeTrace('refresh', {
    ok: false,
    why: typeof name === 'string' ? name : 'unknown',
    status: typeof statusCode === 'number' ? statusCode : 0,
    kept,
  });
};

export const auth = {
  getToken: () => synced().accessToken,
  getRefreshToken: () => synced().refreshToken,
  /**
   * Whether there is a session: a live access token, or a live refresh token that can mint one (`exp`-aware). When
   * only the refresh token is live, the next request refreshes before it is sent (see `needsRefresh`). An expired
   * pair is signed out.
   */
  isAuthenticated: () => sessionAlive(synced()),
  /** The access token is missing or expired while a live refresh token exists: refresh before sending a request. */
  needsRefresh: () => {
    const s = synced();
    if (s.clockSkewed || !isLive(s, s.refreshToken)) return false;
    return !s.accessToken || isExpired(s.accessToken);
  },
  setToken(token: string | null) {
    const s = state();
    storeTrace('store.setToken', { present: token !== null });
    s.accessToken = token;
    persistToken(s, CFG_KEYS.accessToken.key, token);
    markCookiesSeen(s);
    emit(s);
  },
  setRefreshToken(token: string | null) {
    const s = state();
    storeTrace('store.setRefreshToken', { present: token !== null });
    s.refreshToken = token;
    persistToken(s, CFG_KEYS.refreshToken.key, token);
    markCookiesSeen(s);
    emit(s);
  },
  /**
   * Persist a token pair: the one write path for sign-in flows and the refresh. `refresh: undefined` keeps the
   * current refresh token (an access-only rotation); `null` drops it.
   */
  setSession(session: { access: string; refresh?: string | null }) {
    const s = state();
    storeTrace('store.setSession', {
      refresh: session.refresh === undefined ? 'kept' : session.refresh === null ? 'dropped' : 'set',
    });
    s.accessToken = session.access;
    persistToken(s, CFG_KEYS.accessToken.key, s.accessToken);
    if (session.refresh !== undefined) {
      s.refreshToken = session.refresh;
      persistToken(s, CFG_KEYS.refreshToken.key, session.refresh);
    }
    markCookiesSeen(s);
    emit(s);
  },
  clearSession() {
    const s = state();
    storeTrace('store.clear');
    s.accessToken = null;
    s.refreshToken = null;
    persistToken(s, CFG_KEYS.accessToken.key, null);
    persistToken(s, CFG_KEYS.refreshToken.key, null);
    markCookiesSeen(s);
    emit(s);
  },
  clearTokens() { auth.clearSession(); },
  /** An API key for this page only (`X-API-Key`); wins over the persisted key and `NEXT_PUBLIC_API_KEY`. */
  setApiKey(value: string | null) { state().apiKeyOverride = value; },
  setApiKeyPersist(value: string | null) {
    const s = state();
    s.apiKey = value;
    s.apiKeyOverride = null;
    if (value) cfgStorage.write(CFG_KEYS.apiKey.key, value, 'local');
    else cfgStorage.remove(CFG_KEYS.apiKey.key, 'local');
  },
  /** Drop both the page key and the persisted key; `NEXT_PUBLIC_API_KEY` applies again. */
  clearApiKey() {
    const s = state();
    s.apiKeyOverride = null;
    s.apiKey = null;
    cfgStorage.remove(CFG_KEYS.apiKey.key, 'local');
  },
  getApiKey: () => {
    const s = state();
    return s.apiKeyOverride ?? s.apiKey ?? defaultApiKey();
  },
  getLocale: () => state().locale ?? browserLocale(),
  setLocale(value: string | null) { state().locale = value; },
  getStorageMode: () => 'cookie' as const,
  /** Tokens are kept in cookies only. Another mode is not applied, and says so once instead of failing silently. */
  setStorageMode(mode: 'cookie' | 'localStorage' | 'sessionStorage') {
    if (mode === 'cookie') return;
    warnOnce(state(), `storage-mode:${String(mode)}`, `setStorageMode(${JSON.stringify(mode)}) is not supported: session tokens are kept in cookies only.`);
  },
  setCookieDomain(domain: 'auto' | string | false) {
    state().cookieDomain = domain;
    cfgStorage.setCookieDomain(domain);
  },
  /** The `Domain` token cookies are written with; `null` = host-only. */
  getCookieDomain: (): string | null => {
    const s = state();
    if (s.cookieDomain !== undefined) cfgStorage.setCookieDomain(s.cookieDomain);
    return cfgStorage.cookieDomain();
  },
  setTimezone(value: string | null) { state().timezone = value ?? browserTimezone(); },
  getTimezone: () => state().timezone ?? browserTimezone(),
  getClientId: () => browserClientId(state()),
  setClientId(value: string | null) {
    state().clientId = value;
    if (value) cfgStorage.write(CFG_KEYS.clientId.key, value, 'local');
    else cfgStorage.remove(CFG_KEYS.clientId.key, 'local');
  },
  getWithCredentials: () => state().withCredentials,
  setWithCredentials(value: boolean) { state().withCredentials = value; },
  getBaseUrl: () => getApiOrigin() ?? '',
  /** Alias of `setApiOrigin`: an invalid value warns once and is ignored, `null` or `''` clears. Returns the result. */
  setBaseUrl(value: string | null): string | null {
    return setApiOrigin(value);
  },
  setRefreshHandler(handler: RefreshHandler | null) { state().refreshHandler = handler; },
  /**
   * Refresh the access token once for every caller in the page (single flight) and, where Web Locks exist, one
   * tab at a time (H1.2). Inside the lock the tokens are re-read: if another tab has already rotated them, their
   * access token is adopted with no second call, so a rotating refresh token is never presented twice.
   *
   * Resolves the new access token, or `null` without a refresh token. A 400/401/403 answer, or a body without an
   * access token, ends the session: it is cleared, `onUnauthorized` and `onSessionExpired` fire, and the promise
   * rejects. A failure that says nothing about the token (see `isTransientRefreshError`) rejects with that error
   * and keeps the session.
   */
  async refreshNow(): Promise<string | null> {
    const s = synced();
    if (!s.refreshToken) return null;
    if (!s.refreshInflight) {
      const startedRefresh = s.refreshToken;
      const startedAccess = s.accessToken;
      storeTrace('refresh.start', { locked: webLocks() !== null });
      const run = async (): Promise<string | null> => {
        const live = synced();
        const current = live.refreshToken;
        if (!current) return null;
        const rotatedElsewhere = current !== startedRefresh || live.accessToken !== startedAccess;
        if (rotatedElsewhere && live.accessToken && isLive(live, live.accessToken)) {
          storeTrace('refresh', { ok: true, adopted: true });
          return live.accessToken;
        }
        const result = await (live.refreshHandler ?? defaultRefresh)(current);
        if (!result || typeof result.access !== 'string' || !result.access) {
          throw new SessionRefreshRejected('Session refresh returned no access token');
        }
        const rotated = Boolean(result.refresh && result.refresh !== current);
        checkClock(live, result.access);
        auth.setSession({ access: result.access, refresh: result.refresh ?? current });
        storeTrace('refresh', { ok: true, rotated });
        return result.access;
      };
      const locks = webLocks();
      const serialized = async (): Promise<string | null> => (locks ? await locks.request(REFRESH_LOCK, run) : run());
      const inflight = serialized()
        .catch((error: unknown) => {
          const kept = isTransientRefreshError(error);
          traceRefreshFailure(error, kept);
          if (!kept) expire(s, 'refresh-failed');
          throw error;
        })
        .finally(() => {
          if (s.refreshInflight === inflight) s.refreshInflight = null;
        });
      s.refreshInflight = inflight;
    }
    return s.refreshInflight;
  },
  onUnauthorized(callback: (() => void) | null) {
    const s = state();
    s.unauthorized = callback;
    return () => { if (s.unauthorized === callback) s.unauthorized = null; };
  },
  notifyUnauthorized() {
    state().unauthorized?.();
  },
  notifySessionExpired() {
    for (const listener of Array.from(state().expiryListeners)) listener();
  },
  onSessionExpired(callback: () => void) {
    const s = state();
    s.expiryListeners.add(callback);
    return () => { s.expiryListeners.delete(callback); };
  },
  subscribe(listener: Listener) {
    const s = synced();
    installSync(s);
    s.listeners.add(listener);
    // Time may have passed since the last read: settle the snapshot and arm the timer now that someone listens.
    if (updateSnapshot(s)) queueNotify(s);
    armExpiryTimer(s);
    return () => {
      s.listeners.delete(listener);
      if (s.listeners.size === 0) armExpiryTimer(s);
    };
  },
  /** Referentially stable until the session changes (`useSyncExternalStore` contract). */
  getSnapshot: (): SessionSnapshot => synced().snapshot,
  getServerSnapshot: (): SessionSnapshot => state().serverSnapshot,
  clientHeaders() {
    const s = synced();
    const headers: Record<string, string> = {};
    if (s.accessToken) headers.Authorization = `Bearer ${s.accessToken}`;
    const resolvedApiKey = s.apiKeyOverride ?? s.apiKey ?? defaultApiKey();
    if (resolvedApiKey) headers['X-API-Key'] = resolvedApiKey;
    const resolvedLocale = s.locale ?? browserLocale();
    if (resolvedLocale) headers['Accept-Language'] = resolvedLocale;
    const resolvedTimezone = s.timezone ?? browserTimezone();
    if (resolvedTimezone) headers['X-Timezone'] = resolvedTimezone;
    headers['X-Client-Time'] = new Date().toISOString();
    const resolvedClientId = browserClientId(s);
    if (resolvedClientId) headers['X-Client-Id'] = resolvedClientId;
    return headers;
  },
  get access_token() { return synced().accessToken; },
  get refresh_token() { return synced().refreshToken; },
  get api_key() { return state().apiKey; },
};

export type AuthStore = typeof auth;
