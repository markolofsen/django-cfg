/**
 * OAuth sign-in contract: one hook, every provider.
 *
 * What these guard: the state check is mandatory (a callback with no stored
 * state is a login-CSRF attempt, not a legacy flow), the state is single use,
 * `redirect_uri` is never sent, the session is written through the one store,
 * and the deprecated GitHub wrapper keeps its shape.
 */

// @vitest-environment jsdom
import { act, renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { APIError } from '../../runtime/errors';

const hardPush = vi.fn();
vi.mock('../hooks/useCfgRouter', () => ({
  useCfgRouter: () => ({ push: vi.fn(), replace: vi.fn(), hardPush, hardReplace: vi.fn() }),
}));

const tokens: { access: string | null; refresh: string | null } = { access: null, refresh: null };
const { clearSession } = vi.hoisted(() => ({ clearSession: vi.fn() }));
vi.mock('../../runtime/auth', () => ({
  auth: {
    setSession: ({ access, refresh }: { access: string; refresh?: string | null }) => {
      tokens.access = access;
      tokens.refresh = refresh ?? null;
    },
    clearSession,
    setTimezone: () => {},
  },
}));

vi.mock('../utils/logger', () => ({
  authLogger: { debug: vi.fn(), info: vi.fn(), warn: vi.fn(), error: vi.fn() },
}));

const sdk = {
  cfgAccountsOauthGithubAuthorizeCreate: vi.fn(),
  cfgAccountsOauthGithubCallbackCreate: vi.fn(),
  cfgAccountsOauthGoogleAuthorizeCreate: vi.fn(),
  cfgAccountsOauthGoogleCallbackCreate: vi.fn(),
  cfgAccountsOauthProvidersRetrieve: vi.fn(),
};
vi.mock('../../_api/endpoints', () => sdk);

const STATE_KEY = 'cfg.auth.oauth_state';
const PROVIDER_KEY = 'cfg.auth.oauth_provider';
const REDIRECT_KEY = 'cfg.auth.redirect_url';
const USER = { id: 7, email: 'jane@example.com' };
const SESSION = { requires_2fa: false, access: 'a1', refresh: 'r1', user: USER, is_new_user: true };

async function loadHook(options = {}) {
  const { useOAuthLogin } = await import('../hooks/useOAuthLogin');
  return renderHook(() => useOAuthLogin(options));
}

describe('useOAuthLogin', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    tokens.access = null;
    tokens.refresh = null;
    sessionStorage.clear();
    clearSession.mockImplementation(() => {
      tokens.access = null;
      tokens.refresh = null;
    });
  });

  describe('start', () => {
    it('clears the old session, stores state and provider, and sends no redirect_uri', async () => {
      sdk.cfgAccountsOauthGoogleAuthorizeCreate.mockResolvedValue({ authorization_url: 'about:blank#go', state: 'st-1' });
      const { result } = await loadHook({ sourceUrl: 'https://app.example.com' });

      await act(async () => {
        await result.current.start('google');
      });

      expect(clearSession).toHaveBeenCalled();
      expect(sdk.cfgAccountsOauthGoogleAuthorizeCreate).toHaveBeenCalledWith({ source_url: 'https://app.example.com' });
      expect(sdk.cfgAccountsOauthGithubAuthorizeCreate).not.toHaveBeenCalled();
      expect(sessionStorage.getItem(STATE_KEY)).toBe('st-1');
      expect(sessionStorage.getItem(PROVIDER_KEY)).toBe('google');
      expect(result.current.loadingProvider).toBe('google');
    });

    it('reports a server code and stops loading when authorize fails', async () => {
      sdk.cfgAccountsOauthGithubAuthorizeCreate.mockRejectedValue(
        new APIError(
          503,
          { error: 'oauth_disabled', error_description: 'Not configured' },
          '/x',
        ),
      );
      const onError = vi.fn();
      const { result } = await loadHook({ onError });

      await act(async () => {
        await result.current.start('github');
      });

      expect(result.current.loadingProvider).toBeNull();
      expect(result.current.errorCode).toBe('oauth_disabled');
      expect(result.current.error).toBe('Not configured');
      expect(onError).toHaveBeenCalledWith('Not configured', 'oauth_disabled');
      expect(sessionStorage.getItem(STATE_KEY)).toBeNull();
    });
  });

  describe('complete', () => {
    beforeEach(() => {
      sessionStorage.setItem(STATE_KEY, 'st-1');
      sessionStorage.setItem(PROVIDER_KEY, 'google');
    });

    it('exchanges the code, writes the session, and hands over the user', async () => {
      sdk.cfgAccountsOauthGoogleCallbackCreate.mockResolvedValue(SESSION);
      const onSuccess = vi.fn();
      const { result } = await loadHook({ onSuccess, skipRedirect: true });

      await act(async () => {
        await result.current.complete('google', 'code-1', 'st-1');
      });

      expect(sdk.cfgAccountsOauthGoogleCallbackCreate).toHaveBeenCalledWith({ code: 'code-1', state: 'st-1' });
      expect(tokens).toEqual({ access: 'a1', refresh: 'r1' });
      expect(onSuccess).toHaveBeenCalledWith(USER, true, 'google');
      expect(hardPush).not.toHaveBeenCalled();
      expect(result.current.isLoading).toBe(false);
    });

    it('rejects a state that differs from the stored one without calling the server', async () => {
      const onError = vi.fn();
      const { result } = await loadHook({ onError });

      await act(async () => {
        await result.current.complete('google', 'code-1', 'attacker-state');
      });

      expect(sdk.cfgAccountsOauthGoogleCallbackCreate).not.toHaveBeenCalled();
      expect(result.current.errorCode).toBe('invalid_state');
      expect(onError).toHaveBeenCalledWith(expect.any(String), 'invalid_state');
      expect(tokens.access).toBeNull();
    });

    it('rejects a callback when no state was stored (login CSRF)', async () => {
      sessionStorage.clear();
      const { result } = await loadHook();

      await act(async () => {
        await result.current.complete('google', 'code-1', 'st-1');
      });

      expect(sdk.cfgAccountsOauthGoogleCallbackCreate).not.toHaveBeenCalled();
      expect(result.current.errorCode).toBe('invalid_state');
    });

    it('rejects a state that was stored for another provider', async () => {
      const { result } = await loadHook();

      await act(async () => {
        await result.current.complete('github', 'code-1', 'st-1');
      });

      expect(sdk.cfgAccountsOauthGithubCallbackCreate).not.toHaveBeenCalled();
      expect(result.current.errorCode).toBe('invalid_state');
    });

    it('spends the stored state: a second completion with it fails', async () => {
      sdk.cfgAccountsOauthGoogleCallbackCreate.mockResolvedValue(SESSION);
      const { result } = await loadHook({ skipRedirect: true });

      await act(async () => {
        await result.current.complete('google', 'code-1', 'st-1');
      });
      await act(async () => {
        await result.current.complete('google', 'code-1', 'st-1');
      });

      expect(sdk.cfgAccountsOauthGoogleCallbackCreate).toHaveBeenCalledTimes(1);
      expect(result.current.errorCode).toBe('invalid_state');
      expect(sessionStorage.getItem(STATE_KEY)).toBeNull();
    });

    it('spends the state even when the exchange fails', async () => {
      sdk.cfgAccountsOauthGoogleCallbackCreate.mockRejectedValue(
        new APIError(400, { error: 'email_not_verified', error_description: 'Unverified' }, '/x'),
      );
      const { result } = await loadHook();

      await act(async () => {
        await result.current.complete('google', 'code-1', 'st-1');
      });

      expect(result.current.errorCode).toBe('email_not_verified');
      expect(sessionStorage.getItem(STATE_KEY)).toBeNull();
    });

    it('takes the 2FA branch without writing a session', async () => {
      sdk.cfgAccountsOauthGoogleCallbackCreate.mockResolvedValue({ requires_2fa: true, session_id: 'sess-9', should_prompt_2fa: true });
      const onRequires2FA = vi.fn();
      const onSuccess = vi.fn();
      const { result } = await loadHook({ onRequires2FA, onSuccess });

      await act(async () => {
        await result.current.complete('google', 'code-1', 'st-1');
      });

      expect(onRequires2FA).toHaveBeenCalledWith('sess-9', true);
      expect(onSuccess).not.toHaveBeenCalled();
      expect(tokens.access).toBeNull();
      expect(hardPush).not.toHaveBeenCalled();
    });

    it('navigates to the saved return URL first, with its hash intact', async () => {
      sdk.cfgAccountsOauthGoogleCallbackCreate.mockResolvedValue(SESSION);
      sessionStorage.setItem(REDIRECT_KEY, JSON.stringify('/x#settings/mcp?request=1'));
      const { result } = await loadHook({ redirectUrl: '/home' });

      await act(async () => {
        await result.current.complete('google', 'code-1', 'st-1');
      });

      expect(hardPush).toHaveBeenCalledWith('/x#settings/mcp?request=1');
    });

    it('falls back to the redirectUrl option when nothing was saved', async () => {
      sdk.cfgAccountsOauthGoogleCallbackCreate.mockResolvedValue(SESSION);
      const { result } = await loadHook({ redirectUrl: '/home' });

      await act(async () => {
        await result.current.complete('google', 'code-1', 'st-1');
      });

      expect(hardPush).toHaveBeenCalledWith('/home');
    });

    it('maps an unrecognised failure to a message with no code', async () => {
      sdk.cfgAccountsOauthGoogleCallbackCreate.mockRejectedValue(new Error('boom'));
      const { result } = await loadHook();

      await act(async () => {
        await result.current.complete('google', 'code-1', 'st-1');
      });

      expect(result.current.errorCode).toBeNull();
      expect(result.current.error).toBe('boom');
    });
  });
});

describe('useGithubAuth (deprecated wrapper)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('keeps its return shape and runs the GitHub adapter', async () => {
    const { useGithubAuth } = await import('../hooks/useGithubAuth');
    sdk.cfgAccountsOauthGithubAuthorizeCreate.mockResolvedValue({ authorization_url: 'about:blank#go', state: 'gh-1' });
    sdk.cfgAccountsOauthGithubCallbackCreate.mockResolvedValue(SESSION);
    const { result } = renderHook(() => useGithubAuth({ skipRedirect: true }));

    expect(Object.keys(result.current).sort()).toEqual(
      ['error', 'handleGithubCallback', 'isLoading', 'startGithubAuth'],
    );

    await act(async () => {
      await result.current.startGithubAuth();
    });
    expect(sessionStorage.getItem(PROVIDER_KEY)).toBe('github');

    await act(async () => {
      await result.current.handleGithubCallback('code-1', 'gh-1');
    });
    expect(sdk.cfgAccountsOauthGithubCallbackCreate).toHaveBeenCalledWith({ code: 'code-1', state: 'gh-1' });
    expect(tokens.access).toBe('a1');
  });
});

describe('useOAuthProviders', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('returns the configured providers in server order', async () => {
    sdk.cfgAccountsOauthProvidersRetrieve.mockResolvedValue({
        providers: [
          { id: 'github', name: 'GitHub', icon: 'github' },
          { id: 'google', name: 'Google', icon: 'google' },
        ],
    });
    const { useOAuthProviders } = await import('../hooks/useOAuthProviders');
    const { result } = renderHook(() => useOAuthProviders());

    expect(result.current.isReady).toBe(false);
    await waitFor(() => expect(result.current.isReady).toBe(true));
    expect(result.current.providers.map((p) => p.id)).toEqual(['github', 'google']);
  });

  it('drops a provider this client has no adapter for', async () => {
    sdk.cfgAccountsOauthProvidersRetrieve.mockResolvedValue({ providers: [{ id: 'gitlab', name: 'GitLab', icon: 'gitlab' }, { id: 'google', name: 'Google', icon: 'google' }] });
    const { useOAuthProviders } = await import('../hooks/useOAuthProviders');
    const { result } = renderHook(() => useOAuthProviders());

    await waitFor(() => expect(result.current.isReady).toBe(true));
    expect(result.current.providers.map((p) => p.id)).toEqual(['google']);
  });

  it('returns an empty list and is ready when the request fails', async () => {
    sdk.cfgAccountsOauthProvidersRetrieve.mockRejectedValue(new Error('down'));
    const { useOAuthProviders } = await import('../hooks/useOAuthProviders');
    const { result } = renderHook(() => useOAuthProviders());

    // Not ready while the retries run: the form holds the room of the buttons.
    await waitFor(() => expect(sdk.cfgAccountsOauthProvidersRetrieve).toHaveBeenCalledTimes(2), { timeout: 3000 });
    expect(result.current.isReady).toBe(false);
    await waitFor(() => expect(result.current.isReady).toBe(true), { timeout: 6000 });
    expect(sdk.cfgAccountsOauthProvidersRetrieve).toHaveBeenCalledTimes(3);
    expect(result.current.providers).toEqual([]);
  }, 10000);

  it('shows the buttons when the first request fails and a retry succeeds (flaky mobile network)', async () => {
    sdk.cfgAccountsOauthProvidersRetrieve
      .mockRejectedValueOnce(new Error('502'))
      .mockResolvedValue({ providers: [{ id: 'google', name: 'Google', icon: 'google' }] });
    const { useOAuthProviders } = await import('../hooks/useOAuthProviders');
    const { result } = renderHook(() => useOAuthProviders());

    await waitFor(() => expect(result.current.providers.map((p) => p.id)).toEqual(['google']), { timeout: 4000 });
    expect(result.current.isReady).toBe(true);
  }, 8000);

  it('persists the fetched list under the registry key', async () => {
    sdk.cfgAccountsOauthProvidersRetrieve.mockResolvedValue({ providers: [{ id: 'google', name: 'Google', icon: 'google' }] });
    const { useOAuthProviders } = await import('../hooks/useOAuthProviders');
    const { result } = renderHook(() => useOAuthProviders());

    await waitFor(() => expect(result.current.isReady).toBe(true));
    expect(JSON.parse(sessionStorage.getItem('cfg.auth.oauth_providers') ?? 'null')).toEqual([
      { id: 'google', name: 'Google', icon: 'google' },
    ]);
  });

  it('shows the cached list at once, then lets the server answer replace it', async () => {
    sessionStorage.setItem(
      'cfg.auth.oauth_providers',
      JSON.stringify([{ id: 'github', name: 'GitHub', icon: 'github' }]),
    );
    sdk.cfgAccountsOauthProvidersRetrieve.mockResolvedValue({ providers: [{ id: 'google', name: 'Google', icon: 'google' }] });
    const { useOAuthProviders } = await import('../hooks/useOAuthProviders');
    const { result } = renderHook(() => useOAuthProviders());

    expect(result.current.isReady).toBe(true);
    expect(result.current.providers.map((p) => p.id)).toEqual(['github']);
    await waitFor(() => expect(result.current.providers.map((p) => p.id)).toEqual(['google']));
    expect(sessionStorage.getItem('cfg.auth.oauth_providers')).toContain('google');
  });

  it('ignores an unreadable cache', async () => {
    sessionStorage.setItem('cfg.auth.oauth_providers', '{not json');
    sdk.cfgAccountsOauthProvidersRetrieve.mockResolvedValue({ providers: [] });
    const { useOAuthProviders } = await import('../hooks/useOAuthProviders');
    const { result } = renderHook(() => useOAuthProviders());

    expect(result.current.isReady).toBe(false);
    await waitFor(() => expect(result.current.isReady).toBe(true));
    expect(result.current.providers).toEqual([]);
  });
});
