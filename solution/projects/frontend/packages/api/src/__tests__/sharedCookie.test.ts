// @vitest-environment jsdom
// @vitest-environment-options {"url": "https://my.example.com/"}
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { readCookie } from '../cookies';
import { CFG_KEYS, createStorage } from '../storage';

const ACCESS = CFG_KEYS.accessToken.key;
const REFRESH = CFG_KEYS.refreshToken.key;

function wipe() {
  localStorage.clear();
  document.cookie.split('; ').forEach((c) => {
    const name = c.split('=')[0];
    document.cookie = `${name}=; Max-Age=0; Path=/`;
    document.cookie = `${name}=; Max-Age=0; Path=/; Domain=example.com`;
  });
}

beforeEach(wipe);

describe('shared cookie domain', () => {
  it('finds the registrable domain by asking the browser', () => {
    const storage = createStorage('cfg');
    expect(storage.cookieDomain()).toBe('example.com');
  });

  it('round-trips and removes a token cookie on the shared domain', () => {
    const storage = createStorage('cfg');
    expect(storage.write(ACCESS, 'jwt', 'cookie')).toBe(true);
    expect(storage.read(ACCESS, 'cookie')).toBe('jwt');
    storage.remove(ACCESS, 'cookie');
    expect(storage.read(ACCESS, 'cookie')).toBeNull();
    expect(document.cookie).not.toContain('cfg.auth.access_token');
  });

  it('a host-only cookie from an older build does not shadow the shared one, and sign-out clears both', () => {
    const storage = createStorage('cfg');
    document.cookie = `${encodeURIComponent(ACCESS)}=old; Path=/`;
    storage.write(ACCESS, 'new', 'cookie');
    expect(storage.read(ACCESS, 'cookie')).toBe('new');
    document.cookie = `${encodeURIComponent(ACCESS)}=stale; Path=/`; // stray host-only twin again
    storage.remove(ACCESS, 'cookie');
    expect(document.cookie).not.toContain('cfg.auth.access_token');
  });

  it('stays host-only when asked', () => {
    const storage = createStorage('cfg', { cookieDomain: false });
    expect(storage.cookieDomain()).toBeNull();
    storage.write(ACCESS, 'jwt', 'cookie');
    expect(storage.read(ACCESS, 'cookie')).toBe('jwt');
  });

  it('honours a forced domain', () => {
    const storage = createStorage('cfg', { cookieDomain: 'example.com' });
    expect(storage.cookieDomain()).toBe('example.com');
  });

  it('clearAll removes the personal cookie keys', () => {
    const storage = createStorage('cfg', { keys: CFG_KEYS });
    storage.write(ACCESS, 'a', 'cookie');
    storage.write(REFRESH, 'r', 'cookie');
    storage.clearAll();
    expect(storage.read(ACCESS, 'cookie')).toBeNull();
    expect(storage.read(REFRESH, 'cookie')).toBeNull();
  });
});

describe('readCookie (SSR header)', () => {
  it('reads an encoded name and value from a Cookie header', () => {
    const header = `a=1; ${encodeURIComponent(ACCESS)}=${encodeURIComponent('x.y.z')}; b=2`;
    expect(readCookie(header, ACCESS)).toBe('x.y.z');
    expect(readCookie(header, 'missing')).toBeNull();
    expect(readCookie(null, ACCESS)).toBeNull();
    expect(readCookie('', ACCESS)).toBeNull();
  });
});

describe('auth store session', () => {
  async function loadAuth() {
    vi.resetModules();
    return (await import('../runtime/auth')).auth;
  }

  it('defaults to the cookie backend and writes the pair there', async () => {
    const auth = await loadAuth();
    expect(auth.getStorageMode()).toBe('cookie');
    auth.setSession({ access: 'A', refresh: 'R' });
    expect(readCookie(document.cookie, ACCESS)).toBe('A');
    expect(readCookie(document.cookie, REFRESH)).toBe('R');
    expect(localStorage.getItem(ACCESS)).toBeNull();
    auth.clearTokens();
    expect(readCookie(document.cookie, ACCESS)).toBeNull();
  });

  it('does not adopt sessions from legacy localStorage keys', async () => {
    localStorage.setItem(ACCESS, 'oldA');
    localStorage.setItem(REFRESH, 'oldR');
    const auth = await loadAuth();
    expect(auth.getToken()).toBeNull();
    expect(auth.getRefreshToken()).toBeNull();
    expect(localStorage.getItem(ACCESS)).toBe('oldA');
    expect(readCookie(document.cookie, REFRESH)).toBeNull();
  });

  it('keeps the API key in localStorage', async () => {
    const auth = await loadAuth();
    auth.setApiKeyPersist('key-1');
    expect(localStorage.getItem('cfg.auth.api_key')).toBe('key-1');
    expect(document.cookie).not.toContain('api_key');
  });
});
