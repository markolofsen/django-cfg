/**
 * A rejected sign-in request is an endpoint error, not session expiry (H1.3).
 *
 * The operation's flags decide, not its URL: the generator sets `skipAuthRefresh` on the 7 sign-in steps and
 * `auth: 'none'` on the public operations. The old URL regex also matched the authenticated
 * `/cfg/totp/backup-codes/` and kept a dead session alive there.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from '../../runtime/__tests__/reset-runtime';

const API = 'https://api.example.test';

const unauthorized = () => new Response('{"detail":"no"}', { status: 401, headers: { 'content-type': 'application/json' } });

describe('sign-in refusal', () => {
  beforeEach(async () => {
    vi.unstubAllGlobals();
    resetRuntimeSlots();
    vi.resetModules();
    const { configureApi } = await import('../../runtime/api-origin');
    configureApi({ apiUrl: API });
  });

  it('a 401 on a flagged sign-in step neither refreshes nor expires the session', async () => {
    const fetchMock = vi.fn(async () => unauthorized());
    vi.stubGlobal('fetch', fetchMock);
    const { auth } = await import('../../runtime/auth');
    const { cfgAccountsOtpVerifyCreate } = await import('../../_api/generated/endpoints/cfg-accounts-otp/cfg-accounts-otp');
    auth.setSession({ access: 'access-stale', refresh: 'refresh-live' });
    const expired = vi.fn();
    const unauthorizedListener = vi.fn();
    auth.onSessionExpired(expired);
    auth.onUnauthorized(unauthorizedListener);

    await expect(cfgAccountsOtpVerifyCreate({ identifier: 'a@example.test', otp: '123456' } as never))
      .rejects.toMatchObject({ statusCode: 401 });

    expect(fetchMock.mock.calls.map(([url]) => String(url))).toEqual([`${API}/cfg/accounts/otp/verify/`]);
    expect(expired).not.toHaveBeenCalled();
    expect(unauthorizedListener).not.toHaveBeenCalled();
    expect(auth.getToken()).toBe('access-stale');
    expect(auth.getRefreshToken()).toBe('refresh-live');
  });

  it("a 401 on an auth: 'none' operation neither refreshes nor expires the session", async () => {
    const fetchMock = vi.fn(async () => unauthorized());
    vi.stubGlobal('fetch', fetchMock);
    const { auth } = await import('../../runtime/auth');
    const { djangoFetch } = await import('../../runtime/orval-mutator');
    auth.setSession({ access: 'access-stale', refresh: 'refresh-live' });
    const expired = vi.fn();
    auth.onSessionExpired(expired);

    await expect(djangoFetch('/cfg/anything/public/', { auth: 'none' })).rejects.toMatchObject({ statusCode: 401 });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(expired).not.toHaveBeenCalled();
    expect(auth.getToken()).toBe('access-stale');
  });

  it('a 401 on an unflagged URL that looks like a sign-in path still expires the session', async () => {
    // No regex any more: only the flag makes a call session-neutral.
    vi.stubGlobal('fetch', vi.fn(async () => unauthorized()));
    const { auth } = await import('../../runtime/auth');
    const { djangoFetch } = await import('../../runtime/orval-mutator');
    auth.setToken('access-stale');
    const expired = vi.fn();
    auth.onSessionExpired(expired);

    await expect(djangoFetch('/cfg/accounts/otp/verify/')).rejects.toMatchObject({ statusCode: 401 });

    expect(expired).toHaveBeenCalledTimes(1);
    expect(auth.isAuthenticated()).toBe(false);
  });

  it('a 401 on the authenticated /cfg/totp/backup-codes/ refreshes, then expires the session', async () => {
    const fetchMock = vi.fn(async () => unauthorized());
    vi.stubGlobal('fetch', fetchMock);
    const { auth } = await import('../../runtime/auth');
    const { cfgTotpBackupCodesRetrieve } = await import(
      '../../_api/generated/endpoints/cfg-totp-backup-codes/cfg-totp-backup-codes'
    );
    auth.setSession({ access: 'access-stale', refresh: 'refresh-dead' });
    const expired = vi.fn();
    auth.onSessionExpired(expired);

    await expect(cfgTotpBackupCodesRetrieve()).rejects.toMatchObject({ statusCode: 401 });

    expect(fetchMock.mock.calls.map(([url]) => String(url))).toEqual([
      `${API}/cfg/totp/backup-codes/`,
      `${API}/cfg/accounts/token/refresh/`,
    ]);
    expect(expired).toHaveBeenCalledTimes(1);
    expect(auth.getToken()).toBeNull();
    expect(auth.getRefreshToken()).toBeNull();
  });

  it('expires a signed-in request that has no usable refresh token', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('{}', { status: 401 })));
    const { auth } = await import('../../runtime/auth');
    const { djangoFetch } = await import('../../runtime/orval-mutator');
    auth.setToken('access-stale');
    const expired = vi.fn();
    auth.onSessionExpired(expired);

    await expect(djangoFetch('/apix/crm/me/')).rejects.toMatchObject({ statusCode: 401 });
    expect(expired).toHaveBeenCalledTimes(1);
    expect(auth.isAuthenticated()).toBe(false);
  });
});
