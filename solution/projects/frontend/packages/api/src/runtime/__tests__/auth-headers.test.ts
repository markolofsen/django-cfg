// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from './reset-runtime';

describe('auth transport headers', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    resetRuntimeSlots();
    vi.resetModules();
    localStorage.clear();
    document.cookie = 'NEXT_LOCALE=ru; path=/';
  });

  it('sends the shared djangocfg headers and keeps per-request API keys/client ids authoritative', async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    }));
    vi.stubGlobal('fetch', fetchMock);
    vi.setSystemTime(new Date('2026-01-02T03:04:05.000Z'));

    const { configureApi } = await import('../api-origin');
    const { auth } = await import('../auth');
    const { djangoFetch } = await import('../orval-mutator');
    configureApi({ apiUrl: 'https://api.example.test' });
    auth.setToken('access-token');
    auth.setApiKeyPersist('global-key');
    auth.setLocale(null);
    auth.setTimezone('Asia/Makassar');
    auth.setClientId('stored-client');

    await djangoFetch('/cfg/accounts/profile/', {
      headers: {
        'X-API-Key': 'request-key',
        'X-Client-Id': 'request-client',
        'X-Client-Time': '2026-01-01T00:00:00.000Z',
      },
    });

    const request = fetchMock.mock.calls[0]?.[1] as RequestInit;
    const headers = new Headers(request.headers);
    expect(headers.get('Authorization')).toBe('Bearer access-token');
    expect(headers.get('X-API-Key')).toBe('request-key');
    expect(headers.get('Accept-Language')).toBe('ru');
    expect(headers.get('X-Timezone')).toBe('Asia/Makassar');
    expect(headers.get('X-Client-Time')).toBe('2026-01-01T00:00:00.000Z');
    expect(headers.get('X-Client-Id')).toBe('request-client');
  });

  it('generates and persists a browser client id when one is not supplied', async () => {
    const { auth } = await import('../auth');
    const first = auth.getClientId();
    const second = auth.getClientId();

    expect(first).toEqual(expect.any(String));
    expect(first).toBe(second);
    expect(localStorage.getItem('cfg.client.id')).toBe(first);
  });
});

