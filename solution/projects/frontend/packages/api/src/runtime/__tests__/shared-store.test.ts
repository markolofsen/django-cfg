// @vitest-environment jsdom
/**
 * H0.5: one auth store per page. The published package inlines the runtime into each entry (`index`, `auth`,
 * `clients`, `hooks`), so a page can hold several copies of this module. `vi.resetModules()` between two imports
 * gives two real copies; the state they share is the `globalThis` slot.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from './reset-runtime';

const API = 'https://api.example.test';
const ACCESS_COOKIE = 'cfg.auth.access_token';

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

/** A fresh copy of the runtime modules, as a second bundle in the page would load them. */
async function loadCopy() {
  vi.resetModules();
  const store = await import('../auth');
  const origin = await import('../api-origin');
  const mutator = await import('../orval-mutator');
  return { ...store, ...origin, ...mutator };
}

beforeEach(() => {
  vi.unstubAllGlobals();
  resetRuntimeSlots();
  for (const cookie of document.cookie.split(';')) {
    const name = cookie.split('=')[0]?.trim();
    if (name) document.cookie = `${name}=; Max-Age=0; Path=/`;
  }
  localStorage.clear();
});

describe('two copies of the runtime in one page', () => {
  it('are separate module instances', async () => {
    const a = await loadCopy();
    const b = await loadCopy();

    expect(a.auth).not.toBe(b.auth);
    expect(a.djangoFetch).not.toBe(b.djangoFetch);
  });

  it('attach a token set through one copy to a request from the other, at the origin set through the first', async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const a = await loadCopy();
    const b = await loadCopy();

    a.configureApi({ apiUrl: API });
    a.auth.setSession({ access: 'access-a', refresh: 'refresh-a' });
    await b.djangoFetch('/cfg/accounts/profile/');

    expect(String(fetchMock.mock.calls[0]?.[0])).toBe(`${API}/cfg/accounts/profile/`);
    expect(new Headers(fetchMock.mock.calls[0]?.[1]?.headers).get('Authorization')).toBe('Bearer access-a');
    expect(b.auth.getToken()).toBe('access-a');
    expect(b.auth.getSnapshot()).toBe(a.auth.getSnapshot());
  });

  it('fire a session-expired handler registered on one copy for a 401 seen by the other', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => json({ detail: 'Token is invalid' }, 401)));
    const a = await loadCopy();
    const b = await loadCopy();
    a.configureApi({ apiUrl: API });
    a.auth.setToken('access-stale');
    const expired = vi.fn();
    const unauthorized = vi.fn();
    a.auth.onSessionExpired(expired);
    a.auth.onUnauthorized(unauthorized);

    await expect(b.djangoFetch('/apix/crm/me/')).rejects.toMatchObject({ statusCode: 401 });

    expect(expired).toHaveBeenCalledTimes(1);
    expect(unauthorized).toHaveBeenCalledTimes(1);
    expect(a.auth.isAuthenticated()).toBe(false);
  });

  it('notify a subscriber of one copy when the other signs in', async () => {
    const a = await loadCopy();
    const b = await loadCopy();
    const listener = vi.fn();
    a.auth.subscribe(listener);

    b.auth.setSession({ access: 'access-b', refresh: 'refresh-b' });

    expect(listener).toHaveBeenCalledTimes(1);
    expect(a.auth.getSnapshot()).toMatchObject({ status: 'authenticated', accessToken: 'access-b' });
  });

  it('share one refresh for 401s from both copies at once', async () => {
    let refreshes = 0;
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (String(input).includes('/token/refresh/')) {
        refreshes += 1;
        await new Promise((resolve) => setTimeout(resolve, 5));
        return json({ access: 'access-2', refresh: 'refresh-2' });
      }
      const authorization = new Headers(init?.headers).get('Authorization');
      return authorization === 'Bearer access-2' ? json({ ok: true }) : json({ detail: 'expired' }, 401);
    }));
    const a = await loadCopy();
    const b = await loadCopy();
    a.configureApi({ apiUrl: API });
    a.auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    await expect(Promise.all([a.djangoFetch('/apix/one/'), b.djangoFetch('/apix/two/')]))
      .resolves.toEqual([{ ok: true }, { ok: true }]);

    expect(refreshes).toBe(1);
    expect(b.auth.getRefreshToken()).toBe('refresh-2');
  });

  it('share the transport overrides: locale, timezone, client id and API key', async () => {
    const a = await loadCopy();
    const b = await loadCopy();

    a.auth.setLocale('pt-BR');
    a.auth.setTimezone('Asia/Makassar');
    a.auth.setClientId('client-a');
    a.auth.setApiKeyPersist('key-a');
    a.auth.setWithCredentials(false);

    expect(b.auth.clientHeaders()).toMatchObject({
      'Accept-Language': 'pt-BR',
      'X-Timezone': 'Asia/Makassar',
      'X-Client-Id': 'client-a',
      'X-API-Key': 'key-a',
    });
    expect(b.auth.getWithCredentials()).toBe(false);
  });
});

describe('a token cookie changed outside the store', () => {
  it('is picked up on the next read, and subscribers hear about it', async () => {
    const a = await loadCopy();
    const listener = vi.fn();
    a.auth.subscribe(listener);
    const before = a.auth.getSnapshot();

    // What an older copy of the package without the shared slot (or another tab) does.
    document.cookie = `${ACCESS_COOKIE}=outside; Path=/`;

    expect(a.auth.getToken()).toBe('outside');
    const after = a.auth.getSnapshot();
    expect(after).not.toBe(before);
    expect(after).toMatchObject({ status: 'authenticated', accessToken: 'outside' });
    expect(a.auth.getSnapshot()).toBe(after);
    await Promise.resolve();
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('is read as a sign-out when another writer removes it', async () => {
    const a = await loadCopy();
    a.auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    document.cookie = `${ACCESS_COOKIE}=; Max-Age=0; Path=/`;

    expect(a.auth.getToken()).toBeNull();
    expect(a.auth.getRefreshToken()).toBe('refresh-1');
  });
});
