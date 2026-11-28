// @vitest-environment jsdom
/**
 * H1.6 store methods that were missing or silent (`setApiKey`, `clearApiKey`, `setStorageMode`, `setBaseUrl`) and
 * H1.7 store events in the auth trace.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from './reset-runtime';

const API = 'https://api.example.test';
const PROFILE = '/cfg/accounts/profile/';

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

beforeEach(() => {
  vi.unstubAllGlobals();
  resetRuntimeSlots();
  for (const cookie of document.cookie.split(';')) {
    const name = cookie.split('=')[0]?.trim();
    if (name) document.cookie = `${name}=; Max-Age=0; Path=/`;
  }
  localStorage.clear();
  const g = globalThis as Record<string, unknown>;
  delete g.__cfgAuthTrace;
  delete g.__cfgAuthTraceQ;
  vi.resetModules();
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe('API key', () => {
  it('prefers the page key, then the persisted key, then NEXT_PUBLIC_API_KEY', async () => {
    vi.stubEnv('NEXT_PUBLIC_API_KEY', 'env-key');
    const { auth } = await import('../auth');
    expect(auth.getApiKey()).toBe('env-key');

    auth.setApiKeyPersist('stored-key');
    expect(auth.getApiKey()).toBe('stored-key');
    expect(localStorage.getItem('cfg.auth.api_key')).toBe('stored-key');

    auth.setApiKey('page-key');
    expect(auth.getApiKey()).toBe('page-key');
    expect(auth.clientHeaders()['X-API-Key']).toBe('page-key');
    expect(localStorage.getItem('cfg.auth.api_key')).toBe('stored-key');

    auth.setApiKey(null);
    expect(auth.getApiKey()).toBe('stored-key');

    auth.setApiKey('page-key');
    auth.clearApiKey();
    expect(auth.getApiKey()).toBe('env-key');
    expect(localStorage.getItem('cfg.auth.api_key')).toBeNull();
  });

  it('sends no X-API-Key when none is set', async () => {
    vi.stubEnv('NEXT_PUBLIC_API_KEY', undefined);
    const { auth } = await import('../auth');

    expect(auth.getApiKey()).toBeNull();
    expect(auth.clientHeaders()).not.toHaveProperty('X-API-Key');
  });
});

describe('no silent no-ops', () => {
  it('setBaseUrl is setApiOrigin: it applies, returns the origin, and warns once on a bad value', async () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const { auth } = await import('../auth');
    const { resolveApiUrl } = await import('../api-origin');

    expect(auth.setBaseUrl(`${API}/`)).toBe(API);
    expect(auth.getBaseUrl()).toBe(API);
    expect(resolveApiUrl(PROFILE)).toBe(`${API}${PROFILE}`);

    auth.setBaseUrl('not a url');
    auth.setBaseUrl('not a url');
    expect(warn).toHaveBeenCalledTimes(1);
    expect(auth.getBaseUrl()).toBe(API);
  });

  it("setStorageMode keeps cookies and says so once for another mode", async () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const { auth } = await import('../auth');

    auth.setStorageMode('cookie');
    expect(warn).not.toHaveBeenCalled();
    auth.setStorageMode('localStorage');
    auth.setStorageMode('localStorage');

    expect(warn).toHaveBeenCalledTimes(1);
    expect(String(warn.mock.calls[0]?.[0])).toMatch(/cookies only/);
    expect(auth.getStorageMode()).toBe('cookie');
  });
});

describe('store events in the auth trace (H1.7)', () => {
  type Call = [string, Record<string, unknown> | undefined];

  function installSink(): Call[] {
    const calls: Call[] = [];
    (globalThis as Record<string, unknown>).__cfgAuthTrace = (ev: string, fields?: Record<string, unknown>) => {
      calls.push([ev, fields]);
    };
    return calls;
  }

  it('records session writes, refresh, expiry and a sign-in refusal, with no token in any field', async () => {
    const calls = installSink();
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(json({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(json({ access: 'access-2', refresh: 'refresh-2' }))
      .mockResolvedValueOnce(json({ ok: true }))
      .mockResolvedValueOnce(json({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(json({ detail: 'Token is blacklisted' }, 401))
      .mockResolvedValueOnce(json({ detail: 'Wrong code' }, 401)));
    const { configureApi } = await import('../api-origin');
    const { auth } = await import('../auth');
    const { djangoFetch } = await import('../orval-mutator');
    configureApi({ apiUrl: API });

    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
    await djangoFetch(PROFILE);
    await djangoFetch(PROFILE).catch(() => undefined);
    await djangoFetch('/cfg/accounts/otp/verify/?code=123456', { method: 'POST', skipAuthRefresh: true })
      .catch(() => undefined);

    const events = calls.map(([ev]) => ev);
    expect(events).toEqual([
      'store.setSession',
      'refresh.start',
      'store.setSession',
      'refresh',
      'refresh.start',
      'refresh',
      'store.expire',
      'store.clear',
      '401.passthrough',
    ]);
    expect(calls[3]?.[1]).toMatchObject({ ok: true, rotated: true });
    expect(calls[5]?.[1]).toMatchObject({ ok: false, status: 401, kept: false });
    expect(calls[6]?.[1]).toMatchObject({ why: 'refresh-failed' });
    expect(calls[8]?.[1]).toEqual({ path: '/cfg/accounts/otp/verify/' });

    const written = JSON.stringify(calls);
    for (const secret of ['access-1', 'access-2', 'refresh-1', 'refresh-2', '123456']) {
      expect(written).not.toContain(secret);
    }
  });

  it('records a refresh that keeps the session, and an expired session after a 401', async () => {
    const calls = installSink();
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(json({ detail: 'expired' }, 401))
      .mockRejectedValueOnce(new TypeError('fetch failed'))
      .mockResolvedValueOnce(json({ detail: 'no' }, 401)));
    const { configureApi } = await import('../api-origin');
    const { auth } = await import('../auth');
    const { djangoFetch } = await import('../orval-mutator');
    configureApi({ apiUrl: API });

    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
    await djangoFetch(PROFILE).catch(() => undefined);
    auth.setRefreshToken(null);
    await djangoFetch(PROFILE).catch(() => undefined);

    expect(calls.find(([ev, f]) => ev === 'refresh' && f?.ok === false)?.[1])
      .toMatchObject({ why: 'NetworkError', kept: true });
    expect(calls.find(([ev]) => ev === 'store.expire')?.[1]).toEqual({ why: '401', path: PROFILE });
  });

  it('queues events until the reader installs, and the reader drains them', async () => {
    const { auth } = await import('../auth');
    auth.setToken('access-1');
    const queue = (globalThis as Record<string, unknown>).__cfgAuthTraceQ as unknown[];
    expect(queue.map((entry) => (entry as unknown[])[1])).toEqual(['store.setToken']);

    // Loading the reader installs it (as the package entry does) and drains the queue.
    const { readAuthTrace } = await import('../../auth/trace');

    expect(readAuthTrace().map((entry) => entry.ev)).toContain('store.setToken');
    expect((globalThis as Record<string, unknown>).__cfgAuthTraceQ).toEqual([]);
    expect(JSON.stringify(readAuthTrace())).not.toContain('access-1');
  });
});
