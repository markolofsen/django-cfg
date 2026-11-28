// @vitest-environment jsdom
/**
 * H1.1 and H1.2: the session follows token `exp`, other tabs, and one refresh at a time across tabs.
 *
 * jsdom has one window, so "the other tab" is played by `otherTab`: it does what the store in another tab does
 * (writes the token cookies and bumps the localStorage signal), and delivers the `storage` event the browser would
 * raise here. A same-page second copy of the module needs no event at all (shared-store.test.ts).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from './reset-runtime';

const API = 'https://api.example.test';
const ACCESS = 'cfg.auth.access_token';
const REFRESH = 'cfg.auth.refresh_token';
const SIGNAL = 'cfg.auth.session_signal';
const PROFILE = '/cfg/accounts/profile/';
const REFRESH_PATH = '/cfg/accounts/token/refresh/';

const b64url = (value: unknown) => Buffer.from(JSON.stringify(value)).toString('base64url');
/** A JWT-shaped token that expires `inSeconds` from now (negative: already expired). */
const jwt = (name: string, inSeconds: number) =>
  `${b64url({ alg: 'none' })}.${b64url({ sub: name, exp: Math.floor(Date.now() / 1000) + inSeconds })}.sig`;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

function clearCookies(): void {
  for (const cookie of document.cookie.split(';')) {
    const name = cookie.split('=')[0]?.trim();
    if (name) document.cookie = `${name}=; Max-Age=0; Path=/`;
  }
}

/** What another tab's store does when it signs in, rotates or signs out, as this tab sees it. */
function otherTab(tokens: { access: string | null; refresh: string | null }): void {
  for (const [key, value] of [[ACCESS, tokens.access], [REFRESH, tokens.refresh]] as const) {
    document.cookie = value === null
      ? `${encodeURIComponent(key)}=; Max-Age=0; Path=/`
      : `${encodeURIComponent(key)}=${encodeURIComponent(value)}; Path=/`;
  }
  const previous = localStorage.getItem(SIGNAL);
  const next = `${Date.now()}.other`;
  window.dispatchEvent(new StorageEvent('storage', {
    key: SIGNAL,
    oldValue: previous,
    newValue: next,
    storageArea: localStorage,
  }));
}

async function load() {
  const origin = await import('../api-origin');
  const store = await import('../auth');
  const mutator = await import('../orval-mutator');
  origin.configureApi({ apiUrl: API });
  return { ...store, ...mutator };
}

beforeEach(() => {
  vi.unstubAllGlobals();
  resetRuntimeSlots();
  clearCookies();
  localStorage.clear();
  vi.resetModules();
});

afterEach(() => {
  vi.useRealTimers();
});

describe('isAuthenticated respects exp', () => {
  it.each<[string, () => { access: string | null; refresh: string | null }, boolean, boolean]>([
    ['live access, no refresh', () => ({ access: jwt('a', 300), refresh: null }), true, false],
    ['expired access, no refresh: signed out', () => ({ access: jwt('a', -10), refresh: null }), false, false],
    ['expired access, live refresh: refresh first', () => ({ access: jwt('a', -10), refresh: jwt('r', 3600) }), true, true],
    ['no access, live refresh: refresh first', () => ({ access: null, refresh: jwt('r', 3600) }), true, true],
    ['expired access, expired refresh: signed out', () => ({ access: jwt('a', -10), refresh: jwt('r', -5) }), false, false],
    ['live access, expired refresh', () => ({ access: jwt('a', 300), refresh: jwt('r', -5) }), true, false],
    ['tokens without exp count while present', () => ({ access: 'opaque-access', refresh: null }), true, false],
  ])('%s', async (_label, tokens, authenticated, needsRefresh) => {
    const { access, refresh } = tokens();
    if (access) document.cookie = `${ACCESS}=${access}; Path=/`;
    if (refresh) document.cookie = `${REFRESH}=${refresh}; Path=/`;
    const { auth } = await load();

    expect(auth.isAuthenticated()).toBe(authenticated);
    expect(auth.getSnapshot().status).toBe(authenticated ? 'authenticated' : 'anonymous');
    expect(auth.needsRefresh()).toBe(needsRefresh);
  });

  it('refreshes before sending a request whose access token has expired', async () => {
    const fresh = jwt('fresh', 300);
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(json({ access: fresh, refresh: jwt('r2', 3600) }))
      .mockResolvedValueOnce(json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { auth, djangoFetch } = await load();
    auth.setSession({ access: jwt('stale', -10), refresh: jwt('r1', 3600) });

    await expect(djangoFetch(PROFILE)).resolves.toEqual({ ok: true });

    expect(fetchMock.mock.calls.map(([url]) => String(url))).toEqual([`${API}${REFRESH_PATH}`, `${API}${PROFILE}`]);
    expect(new Headers((fetchMock.mock.calls[1]?.[1] as RequestInit).headers).get('Authorization')).toBe(`Bearer ${fresh}`);
  });

  it('does not refresh first for a flagged sign-in step', async () => {
    const fetchMock = vi.fn(async () => json({ access: 'x', refresh: 'y' }));
    vi.stubGlobal('fetch', fetchMock);
    const { auth, djangoFetch } = await load();
    auth.setSession({ access: jwt('stale', -10), refresh: jwt('r1', 3600) });

    await djangoFetch('/cfg/accounts/otp/verify/', { method: 'POST', skipAuthRefresh: true });

    expect(fetchMock.mock.calls.map(([url]) => String(url))).toEqual([`${API}/cfg/accounts/otp/verify/`]);
  });

  it('stops trusting exp on a page whose clock makes fresh tokens look expired', async () => {
    // The server issues a token that is already "expired" by this device's clock: the clock is ahead.
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(json({ access: jwt('fresh-but-skewed', -30), refresh: jwt('r2', 3600) }))
      .mockImplementation(async () => json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { auth, djangoFetch } = await load();
    auth.setSession({ access: 'opaque', refresh: jwt('r1', 3600) });
    await auth.refreshNow();

    await djangoFetch(PROFILE);
    await djangoFetch(PROFILE);

    // One refresh, then plain requests: no refresh before every request.
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(auth.needsRefresh()).toBe(false);
    expect(auth.isAuthenticated()).toBe(true);
  });
});

describe('the expiry timer', () => {
  it('turns the snapshot anonymous when the last live token expires, and tells subscribers', async () => {
    vi.useFakeTimers({ now: new Date('2026-11-23T10:00:00Z') });
    const { auth } = await load();
    auth.setToken(jwt('a', 60));
    const listener = vi.fn();
    auth.subscribe(listener);
    expect(auth.getSnapshot().status).toBe('authenticated');

    await vi.advanceTimersByTimeAsync(59_000);
    expect(listener).not.toHaveBeenCalled();

    await vi.advanceTimersByTimeAsync(2_000);
    expect(listener).toHaveBeenCalledTimes(1);
    expect(auth.getSnapshot().status).toBe('anonymous');
    expect(auth.isAuthenticated()).toBe(false);
  });

  it('keeps the session past the access exp while the refresh token lives', async () => {
    vi.useFakeTimers({ now: new Date('2026-11-23T10:00:00Z') });
    const { auth } = await load();
    auth.setSession({ access: jwt('a', 60), refresh: jwt('r', 600) });
    const listener = vi.fn();
    auth.subscribe(listener);

    await vi.advanceTimersByTimeAsync(61_000);
    expect(auth.getSnapshot().status).toBe('authenticated');
    expect(auth.needsRefresh()).toBe(true);

    await vi.advanceTimersByTimeAsync(540_000);
    expect(auth.getSnapshot().status).toBe('anonymous');
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('arms no timer when nobody listens', async () => {
    vi.useFakeTimers();
    const { auth } = await load();
    auth.setToken(jwt('a', 60));

    expect(vi.getTimerCount()).toBe(0);
    const unsubscribe = auth.subscribe(() => {});
    expect(vi.getTimerCount()).toBe(1);
    unsubscribe();
    expect(vi.getTimerCount()).toBe(0);
  });
});

describe('another tab', () => {
  it('hears about a write here through the localStorage signal, which carries no token', async () => {
    const { auth } = await load();
    expect(localStorage.getItem(SIGNAL)).toBeNull();

    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
    const afterSignIn = localStorage.getItem(SIGNAL);
    auth.clearSession();

    expect(afterSignIn).toMatch(/\S/);
    expect(localStorage.getItem(SIGNAL)).not.toBe(afterSignIn);
    expect(`${afterSignIn} ${localStorage.getItem(SIGNAL)}`).not.toMatch(/access-1|refresh-1/);
  });

  it('signs in here when it signs in there', async () => {
    const { auth } = await load();
    const listener = vi.fn();
    auth.subscribe(listener);
    expect(auth.getSnapshot().status).toBe('anonymous');

    otherTab({ access: 'access-b', refresh: 'refresh-b' });
    await Promise.resolve();

    expect(listener).toHaveBeenCalledTimes(1);
    expect(auth.getSnapshot()).toMatchObject({ status: 'authenticated', accessToken: 'access-b' });
  });

  it('signs out here when it signs out there', async () => {
    const { auth } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
    const listener = vi.fn();
    auth.subscribe(listener);

    otherTab({ access: null, refresh: null });
    await Promise.resolve();

    expect(listener).toHaveBeenCalledTimes(1);
    expect(auth.getSnapshot().status).toBe('anonymous');
  });

  it.each(['focus', 'visibilitychange'] as const)(
    'picks up a cookie written by another subdomain (no storage event) on %s',
    async (eventName) => {
      const { auth } = await load();
      const listener = vi.fn();
      auth.subscribe(listener);

      document.cookie = `${ACCESS}=from-sso; Path=/`;
      if (eventName === 'focus') window.dispatchEvent(new Event('focus'));
      else {
        Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'visible' });
        document.dispatchEvent(new Event('visibilitychange'));
      }
      await Promise.resolve();

      expect(listener).toHaveBeenCalledTimes(1);
      expect(auth.getSnapshot().accessToken).toBe('from-sso');
    },
  );

  it('ignores storage events for unrelated keys', async () => {
    const { auth } = await load();
    const listener = vi.fn();
    auth.subscribe(listener);

    window.dispatchEvent(new StorageEvent('storage', { key: 'cfg.ui.state', newValue: '{}', storageArea: localStorage }));
    await Promise.resolve();

    expect(listener).not.toHaveBeenCalled();
  });
});

describe('one refresh at a time across tabs (Web Locks)', () => {
  /** A LockManager that grants in order and lets a test run "another tab" before a waiting callback. */
  function fakeLocks(beforeGrant?: () => void) {
    const names: string[] = [];
    let tail: Promise<unknown> = Promise.resolve();
    const locks = {
      request: vi.fn((name: string, callback: () => Promise<unknown>) => {
        names.push(name);
        const granted = tail.then(() => {
          beforeGrant?.();
          return callback();
        });
        tail = granted.catch(() => undefined);
        return granted;
      }),
    };
    vi.stubGlobal('navigator', { ...navigator, locks });
    return { locks, names };
  }

  it('refreshes inside the djangocfg.api.refresh lock', async () => {
    const { names } = fakeLocks();
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(json({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(json({ access: 'access-2', refresh: 'refresh-2' }))
      .mockResolvedValueOnce(json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { auth, djangoFetch } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    await expect(djangoFetch(PROFILE)).resolves.toEqual({ ok: true });

    expect(names).toEqual(['djangocfg.api.refresh']);
    expect(auth.getRefreshToken()).toBe('refresh-2');
  });

  it('adopts the tokens another tab rotated while this one waited, without a second refresh call', async () => {
    fakeLocks(() => otherTab({ access: 'access-from-b', refresh: 'refresh-from-b' }));
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(json({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { auth, djangoFetch } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    await expect(djangoFetch(PROFILE)).resolves.toEqual({ ok: true });

    const urls = fetchMock.mock.calls.map(([url]) => String(url));
    expect(urls).toEqual([`${API}${PROFILE}`, `${API}${PROFILE}`]);
    expect(new Headers((fetchMock.mock.calls[1]?.[1] as RequestInit).headers).get('Authorization')).toBe('Bearer access-from-b');
    expect([auth.getToken(), auth.getRefreshToken()]).toEqual(['access-from-b', 'refresh-from-b']);
  });

  it('falls back to the in-page single flight without Web Locks', async () => {
    expect((navigator as Navigator & { locks?: unknown }).locks).toBeUndefined();
    let refreshes = 0;
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (String(input).includes(REFRESH_PATH)) {
        refreshes += 1;
        return json({ access: 'access-2', refresh: 'refresh-2' });
      }
      return new Headers(init?.headers).get('Authorization') === 'Bearer access-2'
        ? json({ ok: true })
        : json({ detail: 'expired' }, 401);
    }));
    const { auth, djangoFetch } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    await Promise.all([djangoFetch('/apix/a/'), djangoFetch('/apix/b/'), djangoFetch('/apix/c/')]);

    expect(refreshes).toBe(1);
  });
});
