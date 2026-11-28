/**
 * Profile cache tests (auth/hooks/useProfileCache.ts).
 *
 * The profile cache is a localStorage entry that lets the app render "logged in"
 * UI without an API round-trip. It is DIRECTLY implicated in the stuck-auth bug:
 * a cached profile left behind by a now-dead session made AuthContext skip the
 * API and treat the user as authenticated. So the cache must expire on TTL,
 * invalidate on version bump, and fail CLOSED on corruption (return null + clear)
 * rather than surfacing garbage.
 *
 * The module reads `window.localStorage` / `Date.now()` at call time; we install
 * a fake storage on globalThis before import and drive time via vi.setSystemTime.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

function installBrowserStorage() {
  const map = new Map<string, string>();
  const storage = {
    getItem: (k: string) => (map.has(k) ? map.get(k)! : null),
    setItem: (k: string, v: string) => void map.set(k, v),
    removeItem: (k: string) => void map.delete(k),
    clear: () => map.clear(),
    key: (i: number) => Array.from(map.keys())[i] ?? null,
    get length() { return map.size; },
  };
  // useBase64 checks `isDev` via env and uses window for btoa/atob; provide both.
  vi.stubGlobal('window', { localStorage: storage });
  vi.stubGlobal('localStorage', storage);
  return map;
}

const CACHE_KEY = 'cfg.profile.cache';
const NOW = 1_800_000_000_000;

// Minimal User-shaped object; the cache is generic over its shape.
const sampleUser = { id: 7, email: 'a@b.com', is_staff: false } as never;

describe('profile cache', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.resetModules();
    vi.useFakeTimers();
    vi.setSystemTime(NOW);
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('round-trips a profile set→get within TTL', async () => {
    installBrowserStorage();
    const { setCachedProfile, getCachedProfile } = await import('../hooks/useProfileCache');
    setCachedProfile(sampleUser);
    expect(getCachedProfile()).toEqual(sampleUser);
  });

  it('returns null when nothing is cached', async () => {
    installBrowserStorage();
    const { getCachedProfile } = await import('../hooks/useProfileCache');
    expect(getCachedProfile()).toBeNull();
  });

  it('expires after TTL and clears the entry', async () => {
    const map = installBrowserStorage();
    const { setCachedProfile, getCachedProfile } = await import('../hooks/useProfileCache');
    setCachedProfile(sampleUser, { ttl: 1000 });
    expect(getCachedProfile()).toEqual(sampleUser);

    vi.setSystemTime(NOW + 1001); // just past TTL
    expect(getCachedProfile()).toBeNull();
    expect(map.has(CACHE_KEY)).toBe(false); // expired cache is purged
  });

  it('keeps the profile right up to the TTL boundary', async () => {
    installBrowserStorage();
    const { setCachedProfile, getCachedProfile } = await import('../hooks/useProfileCache');
    setCachedProfile(sampleUser, { ttl: 1000 });
    vi.setSystemTime(NOW + 1000); // exactly TTL — age === ttl, not yet "> ttl"
    expect(getCachedProfile()).toEqual(sampleUser);
  });

  it('invalidates on a cache-version mismatch (migration safety)', async () => {
    const map = installBrowserStorage();
    const { getCachedProfile } = await import('../hooks/useProfileCache');
    const { encodeBase64 } = await import('../hooks/useBase64');
    // Hand-write an entry from a FUTURE/old version.
    const stale = { version: 999, data: sampleUser, timestamp: NOW, ttl: 10_000 };
    map.set(CACHE_KEY, encodeBase64(JSON.stringify(stale)));
    expect(getCachedProfile()).toBeNull();
    expect(map.has(CACHE_KEY)).toBe(false);
  });

  it('fails closed on corrupt cache data (returns null + clears)', async () => {
    const map = installBrowserStorage();
    const { getCachedProfile } = await import('../hooks/useProfileCache');
    map.set(CACHE_KEY, 'this-is-not-valid-encoded-json');
    expect(getCachedProfile()).toBeNull();
    expect(map.has(CACHE_KEY)).toBe(false);
  });

  it('clearProfileCache removes the entry', async () => {
    const map = installBrowserStorage();
    const { setCachedProfile, clearProfileCache } = await import('../hooks/useProfileCache');
    setCachedProfile(sampleUser);
    expect(map.has(CACHE_KEY)).toBe(true);
    clearProfileCache();
    expect(map.has(CACHE_KEY)).toBe(false);
  });

  it('hasValidCache reflects presence + freshness', async () => {
    installBrowserStorage();
    const { setCachedProfile, hasValidCache } = await import('../hooks/useProfileCache');
    expect(hasValidCache()).toBe(false);
    setCachedProfile(sampleUser, { ttl: 500 });
    expect(hasValidCache()).toBe(true);
    vi.setSystemTime(NOW + 501);
    expect(hasValidCache()).toBe(false);
  });

  it('getCacheMetadata reports age / ttl / expiresIn', async () => {
    installBrowserStorage();
    const { setCachedProfile, getCacheMetadata } = await import('../hooks/useProfileCache');
    expect(getCacheMetadata()).toEqual({ exists: false });

    setCachedProfile(sampleUser, { ttl: 10_000 });
    vi.setSystemTime(NOW + 3_000);
    const meta = getCacheMetadata();
    expect(meta).toMatchObject({ exists: true, age: 3_000, ttl: 10_000, expiresIn: 7_000 });
  });

  it('getCacheMetadata clamps expiresIn to 0 once expired', async () => {
    installBrowserStorage();
    const { setCachedProfile, getCacheMetadata } = await import('../hooks/useProfileCache');
    setCachedProfile(sampleUser, { ttl: 1_000 });
    vi.setSystemTime(NOW + 5_000);
    expect(getCacheMetadata()?.expiresIn).toBe(0);
  });
});
