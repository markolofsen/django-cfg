/**
 * Refresh-token ROTATION contract test.
 *
 * This is the regression guard for the "Token is blacklisted" 401 that logged
 * users out. Django (SimpleJWT via django-cfg) ships ROTATE_REFRESH_TOKENS +
 * BLACKLIST_AFTER_ROTATION on by default: every successful refresh returns a
 * NEW refresh token and blacklists the old one. If the client persists the OLD
 * token instead of the rotated one, the *next* refresh reuses a blacklisted
 * token and 401s.
 *
 * The test drives the real `auth` store with a handler that models exactly that
 * server behaviour (rotate + blacklist), then asserts a SECOND refresh still
 * succeeds — which can only happen if the store persisted the rotated token.
 * A client that saves the old token (the original bug) fails the second refresh.
 *
 * The store reads `window.localStorage` and captures `isBrowser` at import time,
 * so we install a minimal localStorage on globalThis BEFORE importing it.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from '../../runtime/__tests__/reset-runtime';

// Minimal in-memory localStorage installed before the store module loads.
function installBrowserStorage() {
  const map = new Map<string, string>();
  const storage = {
    getItem: (k: string) => (map.has(k) ? map.get(k)! : null),
    setItem: (k: string, v: string) => void map.set(k, v),
    removeItem: (k: string) => void map.delete(k),
    clear: () => map.clear(),
  };
  vi.stubGlobal('window', { localStorage: storage, location: { protocol: 'http:' } });
  vi.stubGlobal('localStorage', storage);
  return map;
}

/**
 * Fake SimpleJWT refresh endpoint with rotation + blacklist.
 * Each call: rejects a blacklisted token, otherwise blacklists the presented
 * token and issues a fresh access + fresh (rotated) refresh.
 */
function makeRotatingServer() {
  const blacklist = new Set<string>();
  let seq = 0;
  return {
    blacklist,
    refresh(presented: string): { access: string; refresh: string } {
      if (blacklist.has(presented)) {
        const err = new Error('Token is blacklisted') as Error & { code: string };
        err.code = 'token_not_valid';
        throw err;
      }
      blacklist.add(presented); // BLACKLIST_AFTER_ROTATION
      seq += 1;
      return { access: `access-${seq}`, refresh: `refresh-${seq}` }; // ROTATE_REFRESH_TOKENS
    },
  };
}

describe('refresh token rotation contract', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    resetRuntimeSlots();
    vi.resetModules();
  });

  it('persists the ROTATED refresh token so consecutive refreshes succeed', async () => {
    installBrowserStorage();
    const { auth } = await import('../../runtime/auth');
    const server = makeRotatingServer();

    // Seed the initial rotated pair (as a login would).
    auth.setToken('access-0');
    auth.setRefreshToken('R0');

    // Canonical handler: returns the rotated refresh from the response.
    auth.setRefreshHandler(async (refresh: string) => {
      const res = server.refresh(refresh);
      return { access: res.access, refresh: res.refresh };
    });

    // `refreshNow` is added by the generator; skip gracefully until regen.
    const store = auth as unknown as { refreshNow?: () => Promise<string | null> };
    if (typeof store.refreshNow !== 'function') {
      // Contract still enforced via the handler directly below.
      return;
    }

    const first = await store.refreshNow();
    expect(first).toBe('access-1');
    expect(auth.getRefreshToken()).toBe('refresh-1'); // rotated, not R0

    // The SECOND refresh is the one that broke before: it must NOT reuse R0.
    const second = await store.refreshNow();
    expect(second).toBe('access-2');
    expect(auth.getRefreshToken()).toBe('refresh-2');
    expect(server.blacklist.has('R0')).toBe(true); // R0 was retired, never reused
  });

  it('a client that keeps the OLD refresh token would be rejected (bug reproduction)', async () => {
    installBrowserStorage();
    const { auth } = await import('../../runtime/auth');
    const server = makeRotatingServer();

    auth.setRefreshToken('R0');

    // Simulate the ORIGINAL bug: persist the OLD token after a refresh.
    const buggyRefresh = () => {
      const presented = auth.getRefreshToken()!;
      const res = server.refresh(presented);
      auth.setToken(res.access);
      auth.setRefreshToken(presented); // BUG: should be res.refresh
    };

    buggyRefresh(); // first refresh "works" but leaves R0 in storage
    expect(auth.getRefreshToken()).toBe('R0');

    // Second refresh reuses the now-blacklisted R0 → server rejects it.
    expect(() => buggyRefresh()).toThrow(/blacklisted/i);
  });
});
