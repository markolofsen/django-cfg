/**
 * Hydration contract: the auth context renders on the client's FIRST render exactly what the server
 * rendered (a guest), even when localStorage holds a cached profile of a live session. The cached
 * profile appears only after the hydration commit, and `isHydrated` says when.
 *
 * Regression guard for React #418: the profile used to be read from the cache in a `useState`
 * initializer, so `user` / `isAdminUser` were set during hydration while the server HTML had a guest.
 *
 * The server HTML is written by hand (what SSR produces: no localStorage, so a guest) and then
 * hydrated with the real AccountsProvider + AuthProvider.
 */

// @vitest-environment jsdom
import { act, render } from '@testing-library/react';
import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn(), back: vi.fn() }),
  usePathname: () => '/film/1',
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock('../hooks/useCfgRouter', () => ({
  useCfgRouter: () => ({ push: vi.fn(), replace: vi.fn(), hardPush: vi.fn(), hardReplace: vi.fn() }),
}));

vi.mock('../utils/logger', () => ({
  authLogger: { debug: vi.fn(), info: vi.fn(), warn: vi.fn(), error: vi.fn() },
}));

// A live session in storage. The server snapshot is anonymous, like the real store's.
const session = { access: 'live-access' as string | null };
vi.mock('../../runtime/auth', () => {
  const authed = { status: 'authenticated' };
  const anon = { status: 'anonymous' };
  return {
    auth: {
      getToken: () => session.access,
      getRefreshToken: () => session.access,
      isAuthenticated: () => Boolean(session.access),
      getSnapshot: () => (session.access ? authed : anon),
      getServerSnapshot: () => anon,
      subscribe: () => () => {},
      setSession: () => {},
      clearSession: () => {
        session.access = null;
      },
      setCookieDomain: () => {},
      setTimezone: () => {},
      onSessionExpired: () => () => {},
    },
  };
});

const STAFF = { id: 1, email: 'staff@example.com', is_staff: true, is_superuser: false };
const GUEST_HTML = '<span data-testid="who">guest|false|false</span>';

async function hydrateWithCache() {
  const { setCachedProfile } = await import('../hooks/useProfileCache');
  const { AuthProvider, useAuth } = await import('../context/AuthContext');
  setCachedProfile(STAFF as never);

  // What each render of the consumer showed, in order: the first entry is the hydration render.
  const renders: string[] = [];
  function Who() {
    const { user, isAdminUser, isHydrated } = useAuth();
    const text = `${user?.email ?? 'guest'}|${isAdminUser}|${isHydrated}`;
    renders.push(text);
    return <span data-testid="who">{text}</span>;
  }

  const container = document.createElement('div');
  container.innerHTML = GUEST_HTML;
  document.body.appendChild(container);

  const recoverable: unknown[] = [];
  let view!: ReturnType<typeof render>;
  await act(async () => {
    view = render(
      <AuthProvider>
        <Who />
      </AuthProvider>,
      { container, hydrate: true, onRecoverableError: (error: unknown) => recoverable.push(error) },
    );
  });
  return { view, renders, recoverable };
}

describe('auth context hydration', () => {
  let consoleError: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    vi.resetModules();
    localStorage.clear();
    session.access = 'live-access';
    consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleError.mockRestore();
    document.body.innerHTML = '';
  });

  it('renders a guest during hydration even with a cached signed-in profile', async () => {
    const { renders, recoverable } = await hydrateWithCache();

    expect(renders[0]).toBe('guest|false|false');
    expect(recoverable).toEqual([]);
    const mismatch = consoleError.mock.calls.some((args: unknown[]) =>
      /hydrat|did not match/i.test(String(args[0])),
    );
    expect(mismatch).toBe(false);
  });

  it('applies the cached profile right after mount and flips isHydrated', async () => {
    const { view, renders } = await hydrateWithCache();

    expect(view.getByTestId('who').textContent).toBe('staff@example.com|true|true');
    expect(renders.at(-1)).toBe('staff@example.com|true|true');
  });

  it('drops the cache and stays a guest when there is no live session', async () => {
    session.access = null;
    const { view } = await hydrateWithCache();
    const { getCachedProfile } = await import('../hooks/useProfileCache');

    expect(view.getByTestId('who').textContent).toBe('guest|false|true');
    expect(getCachedProfile()).toBeNull();
  });
});
