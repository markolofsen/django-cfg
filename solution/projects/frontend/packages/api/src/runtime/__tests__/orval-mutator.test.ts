import { beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from './reset-runtime';

describe('djangoFetch runtime transport', () => {
  beforeEach(async () => {
    vi.unstubAllGlobals();
    resetRuntimeSlots();
    vi.resetModules();
    const { configureApi } = await import('../api-origin');
    configureApi({ apiUrl: null, allowRelative: false });
  });

  it('resolves generated relative operations against the configured absolute origin', async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    }));
    vi.stubGlobal('fetch', fetchMock);

    const { configureApi } = await import('../api-origin');
    const { djangoFetch } = await import('../orval-mutator');
    configureApi({ apiUrl: 'https://api.example.test/' });

    await expect(djangoFetch<{ ok: boolean }>('/apix/catalog/v1/titles/?limit=10'))
      .resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.example.test/apix/catalog/v1/titles/?limit=10',
      expect.objectContaining({ credentials: 'include' }),
    );
  });

  it('uses the configured origin for the default refresh handler as well', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response('{}', { status: 401 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ access: 'fresh', refresh: 'rotated' }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      }));
    vi.stubGlobal('fetch', fetchMock);

    const { configureApi } = await import('../api-origin');
    const { auth } = await import('../auth');
    const { djangoFetch } = await import('../orval-mutator');
    configureApi({ apiUrl: 'https://api.example.test' });
    auth.setSession({ access: 'stale', refresh: 'old' });

    await expect(djangoFetch<{ ok: boolean }>('/cfg/accounts/profile/'))
      .resolves.toEqual({ ok: true });
    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      'https://api.example.test/cfg/accounts/profile/',
      'https://api.example.test/cfg/accounts/token/refresh/',
      'https://api.example.test/cfg/accounts/profile/',
    ]);
  });

  it('fails closed instead of sending a relative browser request without an origin', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    const { configureApi } = await import('../api-origin');
    const { APIConfigurationError } = await import('../errors');
    const { djangoFetch } = await import('../orval-mutator');
    configureApi({ apiUrl: null, allowRelative: false });

    await expect(djangoFetch('/cfg/accounts/profile/')).rejects.toBeInstanceOf(APIConfigurationError);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it.each([401, 404, 500, 503])('normalizes HTTP %s into APIError without throwing a raw fetch error', async (status) => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ detail: 'unavailable' }), {
      status,
      headers: { 'content-type': 'application/json' },
    })));

    const { configureApi } = await import('../api-origin');
    const { APIError } = await import('../errors');
    const { djangoFetch } = await import('../orval-mutator');
    configureApi({ apiUrl: 'https://api.example.test' });

    await expect(djangoFetch('/apix/catalog/v1/titles/')).rejects.toMatchObject({
      name: 'APIError',
      statusCode: status,
      url: 'https://api.example.test/apix/catalog/v1/titles/',
    });
    try {
      await djangoFetch('/apix/catalog/v1/titles/');
    } catch (error) {
      expect(error).toBeInstanceOf(APIError);
      expect((error as APIError).errorMessage).toBe('unavailable');
    }
  });

  it('normalizes network failures and retains the absolute URL', async () => {
    const cause = new Error('offline');
    vi.stubGlobal('fetch', vi.fn(async () => { throw cause; }));

    const { configureApi } = await import('../api-origin');
    const { NetworkError } = await import('../errors');
    const { djangoFetch } = await import('../orval-mutator');
    configureApi({ apiUrl: 'https://api.example.test' });

    await expect(djangoFetch('/cfg/accounts/profile/')).rejects.toMatchObject({
      name: 'NetworkError',
      url: 'https://api.example.test/cfg/accounts/profile/',
      originalError: cause,
    });
    await expect(djangoFetch('/cfg/accounts/profile/')).rejects.toBeInstanceOf(NetworkError);
  });
});

