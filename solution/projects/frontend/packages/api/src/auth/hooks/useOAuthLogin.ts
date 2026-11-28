'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import {
  cfgAccountsOauthGithubAuthorizeCreate,
  cfgAccountsOauthGithubCallbackCreate,
  cfgAccountsOauthGoogleAuthorizeCreate,
  cfgAccountsOauthGoogleCallbackCreate,
} from '../../_api/endpoints';
import type {
  OAuthAuthorizeRequestRequest,
  OAuthAuthorizeResponse,
  OAuthCallbackRequestRequest,
  OAuthTokenResponse,
} from '../../_api/models';
import { auth } from '../../runtime/auth';
import { CFG_KEYS, cfgStorage } from '../../runtime/keys';
import { Analytics, AnalyticsCategory, AnalyticsEvent } from '../utils/analytics';
import { authLogger } from '../utils/logger';
import { type OAuthFailureCode, type OAuthProviderId, readOAuthFailure } from '../utils/oauthErrors';
import { consumeSavedRedirect } from './useAuthRedirect';
import { useCfgRouter } from './useCfgRouter';
import { authTrace } from '../trace';

/**
 * The user payload as the OAuth endpoint declares it.
 *
 * Derived from the generated response rather than restated, so a schema change
 * reaches callers through `make generate` instead of drifting silently.
 */
export type OAuthUser = NonNullable<OAuthTokenResponse['user']>;

interface OAuthAdapter {
  authorize: (body: OAuthAuthorizeRequestRequest) => Promise<OAuthAuthorizeResponse>;
  callback: (body: OAuthCallbackRequestRequest) => Promise<OAuthTokenResponse>;
}

/**
 * One entry per provider the backend can offer. Keyed by the generated enum:
 * when the backend adds a provider, this stops compiling until it is wired.
 */
const ADAPTERS: Record<OAuthProviderId, OAuthAdapter> = {
  github: {
    authorize: async (body) =>
      cfgAccountsOauthGithubAuthorizeCreate(body),
    callback: async (body) =>
      cfgAccountsOauthGithubCallbackCreate(body),
  },
  google: {
    authorize: async (body) =>
      cfgAccountsOauthGoogleAuthorizeCreate(body),
    callback: async (body) =>
      cfgAccountsOauthGoogleCallbackCreate(body),
  },
};

/** Provider ids this client can run, in the order the adapters are declared. */
export const OAUTH_PROVIDER_IDS = Object.keys(ADAPTERS) as OAuthProviderId[];

export const isOAuthProviderId = (value: unknown): value is OAuthProviderId =>
  typeof value === 'string' && Object.hasOwn(ADAPTERS, value);

const STATE_KEY = CFG_KEYS.oauthState.key;
const PROVIDER_KEY = CFG_KEYS.oauthProvider.key;

/** Forget the stored state: the attempt is over without an exchange (Cancel, a provider error). */
export const clearOAuthAttempt = (): void => {
  cfgStorage.remove(STATE_KEY);
  cfgStorage.remove(PROVIDER_KEY);
};

export interface UseOAuthLoginOptions {
  sourceUrl?: string;
  /** The endpoint types `user` as a free-form object; narrow it at the call site. */
  onSuccess?: (user: OAuthUser, isNewUser: boolean, provider: OAuthProviderId) => void;
  /** `message` is server prose or an English fallback; `code` lets the caller choose its own copy. */
  onError?: (message: string, code?: OAuthFailureCode) => void;
  /** Called when 2FA is required instead of a session. */
  onRequires2FA?: (sessionId: string, shouldPrompt2FA: boolean) => void;
  redirectUrl?: string;
  /** Skip the automatic redirect after success (the caller navigates). */
  skipRedirect?: boolean;
}

export interface UseOAuthLoginReturn {
  /** True from the click until the page leaves (start) or the exchange settles (complete). */
  isLoading: boolean;
  /** The provider whose flow is in flight; disable the other buttons, show progress on this one. */
  loadingProvider: OAuthProviderId | null;
  error: string | null;
  errorCode: OAuthFailureCode | null;
  /** Redirects the tab to the provider. Resolves only if it failed to start. */
  start: (provider: OAuthProviderId) => Promise<void>;
  /** Exchanges the `code` the provider returned. The stored `state` must match; there is no unchecked path. */
  complete: (provider: OAuthProviderId, code: string, state: string) => Promise<void>;
}

/**
 * Sign in with a third-party provider: one hook for every provider.
 *
 * Flow, full page in the same tab so the saved return URL survives:
 * `start(provider)` stores the server's `state`, then navigates to the provider.
 * The provider returns to `/auth?provider=<id>&code&state`; `complete(...)`
 * verifies that `state` against the stored one (login CSRF defence), exchanges
 * the code and writes the session.
 */
export const useOAuthLogin = (options: UseOAuthLoginOptions = {}): UseOAuthLoginReturn => {
  const router = useCfgRouter();

  const optionsRef = useRef(options);
  optionsRef.current = options;
  const routerRef = useRef(router);
  routerRef.current = router;

  const [loadingProvider, setLoadingProvider] = useState<OAuthProviderId | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<OAuthFailureCode | null>(null);

  // Coming back with the back button restores this page from the bfcache with
  // the spinner still on; the provider page was left, so the flow is over.
  useEffect(() => {
    const onShow = (event: PageTransitionEvent) => {
      if (event.persisted) setLoadingProvider(null);
    };
    window.addEventListener('pageshow', onShow);
    return () => window.removeEventListener('pageshow', onShow);
  }, []);

  const fail = useCallback((provider: OAuthProviderId, message: string, code?: OAuthFailureCode) => {
    setError(message);
    setErrorCode(code ?? null);
    setLoadingProvider(null);
    optionsRef.current.onError?.(message, code);
    Analytics.event(AnalyticsEvent.AUTH_OAUTH_FAIL, {
      category: AnalyticsCategory.AUTH,
      label: provider,
    });
  }, []);

  const start = useCallback(async (provider: OAuthProviderId) => {
    setLoadingProvider(provider);
    setError(null);
    setErrorCode(null);
    // Match the OTP flow: a new login must not leave an older persistent
    // session available after this browser is intentionally made session-only.
    authTrace('oauth.start');
    auth.clearSession();

    try {
      Analytics.event(AnalyticsEvent.AUTH_OAUTH_START, {
        category: AnalyticsCategory.AUTH,
        label: provider,
      });

      // No `redirect_uri`: the server derives it from the request origin.
      const sourceUrl = optionsRef.current.sourceUrl || window.location.href;
      const response = await ADAPTERS[provider].authorize({ source_url: sourceUrl });
      if (!response.authorization_url || !response.state) {
        throw new Error('Failed to get authorization URL');
      }

      cfgStorage.write(STATE_KEY, response.state);
      cfgStorage.write(PROVIDER_KEY, provider);
      authLogger.info(`Redirecting to ${provider}...`);
      // Loading stays on: the tab is leaving.
      window.location.href = response.authorization_url;
    } catch (err) {
      authLogger.error(`${provider} OAuth start error:`, err);
      const failure = readOAuthFailure(err, 'Failed to start authentication');
      fail(provider, failure.message, failure.code);
    }
  }, [fail]);

  const complete = useCallback(async (provider: OAuthProviderId, code: string, state: string) => {
    setLoadingProvider(provider);
    setError(null);
    setErrorCode(null);

    // The stored state is the proof that THIS browser started the flow. A
    // missing one is as wrong as a different one: an attacker's link carries a
    // valid code and state for the attacker's account. Spent before any await.
    const storedState = cfgStorage.read(STATE_KEY);
    const storedProvider = cfgStorage.read(PROVIDER_KEY);
    clearOAuthAttempt();
    if (!storedState || storedState !== state || (storedProvider && storedProvider !== provider)) {
      authLogger.warn(`${provider} OAuth callback rejected: state does not match this browser`);
      fail(provider, 'Invalid sign-in attempt. Please try again.', 'invalid_state');
      return;
    }

    try {
      const response = await ADAPTERS[provider].callback({ code, state });

      if (response.requires_2fa && response.session_id) {
        Analytics.event(AnalyticsEvent.AUTH_OAUTH_START, {
          category: AnalyticsCategory.AUTH,
          label: `${provider}-2fa-required`,
        });
        optionsRef.current.onRequires2FA?.(response.session_id, response.should_prompt_2fa || false);
        setLoadingProvider(null);
        return;
      }

      if (!response.access || !response.refresh) {
        throw new Error('Invalid response from OAuth callback');
      }

      // The ONE write path — atomic pair + session notification.
      authTrace('oauth.session');
      auth.setSession({ access: response.access, refresh: response.refresh });

      Analytics.event(AnalyticsEvent.AUTH_LOGIN_SUCCESS, {
        category: AnalyticsCategory.AUTH,
        label: provider,
      });
      if (response.user?.id) {
        Analytics.setUser(String(response.user.id));
      }
      if (response.user) {
        optionsRef.current.onSuccess?.(response.user, response.is_new_user || false, provider);
      }

      setLoadingProvider(null);
      if (!optionsRef.current.skipRedirect) {
        // Full reload so every React context reinitialises with the new session.
        // The saved back-url (where a guard bounced the visitor from) comes first.
        routerRef.current.hardPush(consumeSavedRedirect() || optionsRef.current.redirectUrl || '/private');
      }
    } catch (err) {
      authLogger.error(`${provider} OAuth callback error:`, err);
      const failure = readOAuthFailure(err, 'Authentication failed');
      fail(provider, failure.message, failure.code);
    }
  }, [fail]);

  return {
    isLoading: loadingProvider !== null,
    loadingProvider,
    error,
    errorCode,
    start,
    complete,
  };
};
