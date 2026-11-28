/**
 * Terminal-401 contract for the Orval fetch mutator.
 *
 * Auth entry points keep their own validation error. A signed-in API request
 * retries once through the refresh store and emits terminal-session events
 * only when the request still cannot be recovered.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from '../../runtime/__tests__/reset-runtime';

describe('Orval mutator 401 handling', () => {
  beforeEach(async () => {
    vi.unstubAllGlobals();
    resetRuntimeSlots();
    vi.resetModules();
    const { configureApi } = await import('../../runtime/api-origin');
    configureApi({ apiUrl: 'https://api.example.test' });
  });

  it('refreshNow rejects and clears a failed refresh session', async () => {
    const { auth } = await import('../../runtime/auth');
    auth.setToken('access-stale');
    auth.setRefreshToken('R-blacklisted');
    auth.setRefreshHandler(async () => { throw new Error('Token is blacklisted'); });

    const onUnauthorized = vi.fn();
    const onExpired = vi.fn();
    auth.onUnauthorized(onUnauthorized);
    auth.onSessionExpired(onExpired);

    await expect(auth.refreshNow()).rejects.toThrow('Token is blacklisted');
    expect(auth.isAuthenticated()).toBe(false);
    expect(onUnauthorized).toHaveBeenCalledTimes(1);
    expect(onExpired).toHaveBeenCalledTimes(1);
  });

  it('refreshNow returns null when there is no refresh token', async () => {
    const { auth } = await import('../../runtime/auth');
    auth.setToken('access-orphan');
    expect(await auth.refreshNow()).toBeNull();
  });

  it('retries a signed-in request and persists rotated tokens', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response('{}', { status: 401 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      }));
    vi.stubGlobal('fetch', fetchMock);

    const { auth } = await import('../../runtime/auth');
    const { djangoFetch } = await import('../../runtime/orval-mutator');
    auth.setSession({ access: 'access-stale', refresh: 'R-old' });
    auth.setRefreshHandler(async () => ({ access: 'access-fresh', refresh: 'R-new' }));
    const onUnauthorized = vi.fn();
    auth.onUnauthorized(onUnauthorized);

    await expect(djangoFetch<{ ok: boolean }>('/apix/crm/me/')).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(auth.getToken()).toBe('access-fresh');
    expect(auth.getRefreshToken()).toBe('R-new');
    expect(onUnauthorized).not.toHaveBeenCalled();
  });

  it('emits terminal events for an unrecoverable signed-in request', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('{}', { status: 401 })));
    const { auth } = await import('../../runtime/auth');
    const { djangoFetch } = await import('../../runtime/orval-mutator');
    auth.setToken('access-orphan');
    const onUnauthorized = vi.fn();
    const onExpired = vi.fn();
    auth.onUnauthorized(onUnauthorized);
    auth.onSessionExpired(onExpired);

    await expect(djangoFetch('/apix/crm/me/')).rejects.toMatchObject({ statusCode: 401 });
    expect(onUnauthorized).toHaveBeenCalledTimes(1);
    expect(onExpired).toHaveBeenCalledTimes(1);
    expect(auth.isAuthenticated()).toBe(false);
  });

  it('does not expire the session for a sign-in refusal (the generated skipAuthRefresh flag)', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('{}', { status: 401 })));
    const { auth } = await import('../../runtime/auth');
    auth.setToken('access-stale');
    const onUnauthorized = vi.fn();
    const onExpired = vi.fn();
    auth.onUnauthorized(onUnauthorized);
    auth.onSessionExpired(onExpired);

    const { cfgAccountsTokenCreate } = await import('../../_api/generated/endpoints/cfg-accounts-auth/cfg-accounts-auth');
    await expect(cfgAccountsTokenCreate({ email: 'a@example.test', password: 'x' } as never))
      .rejects.toMatchObject({ statusCode: 401 });
    expect(onUnauthorized).not.toHaveBeenCalled();
    expect(onExpired).not.toHaveBeenCalled();
    expect(auth.getToken()).toBe('access-stale');
  });
});
