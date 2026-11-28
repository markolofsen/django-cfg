/**
 * Single sign-in, the browser half: a follower host's sign-in route becomes a hop to the host with
 * `next`; the host's own router and a non-SSO app are untouched; sign-out goes without `next`.
 * (The saving of `?next=` on the host and the redirect effect live in AuthContext; their rules are the
 * `safeNext` / `resolveSso` cases in sso.test.ts.)
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const nextPush = vi.fn();
const nextReplace = vi.fn();

vi.mock('react', () => ({ useCallback: (f: unknown) => f, useMemo: (f: () => unknown) => f() }));
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: nextPush, replace: nextReplace, prefetch: vi.fn(), back: vi.fn(), forward: vi.fn(), refresh: vi.fn() }),
}));

function stubWindow(href: string) {
  const url = new URL(href);
  const loc = {
    href: url.href,
    origin: url.origin,
    hostname: url.hostname,
    protocol: url.protocol,
    pathname: url.pathname,
    assign: vi.fn(),
    replace: vi.fn(),
  };
  vi.stubGlobal('window', { location: loc, addEventListener: vi.fn() });
  return loc;
}

async function load(host: string | null, page: string) {
  vi.resetModules();
  const loc = stubWindow(page);
  const sso = await import('../utils/sso');
  sso.configureSso(host ? { host } : null);
  // Called outside a component on purpose: the hook only reads the stubbed window and next router.
  const { useCfgRouter: makeRouter } = await import('../hooks/useCfgRouter');
  return { router: makeRouter(), loc };
}

beforeEach(() => {
  nextPush.mockClear();
  nextReplace.mockClear();
});
afterEach(() => vi.unstubAllGlobals());

describe('follower host', () => {
  it('push("/auth") hops to the host with the current URL as next', async () => {
    const { router, loc } = await load('reforms.ai', 'https://my.reforms.ai/private/orders?id=3');
    router.push('/auth');
    expect(loc.assign).toHaveBeenCalledWith(
      `https://reforms.ai/auth?next=${encodeURIComponent('https://my.reforms.ai/private/orders?id=3')}`,
    );
    expect(nextPush).not.toHaveBeenCalled();
  });

  it('hardReplace("/ru/auth/") hops too (locale and slash)', async () => {
    const { router, loc } = await load('reforms.ai', 'https://hub.reforms.ai/private');
    router.hardReplace('/ru/auth/');
    expect(loc.replace).toHaveBeenCalledWith(`https://reforms.ai/auth?next=${encodeURIComponent('https://hub.reforms.ai/private')}`);
  });

  it('sign-out ({ next: false }) goes to the host without a way back', async () => {
    const { router, loc } = await load('reforms.ai', 'https://my.reforms.ai/private');
    router.hardReplace('/auth', { next: false });
    expect(loc.replace).toHaveBeenCalledWith('https://reforms.ai/auth');
  });

  it('a hostile next in the href is dropped, not forwarded', async () => {
    const { router, loc } = await load('reforms.ai', 'https://my.reforms.ai/private');
    router.push('/auth?next=https://evil.com/');
    // falls back to the page the visitor is on
    expect(loc.assign).toHaveBeenCalledWith(`https://reforms.ai/auth?next=${encodeURIComponent('https://my.reforms.ai/private')}`);
  });

  it('other routes are not touched', async () => {
    const { router, loc } = await load('reforms.ai', 'https://my.reforms.ai/private');
    router.push('/private/settings');
    expect(nextPush).toHaveBeenCalledWith('/private/settings', undefined);
    expect(loc.assign).not.toHaveBeenCalled();
  });
});

describe('everywhere else the old behaviour', () => {
  it('the host itself renders its own /auth', async () => {
    const { router } = await load('reforms.ai', 'https://reforms.ai/private');
    router.push('/auth');
    expect(nextPush).toHaveBeenCalledWith('/auth', undefined);
  });

  it('localhost: SSO is off, /auth stays local', async () => {
    const { router, loc } = await load('reforms.ai', 'http://localhost:3000/private');
    router.push('/auth');
    expect(nextPush).toHaveBeenCalledWith('/auth', undefined);
    expect(loc.assign).not.toHaveBeenCalled();
  });

  it('no sso configured: nothing changes', async () => {
    const { router } = await load(null, 'https://my.reforms.ai/private');
    router.push('/auth');
    expect(nextPush).toHaveBeenCalledWith('/auth', undefined);
  });
});
