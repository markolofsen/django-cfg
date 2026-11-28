// @vitest-environment jsdom
/**
 * The per-operation flags the generator will emit through Orval `requestOptions` (H2.4): `auth: 'none'` and
 * `origin: 'direct'` (`validation` is in validation-events.test.ts), plus the caller's own abort (audit E9).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from './reset-runtime';

const API = 'https://api.example.test';
const PATH = '/cfg/accounts/oauth/providers/';

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

async function load() {
  const origin = await import('../api-origin');
  const store = await import('../auth');
  const errors = await import('../errors');
  const mutator = await import('../orval-mutator');
  origin.configureApi({ apiUrl: API });
  return { ...origin, ...store, ...errors, ...mutator };
}

beforeEach(() => {
  vi.unstubAllGlobals();
  resetRuntimeSlots();
  vi.resetModules();
});

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("auth: 'none'", () => {
  it('sends no Authorization header while a session exists, and keeps the other transport headers', async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { auth, djangoFetch } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
    auth.setApiKeyPersist('app-key');

    await djangoFetch(PATH, { auth: 'none' });

    const headers = new Headers(fetchMock.mock.calls[0]?.[1]?.headers);
    expect(headers.has('Authorization')).toBe(false);
    expect(headers.get('X-API-Key')).toBe('app-key');
    expect(headers.get('X-Client-Id')).toMatch(/\S/);
  });

  it('does not refresh on a 401 and leaves the session alone', async () => {
    const fetchMock = vi.fn(async () => json({ detail: 'nope' }, 401));
    vi.stubGlobal('fetch', fetchMock);
    const { APIError, auth, djangoFetch } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
    const expired = vi.fn();
    const unauthorized = vi.fn();
    auth.onSessionExpired(expired);
    auth.onUnauthorized(unauthorized);

    const failure = await djangoFetch(PATH, { auth: 'none' }).catch((error: unknown) => error);

    expect(failure).toBeInstanceOf(APIError);
    expect((failure as InstanceType<typeof APIError>).statusCode).toBe(401);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect([auth.getToken(), auth.getRefreshToken()]).toEqual(['access-1', 'refresh-1']);
    expect(expired).not.toHaveBeenCalled();
    expect(unauthorized).not.toHaveBeenCalled();
  });

  it('still sends an Authorization header the caller passes', async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { auth, djangoFetch } = await load();
    auth.setToken('access-1');

    await djangoFetch(PATH, { auth: 'none', headers: { Authorization: 'Bearer caller' } });

    expect(new Headers(fetchMock.mock.calls[0]?.[1]?.headers).get('Authorization')).toBe('Bearer caller');
  });

  it('keeps refresh and retry for an operation without the flag', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(json({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(json({ access: 'access-2', refresh: 'refresh-2' }))
      .mockResolvedValueOnce(json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { auth, djangoFetch } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    await expect(djangoFetch('/apix/crm/me/')).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });
});

describe('the flags never reach fetch', () => {
  it('strips schema, auth, origin, validation and skipAuthRefresh from the RequestInit', async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { djangoFetch } = await load();

    await djangoFetch(PATH, { auth: 'none', origin: 'direct', validation: 'strict', skipAuthRefresh: true });

    const init = fetchMock.mock.calls[0]?.[1] as Record<string, unknown>;
    for (const key of ['schema', 'auth', 'origin', 'validation', 'skipAuthRefresh']) expect(init).not.toHaveProperty(key);
  });
});

describe('a request the caller aborts', () => {
  it('rejects with the original AbortError, not NetworkError', async () => {
    vi.stubGlobal('fetch', vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      await new Promise((resolve) => setTimeout(resolve, 0));
      init?.signal?.throwIfAborted();
      return json({ ok: true });
    }));
    const { NetworkError, djangoFetch } = await load();
    const controller = new AbortController();

    const pending = djangoFetch(PATH, { signal: controller.signal });
    controller.abort();
    const failure = await pending.catch((error: unknown) => error);

    expect(failure).not.toBeInstanceOf(NetworkError);
    expect((failure as Error).name).toBe('AbortError');
  });

  it('rethrows the abort reason unchanged when the caller passes one', async () => {
    const reason = new Error('route changed');
    vi.stubGlobal('fetch', vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      await new Promise((resolve) => setTimeout(resolve, 0));
      init?.signal?.throwIfAborted();
      return json({ ok: true });
    }));
    const { djangoFetch } = await load();
    const controller = new AbortController();

    const pending = djangoFetch(PATH, { signal: controller.signal });
    controller.abort(reason);

    await expect(pending).rejects.toBe(reason);
  });

  it('still wraps a real transport failure as NetworkError', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('fetch failed'); }));
    const { NetworkError, djangoFetch } = await load();

    await expect(djangoFetch(PATH)).rejects.toBeInstanceOf(NetworkError);
  });
});

describe('setWithCredentials', () => {
  const credentialsOf = (fetchMock: ReturnType<typeof vi.fn>) =>
    fetchMock.mock.calls.map(([, init]) => (init as RequestInit).credentials);

  it("is honoured by djangoFetch: 'include' by default, 'same-origin' when switched off, a caller's value wins", async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { auth, djangoFetch } = await load();

    await djangoFetch('/cfg/a/');
    auth.setWithCredentials(false);
    await djangoFetch('/cfg/b/');
    await djangoFetch('/cfg/c/', { credentials: 'include' });

    expect(credentialsOf(fetchMock)).toEqual(['include', 'same-origin', 'include']);
  });
});
