// @vitest-environment jsdom
/**
 * H0.7: a refresh that fails for a reason that says nothing about the token keeps the session. Only a 400, 401 or
 * 403 from the refresh endpoint, or a body without an access token, signs the user out.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from './reset-runtime';

const API = 'https://api.example.test';
const PROFILE = '/cfg/accounts/profile/';
const REFRESH = '/cfg/accounts/token/refresh/';

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

function stubFetch(...replies: Array<Response | Error>) {
  const queue = [...replies];
  const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => {
    const next = queue.shift();
    if (next === undefined) throw new Error('test: a request nobody expected');
    if (next instanceof Error) throw next;
    return next;
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

async function load() {
  const origin = await import('../api-origin');
  const store = await import('../auth');
  const errors = await import('../errors');
  const mutator = await import('../orval-mutator');
  origin.configureApi({ apiUrl: API });
  store.auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
  const expired = vi.fn();
  const unauthorized = vi.fn();
  store.auth.onSessionExpired(expired);
  store.auth.onUnauthorized(unauthorized);
  return { ...store, ...errors, ...mutator, expired, unauthorized };
}

beforeEach(() => {
  vi.unstubAllGlobals();
  resetRuntimeSlots();
  for (const cookie of document.cookie.split(';')) {
    const name = cookie.split('=')[0]?.trim();
    if (name) document.cookie = `${name}=; Max-Age=0; Path=/`;
  }
  vi.resetModules();
});

describe('a refresh that cannot reach the API', () => {
  it('keeps the session and rejects the original request with NetworkError', async () => {
    const fetchMock = stubFetch(json({ detail: 'Token is expired' }, 401), new TypeError('fetch failed'));
    const { NetworkError, auth, djangoFetch, expired, unauthorized } = await load();

    await expect(djangoFetch(PROFILE)).rejects.toBeInstanceOf(NetworkError);

    expect(fetchMock.mock.calls.map(([url]) => String(url))).toEqual([`${API}${PROFILE}`, `${API}${REFRESH}`]);
    expect([auth.getToken(), auth.getRefreshToken()]).toEqual(['access-1', 'refresh-1']);
    expect(auth.isAuthenticated()).toBe(true);
    expect(expired).not.toHaveBeenCalled();
    expect(unauthorized).not.toHaveBeenCalled();
  });

  it('lets the next 401 try the refresh again, and that one can succeed', async () => {
    stubFetch(
      json({ detail: 'Token is expired' }, 401),
      new TypeError('fetch failed'),
      json({ detail: 'Token is expired' }, 401),
      json({ access: 'access-2', refresh: 'refresh-2' }),
      json({ ok: true }),
    );
    const { auth, djangoFetch } = await load();

    await djangoFetch(PROFILE).catch(() => undefined);
    await expect(djangoFetch(PROFILE)).resolves.toEqual({ ok: true });

    expect([auth.getToken(), auth.getRefreshToken()]).toEqual(['access-2', 'refresh-2']);
  });
});

describe('a refresh that fails for another transient reason', () => {
  it.each([500, 502, 503, 404, 429])('keeps the session on a %s from the refresh endpoint', async (status) => {
    stubFetch(json({ detail: 'Token is expired' }, 401), json({ detail: 'unavailable' }, status));
    const { APIError, auth, djangoFetch, expired } = await load();

    const failure = await djangoFetch(PROFILE).catch((error: unknown) => error);

    expect(failure).toBeInstanceOf(APIError);
    expect(failure).toMatchObject({ statusCode: status, url: `${API}${REFRESH}` });
    expect(auth.getRefreshToken()).toBe('refresh-1');
    expect(expired).not.toHaveBeenCalled();
  });

  it('keeps the session when a custom refresh handler has no API origin', async () => {
    stubFetch(json({ detail: 'Token is expired' }, 401));
    const { APIConfigurationError, auth, djangoFetch, expired } = await load();
    auth.setRefreshHandler(async () => { throw new APIConfigurationError(); });

    await expect(djangoFetch(PROFILE)).rejects.toBeInstanceOf(APIConfigurationError);

    expect(auth.getRefreshToken()).toBe('refresh-1');
    expect(expired).not.toHaveBeenCalled();
  });
});

describe('a refresh the API refuses', () => {
  it.each([400, 401, 403])('clears the session on a %s and fires session-expired once', async (status) => {
    stubFetch(json({ detail: 'Token is expired' }, 401), json({ detail: 'Token is blacklisted' }, status));
    const { APIError, auth, djangoFetch, expired, unauthorized } = await load();

    const failure = await djangoFetch(PROFILE).catch((error: unknown) => error);

    // The caller sees the original 401 of its own request.
    expect(failure).toBeInstanceOf(APIError);
    expect(failure).toMatchObject({ statusCode: 401, url: `${API}${PROFILE}` });
    expect([auth.getToken(), auth.getRefreshToken()]).toEqual([null, null]);
    expect(auth.isAuthenticated()).toBe(false);
    expect(expired).toHaveBeenCalledTimes(1);
    expect(unauthorized).toHaveBeenCalledTimes(1);
  });

  it('clears the session when the refresh answers 2xx without an access token', async () => {
    stubFetch(json({ detail: 'Token is expired' }, 401), json({ refresh: 'refresh-2' }));
    const { auth, djangoFetch, expired } = await load();

    await expect(djangoFetch(PROFILE)).rejects.toMatchObject({ statusCode: 401 });

    expect(auth.isAuthenticated()).toBe(false);
    expect(expired).toHaveBeenCalledTimes(1);
  });

  it('clears the session when refreshNow is called directly and the refresh is refused', async () => {
    stubFetch(json({ detail: 'Token is blacklisted' }, 401));
    const { auth, expired } = await load();

    await expect(auth.refreshNow()).rejects.toMatchObject({ statusCode: 401 });

    expect(auth.isAuthenticated()).toBe(false);
    expect(expired).toHaveBeenCalledTimes(1);
  });
});
