/**
 * Redirect-URL manager tests (auth/hooks/useAuthRedirect.ts).
 *
 * After login the app must send the user back to where they were headed. The
 * manager persists that URL in sessionStorage (surviving the auth round-trip,
 * readable across component instances) and clears it on use. The public methods
 * getFinalRedirectUrl / useAndClearRedirect / hasRedirect read straight from
 * sessionStorage, bypassing React state — that is exactly the cross-instance
 * behaviour under test.
 *
 * useAuthRedirectManager calls useCfgStored → React.useState. We mock
 * useState with a plain closure so the hook body can run outside a React render
 * (we are testing the storage logic, not React state wiring).
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

// Mock React's useState so the hook runs without a renderer. The lazy
// initializer is invoked immediately (mirroring React) and its value returned.
vi.mock('react', () => ({
  useState: (init: unknown) => {
    const value = typeof init === 'function' ? (init as () => unknown)() : init;
    return [value, () => {}];
  },
  useCallback: (fn: unknown) => fn,
}));

function installSessionStorage() {
  const map = new Map<string, string>();
  const storage = {
    getItem: (k: string) => (map.has(k) ? map.get(k)! : null),
    setItem: (k: string, v: string) => void map.set(k, v),
    removeItem: (k: string) => void map.delete(k),
    clear: () => map.clear(),
  };
  vi.stubGlobal('window', { sessionStorage: storage, localStorage: storage });
  vi.stubGlobal('sessionStorage', storage);
  return map;
}

const KEY = 'cfg.auth.redirect_url';

describe('useAuthRedirectManager (storage-backed paths)', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.resetModules();
  });

  it('falls back to the provided fallbackUrl when nothing is saved', async () => {
    installSessionStorage();
    const { useAuthRedirectManager } = await import('../hooks/useAuthRedirect');
    const mgr = useAuthRedirectManager({ fallbackUrl: '/home', clearOnUse: true });
    expect(mgr.getFinalRedirectUrl()).toBe('/home');
    expect(mgr.hasRedirect()).toBe(false);
  });

  it('reads a saved redirect straight from sessionStorage', async () => {
    const map = installSessionStorage();
    map.set(KEY, JSON.stringify('/projects/42'));
    const { useAuthRedirectManager } = await import('../hooks/useAuthRedirect');
    const mgr = useAuthRedirectManager({ fallbackUrl: '/home' });

    expect(mgr.hasRedirect()).toBe(true);
    expect(mgr.getFinalRedirectUrl()).toBe('/projects/42');
  });

  it('useAndClearRedirect returns the saved URL then clears it (clearOnUse)', async () => {
    const map = installSessionStorage();
    map.set(KEY, JSON.stringify('/settings'));
    const { useAuthRedirectManager } = await import('../hooks/useAuthRedirect');
    const mgr = useAuthRedirectManager({ fallbackUrl: '/home', clearOnUse: true });

    expect(mgr.useAndClearRedirect()).toBe('/settings');
    expect(map.has(KEY)).toBe(false); // cleared from storage

    // A FRESH manager (mirrors a new component instance after the redirect) now
    // sees empty storage and falls back. (This manager's mocked React state
    // still holds the old value — real React would re-init from storage.)
    const fresh = useAuthRedirectManager({ fallbackUrl: '/home' });
    expect(fresh.getFinalRedirectUrl()).toBe('/home');
    expect(fresh.hasRedirect()).toBe(false);
  });

  it('useAndClearRedirect keeps the URL when clearOnUse is false', async () => {
    const map = installSessionStorage();
    map.set(KEY, JSON.stringify('/keep-me'));
    const { useAuthRedirectManager } = await import('../hooks/useAuthRedirect');
    const mgr = useAuthRedirectManager({ fallbackUrl: '/home', clearOnUse: false });

    expect(mgr.useAndClearRedirect()).toBe('/keep-me');
    expect(map.has(KEY)).toBe(true); // preserved
  });

  it('gracefully falls back on corrupt storage JSON', async () => {
    const map = installSessionStorage();
    map.set(KEY, 'not-json'); // getRedirectFromStorage catches + returns ''
    const { useAuthRedirectManager } = await import('../hooks/useAuthRedirect');
    const mgr = useAuthRedirectManager({ fallbackUrl: '/home' });

    expect(mgr.getFinalRedirectUrl()).toBe('/home');
  });
});
