/**
 * Password login contract test.
 *
 * The password grant returns the SAME envelope as OTP verify, and the point of
 * that is a single session owner: tokens are written by exactly one path, and
 * the 2FA branch carries a session id and NO tokens. These three cases are the
 * regression guard for a second token store creeping in — a bespoke fetch that
 * "also" saves an access token would pass a shape test and fail these.
 *
 * `AccountsContext` is mocked at the module boundary so the test drives the
 * real `AuthContext.login` (branching, redirect suppression, error mapping)
 * against a scripted server envelope.
 */

// @vitest-environment jsdom
import { act, renderHook } from '@testing-library/react';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { APIError } from '../../runtime/errors';

const hardPush = vi.fn();
const hardReplace = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn(), back: vi.fn() }),
  usePathname: () => '/auth',
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock('../hooks/useCfgRouter', () => ({
  useCfgRouter: () => ({ push: vi.fn(), replace: vi.fn(), hardPush, hardReplace }),
}));

// The token store stands in for the ONE write path. Asserting on this fake is
// how "a 401 stored nothing" and "the 2FA branch stored nothing" are proven.
const tokens: { access: string | null; refresh: string | null } = { access: null, refresh: null };
vi.mock('../../runtime/auth', () => ({
  auth: {
    getToken: () => tokens.access,
    getRefreshToken: () => tokens.refresh,
    isAuthenticated: () => Boolean(tokens.access),
    setSession: ({ access, refresh }: { access: string; refresh?: string | null }) => {
      tokens.access = access;
      tokens.refresh = refresh ?? null;
    },
    clearSession: () => {
      tokens.access = null;
      tokens.refresh = null;
    },
    setTimezone: () => {},
    onSessionExpired: () => () => {},
    subscribe: () => () => {},
  },
}));

vi.mock('../utils/logger', () => ({
  authLogger: { debug: vi.fn(), info: vi.fn(), warn: vi.fn(), error: vi.fn() },
}));

vi.mock('../hooks/useSession', () => ({
  useSession: () => ({ status: tokens.access ? 'authenticated' : 'anonymous' }),
}));

// Mirrors AccountsContext.loginWithPassword: settles the envelope through the
// same store the OTP path uses, then hands the raw response back.
const loginWithPassword = vi.fn();
const accountsValue = {
  profile: undefined,
  isHydrated: true,
  isLoadingProfile: false,
  profileError: null,
  updateProfile: vi.fn(),
  partialUpdateProfile: vi.fn(),
  uploadAvatar: vi.fn(),
  refreshProfile: vi.fn().mockResolvedValue(undefined),
  requestOTP: vi.fn(),
  verifyOTP: vi.fn(),
  loginWithPassword,
  logout: vi.fn(),
};

vi.mock('../context/AccountsContext', () => ({
  AccountsProvider: ({ children }: { children: React.ReactNode }) => children,
  useAccountsContext: () => accountsValue,
}));

const USER = { id: 7, email: 'jane@example.com' };

/** Script `loginWithPassword` with a server envelope, settled like the real one. */
function respondWith(envelope: Record<string, unknown>) {
  loginWithPassword.mockImplementation(async () => {
    const { auth } = await import('../../runtime/auth');
    if (envelope.requires_2fa && envelope.session_id) return envelope;
    if (envelope.access && envelope.refresh) {
      auth.setSession({
        access: envelope.access as string,
        refresh: envelope.refresh as string,
      });
    }
    return envelope;
  });
}

async function renderAuth() {
  const { AuthProvider, useAuth } = await import('../context/AuthContext');
  return renderHook(() => useAuth(), {
    wrapper: ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    ),
  });
}

describe('AuthContext.login (password grant)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    tokens.access = null;
    tokens.refresh = null;
  });

  it('stores the token pair and returns the user on success', async () => {
    respondWith({ requires_2fa: false, access: 'access-1', refresh: 'refresh-1', user: USER });
    const { result } = await renderAuth();

    let outcome!: Awaited<ReturnType<typeof result.current.login>>;
    await act(async () => {
      outcome = await result.current.login('jane@example.com', 'correct horse', {
        skipRedirect: true,
      });
    });

    expect(outcome.success).toBe(true);
    expect(outcome.user).toEqual(USER);
    expect(outcome.requires_2fa).toBeUndefined();
    expect(tokens).toEqual({ access: 'access-1', refresh: 'refresh-1' });
  });

  it('sends email and password to the password endpoint', async () => {
    respondWith({ requires_2fa: false, access: 'access-1', refresh: 'refresh-1', user: USER });
    const { result } = await renderAuth();

    await act(async () => {
      await result.current.login('jane@example.com', 'correct horse', {
        skipRedirect: true,
      });
    });

    expect(loginWithPassword).toHaveBeenCalledWith({
      email: 'jane@example.com',
      password: 'correct horse',
    });
  });

  it('surfaces a 401 as a typed failure and stores nothing', async () => {
    loginWithPassword.mockRejectedValue(
      new APIError(
        401,
        { error: 'Authentication failed', error_code: 'invalid_credentials' },
        '/cfg/accounts/token/',
      ),
    );
    const { result } = await renderAuth();

    let outcome!: Awaited<ReturnType<typeof result.current.login>>;
    await act(async () => {
      outcome = await result.current.login('jane@example.com', 'wrong', { skipRedirect: true });
    });

    expect(outcome.success).toBe(false);
    expect(outcome.statusCode).toBe(401);
    expect(outcome.errorCode).toBe('invalid_credentials');
    expect(outcome.message).toBe('Authentication failed');
    expect(tokens).toEqual({ access: null, refresh: null });
    expect(hardPush).not.toHaveBeenCalled();
  });

  it('carries retry_after from a 429 lockout', async () => {
    loginWithPassword.mockRejectedValue(
      new APIError(
        429,
        {
          error: 'Too many failed attempts. Please try again later.',
          error_code: 'locked_out',
          retry_after: 900,
        },
        '/cfg/accounts/token/',
      ),
    );
    const { result } = await renderAuth();

    let outcome!: Awaited<ReturnType<typeof result.current.login>>;
    await act(async () => {
      outcome = await result.current.login('jane@example.com', 'wrong', { skipRedirect: true });
    });

    expect(outcome.success).toBe(false);
    expect(outcome.statusCode).toBe(429);
    expect(outcome.errorCode).toBe('locked_out');
    expect(outcome.retryAfter).toBe(900);
    expect(tokens).toEqual({ access: null, refresh: null });
  });

  it('returns the session id and stores NO tokens when 2FA is required', async () => {
    respondWith({ requires_2fa: true, session_id: 'sess-abc', should_prompt_2fa: false });
    const { result } = await renderAuth();

    let outcome!: Awaited<ReturnType<typeof result.current.login>>;
    await act(async () => {
      outcome = await result.current.login('jane@example.com', 'correct horse', {
        skipRedirect: true,
      });
    });

    expect(outcome.success).toBe(true);
    expect(outcome.requires_2fa).toBe(true);
    expect(outcome.session_id).toBe('sess-abc');
    expect(outcome.user).toBeUndefined();
    expect(tokens).toEqual({ access: null, refresh: null });
    expect(hardPush).not.toHaveBeenCalled();
  });

  it('redirects on success when the caller does not opt out', async () => {
    respondWith({ requires_2fa: false, access: 'access-1', refresh: 'refresh-1', user: USER });
    const { result } = await renderAuth();

    await act(async () => {
      await result.current.login('jane@example.com', 'correct horse', {
        redirectUrl: '/dashboard',
      });
    });

    expect(hardPush).toHaveBeenCalledWith('/dashboard');
  });
});
