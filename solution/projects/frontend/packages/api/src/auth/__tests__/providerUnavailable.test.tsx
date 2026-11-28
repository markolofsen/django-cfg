// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from '../../runtime/__tests__/reset-runtime';

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn(), back: vi.fn() }),
  usePathname: () => '/private',
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock('../hooks/useCfgRouter', () => ({
  useCfgRouter: () => ({ push: vi.fn(), replace: vi.fn(), hardPush: vi.fn(), hardReplace: vi.fn() }),
}));

vi.mock('../utils/logger', () => ({
  authLogger: { debug: vi.fn(), info: vi.fn(), warn: vi.fn(), error: vi.fn() },
}));

describe('AuthProvider unavailable API bootstrap', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    resetRuntimeSlots();
    vi.resetModules();
    localStorage.clear();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    cleanup();
  });

  it.each([
    ['401', 401],
    ['404', 404],
    ['5xx', 503],
    ['network', 'network'],
  ] as const)('keeps the React tree mounted when profile bootstrap returns %s', async (_label, failure) => {
    if (failure === 'network') {
      vi.stubGlobal('fetch', vi.fn(async () => { throw new Error('offline'); }));
    } else {
      vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ detail: 'unavailable' }), {
        status: failure,
        headers: { 'content-type': 'application/json' },
      })));
    }

    const { configureApi } = await import('../../runtime/api-origin');
    const { auth } = await import('../../runtime/auth');
    const { AuthProvider, useAuth } = await import('../context/AuthContext');
    configureApi({ apiUrl: 'https://api.example.test' });
    auth.setSession({ access: 'access-only' });

    function Probe() {
      const { isLoading } = useAuth();
      return (
        <>
          <span data-testid="alive">alive</span>
          <span data-testid="state">{isLoading ? 'loading' : 'settled'}</span>
        </>
      );
    }

    render(
      <AuthProvider config={{ apiUrl: 'https://api.example.test' }}>
        <Probe />
      </AuthProvider>,
    );

    await waitFor(() => expect(screen.getByTestId('state').textContent).toBe('settled'));
    expect(screen.getByTestId('alive').textContent).toBe('alive');
    auth.clearSession();
  });
});

