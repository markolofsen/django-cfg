// @vitest-environment jsdom
/**
 * `useSession` mounted under React against the REAL auth store (audit E1, React #185).
 *
 * `useSyncExternalStore` compares snapshots with `Object.is`. A `getSnapshot` that builds a new object per call
 * looks like a change after every read and re-renders until React gives up ("Maximum update depth exceeded").
 * `hydration.test.tsx` mocks the store with stable objects, so it cannot catch that; this test does not mock it.
 */
import { act, cleanup, render } from '@testing-library/react';
import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from '../../runtime/__tests__/reset-runtime';

beforeEach(() => {
  vi.unstubAllGlobals();
  resetRuntimeSlots();
  for (const cookie of document.cookie.split(';')) {
    const name = cookie.split('=')[0]?.trim();
    if (name) document.cookie = `${name}=; Max-Age=0; Path=/`;
  }
  vi.resetModules();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe('the session snapshot', () => {
  it('is the same object across reads until a token changes', async () => {
    const { auth } = await import('../../runtime/auth');

    const anonymous = auth.getSnapshot();
    expect(auth.getSnapshot()).toBe(anonymous);

    auth.setToken('access-1');
    const signedIn = auth.getSnapshot();
    expect(signedIn).not.toBe(anonymous);
    expect(signedIn).toEqual({ status: 'authenticated', isAuthenticated: true, accessToken: 'access-1' });
    expect(auth.getSnapshot()).toBe(signedIn);

    // A write that changes nothing the snapshot shows keeps the object.
    auth.setToken('access-1');
    auth.setLocale('de');
    expect(auth.getSnapshot()).toBe(signedIn);

    expect(auth.getServerSnapshot()).toBe(auth.getServerSnapshot());
    expect(auth.getServerSnapshot()).toEqual({ status: 'anonymous', isAuthenticated: false, accessToken: null });
  });
});

describe('useSession under React', () => {
  it('mounts without an update loop and re-renders once per session change', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    const { auth } = await import('../../runtime/auth');
    const { useSession } = await import('../hooks/useSession');
    let renders = 0;
    const seen: unknown[] = [];

    function Probe() {
      const session = useSession();
      renders += 1;
      seen.push(session);
      return <span data-testid="status">{session.status}</span>;
    }

    const view = render(<Probe />);
    expect(view.getByTestId('status').textContent).toBe('anonymous');
    const mounted = renders;
    expect(mounted).toBe(1);

    act(() => auth.setSession({ access: 'access-1', refresh: 'refresh-1' }));
    expect(view.getByTestId('status').textContent).toBe('authenticated');
    expect(renders).toBe(mounted + 1);

    act(() => auth.clearSession());
    expect(view.getByTestId('status').textContent).toBe('anonymous');
    expect(renders).toBe(mounted + 2);

    // React reports an uncached getSnapshot and the update-depth error through console.error.
    expect(consoleError).not.toHaveBeenCalled();
    expect(seen[0]).not.toBe(seen[1]);
  });

  it('keeps every mounted consumer on one snapshot object', async () => {
    const { auth } = await import('../../runtime/auth');
    const { useSession } = await import('../hooks/useSession');
    const seen: unknown[] = [];

    function Probe() {
      seen.push(useSession());
      return null;
    }

    render(<><Probe /><Probe /><Probe /></>);
    act(() => auth.setToken('access-1'));

    const afterChange = seen.slice(-3);
    expect(new Set(afterChange).size).toBe(1);
    expect(afterChange[0]).toBe(auth.getSnapshot());
  });
});
