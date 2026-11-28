'use client';

/**
 * AuthProvider — thin React layer over the generated auth store.
 *
 * Architecture rule (auth v2): the generated store (`_api/generated/helpers/auth`)
 * is the ONLY auth engine. It owns tokens, JWT-exp semantics, the reactive
 * session snapshot, 401→refresh→retry recovery (cross-store Web-Locks), and
 * the terminal-401 `onSessionExpired` event. React only:
 *   1. subscribes to the snapshot (`useSyncExternalStore`),
 *   2. loads the user profile when a session exists,
 *   3. routes to login when the store says the session died,
 *   4. exposes login/logout actions.
 *
 * Everything that used to live here — authTick, expiry timers, four parallel
 * 401 handlers, presence-vs-exp token checks — is the store's job now.
 */

import { usePathname } from 'next/navigation';
import React, {
  memo,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

import { auth } from '../../runtime/auth';
import { configureApi } from '../../runtime/api-origin';
import { APIError } from '../../runtime/errors';
import { CFG_KEYS } from '../../runtime/keys';
import { applyRoleLogPolicy } from '../../log-control';
import { useCfgRouter, useCfgStored, useQueryParams, useSession } from '../hooks';
import { clearProfileCache } from '../hooks/useProfileCache';
import { purgeLegacyTokenStorage } from '../hooks/legacyStorage';
import { useAuthRedirectManager } from '../hooks/useAuthRedirect';
import { Analytics, AnalyticsCategory, AnalyticsEvent } from '../utils/analytics';
import { formatAuthError, logAuthFailure } from '../utils/errors';
import { resolveAuthStatus } from '../utils/authState';
import { normalizePath } from '../utils/path';
import {
  buildSsoLoginUrl,
  configureSso,
  deriveAuthHost,
  getSsoState,
  hasReturnMarker,
  markReturn,
  stripReturnMarker,
  resolveSso,
  safeNext,
  warnSsoOff,
  type SsoConfig,
  type SsoState,
} from '../utils/sso';
import { authTrace } from '../trace';
import { isDev, isBrowser } from '../utils/env';
import { authLogger } from '../utils/logger';
import { AccountsProvider, useAccountsContext } from './AccountsContext';
import { sharedContext } from './sharedContext';

import type { AuthContextType, AuthProviderProps, UserProfile } from './types';
import type {
  OTPRequestConsent,
  OTPRequestResult,
  PasswordLoginOptions,
  PasswordLoginResult,
} from '../types';
import type { OTPRequestRequest } from '../../_api/models';

// The ONLY place route conventions are declared. '/auth' is the sign-in page
// convention and '/private' is the default landing page after sign-in
// (`defaultCallback`). Apps override via AuthConfig.routes;
// everything downstream reads the RESOLVED values from `useAuth().routes`.
const defaultRoutes = {
  auth: '/auth',
  defaultCallback: '/private',
  defaultAuthCallback: '/auth',
};

/** Resolve AuthConfig.routes against the conventions — applied exactly once. */
export const resolveAuthRoutes = (
  routes?: { auth?: string; defaultCallback?: string; defaultAuthCallback?: string },
) => ({
  auth: routes?.auth || defaultRoutes.auth,
  defaultCallback: routes?.defaultCallback || defaultRoutes.defaultCallback,
  defaultAuthCallback: routes?.defaultAuthCallback || routes?.auth || defaultRoutes.defaultAuthCallback,
});


const AuthContext = sharedContext<AuthContextType | undefined>('auth', undefined);

const AuthProviderInternal: React.FC<AuthProviderProps> = ({ children, config }) => {
  const accounts = useAccountsContext();
  const session = useSession();
  const isAuthenticated = session.status === 'authenticated';

  const router = useCfgRouter();
  const pathname = usePathname();
  const queryParams = useQueryParams();
  const [storedEmail, setStoredEmail, clearStoredEmail] = useCfgStored(CFG_KEYS.email);

  // Resolved once; every consumer below (and, via context, every component)
  // reads these — never the raw config and never a module constant.
  const routes = useMemo(() => resolveAuthRoutes(config?.routes), [config?.routes]);
  const routesRef = useRef(routes);
  useEffect(() => {
    routesRef.current = routes;
  }, [routes]);

  // ── Single sign-in host (off unless `config.sso` or NEXT_PUBLIC_AUTH_HOST is set) ──
  // Registered while rendering (idempotent) so the router and guards, which run in children's
  // effects before this provider's own, already see it.
  const ssoConfig = useMemo<SsoConfig | null>(() => {
    const opt: SsoConfig | null = config?.sso === true ? {} : config?.sso || null;
    const host =
      opt?.authHost ||
      opt?.host ||
      process.env.NEXT_PUBLIC_AUTH_HOST ||
      (opt ? deriveAuthHost(process.env.NEXT_PUBLIC_SITE_URL, opt.authLabel) : null) ||
      '';
    return host ? { ...opt, authHost: host, host: undefined, path: opt?.path ?? config?.routes?.auth } : null;
  }, [config?.sso, config?.routes?.auth]);
  configureSso(ssoConfig);
  const [sso, setSso] = useState<SsoState>(() => resolveSso(ssoConfig, null));
  useEffect(() => {
    const state = getSsoState();
    setSso(state);
    warnSsoOff(state, window.location.hostname);
    // The session must land on `.apex` whichever host finishes the sign-in (Google ends on the auth host).
    if (state.enabled) auth.setCookieDomain(ssoConfig?.cookieDomain || state.apex || 'auto');
  }, [ssoConfig]);

  const redirectManager = useAuthRedirectManager({
    fallbackUrl: routes.defaultCallback,
    clearOnUse: true,
  });

  const configRef = useRef(config);
  useEffect(() => {
    configRef.current = config;
  }, [config]);

  const accountsRef = useRef(accounts);
  useEffect(() => {
    accountsRef.current = accounts;
  }, [accounts]);

  // Set when a login flow opts out of automatic navigation (verifyOTP with
  // skipRedirect — the AuthLayout success screen owns the final hardPush,
  // including through a 2FA continuation). While set, the "redirect
  // authenticated users away from /auth" effect must stand down, otherwise it
  // races the success screen and eats the saved back-url.
  const pendingManualNavRef = useRef(false);

  // ── Bootstrap: settle the profile for the current session ─────────────────
  // The session itself needs no async bootstrap — the store answers
  // synchronously from token `exp`. The only async part is the profile fetch,
  // and it re-runs automatically when a session appears later (e.g. iframe
  // token delivery via postMessage → setSession → snapshot flips).
  const [profileSettled, setProfileSettled] = useState(false);
  const hasProfile = Boolean(accounts.profile);
  const accountsHydrated = accounts.isHydrated;
  const profileAttemptedRef = useRef(false);

  useEffect(() => {
    // Wait until AccountsProvider has applied the cached profile: deciding earlier would fetch a
    // profile the cache already holds, or settle before the cache is read.
    if (!accountsHydrated) return;
    if (!isAuthenticated) {
      profileAttemptedRef.current = false;
      // Dead tokens may still sit in storage (access AND refresh both
      // expired). Purge so the login form shows instantly instead of the app
      // firing doomed API calls — the automated "clear localStorage and the
      // form appears".
      //
      // CRITICAL: ask the STORE synchronously, never trust the React snapshot
      // here. During hydration useSyncExternalStore serves the SERVER snapshot
      // ('anonymous') for one commit even when perfectly live tokens sit in
      // storage — purging on that stale value nuked fresh logins (user typed
      // OTP → tokens saved → hardPush → hydration commit saw 'anonymous' →
      // tokens cleared → bounced back to /auth).
      const hasTokens = Boolean(auth.getToken() || auth.getRefreshToken());
      if (hasTokens && !auth.isAuthenticated()) {
        authLogger.warn('Dead session in storage — clearing');
        authTrace('bootstrap.purge', { why: 'dead-tokens' });
        auth.clearSession();
        clearProfileCache();
      } else if (!hasTokens && !auth.isAuthenticated()) {
        // No session at all: a leftover profile cache and the old localStorage tokens (pre-cookie auth) must not keep
        // the private UI alive. Drop them; the page's own guard then sends the user to /auth.
        authTrace('bootstrap.purge', { why: 'no-session' });
        clearProfileCache();
        purgeLegacyTokenStorage();
        if (accountsRef.current.profile) accountsRef.current.logout();
      }
      setProfileSettled(true);
      return;
    }
    if (hasProfile || profileAttemptedRef.current) {
      setProfileSettled(true);
      return;
    }
    profileAttemptedRef.current = true;
    authTrace('bootstrap.profile.start');
    let cancelled = false;
    accountsRef.current
      .refreshProfile({ callerId: 'AuthProvider:bootstrap' })
      .catch((error: unknown) => {
        // A terminal 401 collapses the session via the store's
        // onSessionExpired funnel below. Anything else (network, 5xx) keeps
        // the session — the user can retry.
        authLogger.warn('Profile load failed (session kept):', error);
        authTrace('bootstrap.profile.failed', {
          status: error instanceof APIError ? error.statusCode : 0,
        });
      })
      .finally(() => {
        if (!cancelled) setProfileSettled(true);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, hasProfile, accountsHydrated]);

  const isLoading = !profileSettled;

  // ── The one linear state ───────────────────────────────────────────────────
  // clientReady: the hydration commit is over (the server snapshot is always 'anonymous', so before this the
  // snapshot proves nothing). timedOut: ONE safety timer, so 'resolving' always ends.
  const [clientReady, setClientReady] = useState(false);
  const [timedOut, setTimedOut] = useState(false);
  useEffect(() => {
    setClientReady(true);
    const timer = setTimeout(() => setTimedOut(true), 8000);
    return () => clearTimeout(timer);
  }, []);
  const status = resolveAuthStatus({
    clientReady,
    snapshotAuthenticated: isAuthenticated,
    storeAuthenticated: isBrowser ? auth.isAuthenticated() : false,
    profileSettled,
    timedOut,
  });
  const lastStatusRef = useRef<string>('');
  useEffect(() => {
    if (lastStatusRef.current === status) return;
    lastStatusRef.current = status;
    authTrace('status', {
      status,
      snapshot: isAuthenticated,
      store: auth.isAuthenticated(),
      profileSettled,
      timedOut,
      path: pathname ?? '',
    });
  }, [status, isAuthenticated, profileSettled, timedOut, pathname]);
  useEffect(() => {
    (globalThis as Record<string, unknown>).__cfgAuthNow = () => ({
      status,
      snapshot: isAuthenticated,
      store: auth.isAuthenticated(),
      hasToken: Boolean(auth.getToken()),
      hasRefresh: Boolean(auth.getRefreshToken()),
      profileSettled,
      timedOut,
    });
  }, [status, isAuthenticated, profileSettled, timedOut]);

  // ── The ONE exit: terminal 401 → login ─────────────────────────────────────
  // The store has already cleared the session before this fires (subscribers
  // flipped to 'anonymous'), so the handler only routes. Registration returns
  // its own unsubscribe — StrictMode double-mounts compose instead of racing.
  // One hard navigation per page is enforced in useCfgRouter, so no per-handler dedupe flag is needed.
  useEffect(() => {
    const unsubscribe = auth.onSessionExpired(() => {
      authTrace('expired.handler', { path: pathname ?? '' });
      authLogger.warn('Session expired (terminal 401) — redirecting to login');
      clearProfileCache();
      Analytics.event(AnalyticsEvent.AUTH_SESSION_EXPIRED, {
        category: AnalyticsCategory.AUTH,
      });
      router.hardReplace(routesRef.current.defaultAuthCallback);
    });
    return unsubscribe;
  }, [router, pathname]);

  // ── Single sign-in: the two halves of the round trip ──────────────────────
  // Host: take `?next=` (validated: https, the apex or its subdomains, never the auth page) as the
  // saved back-url, so the existing post-sign-in navigation returns the visitor to it. It must
  // run before the "leave /auth when already signed in" effect below.
  useEffect(() => {
    if (!sso.enabled || !sso.isAuthHost || normalizePath(pathname) !== normalizePath(routes.auth)) return;
    const next = safeNext(queryParams.get('next'), sso.apex, sso.authPath);
    if (next) {
      redirectManager.setRedirect(markReturn(next));
      authTrace('sso.next', { to: next });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sso, pathname, queryParams]);

  // Back from the host with a session: the return marker has done its job, take it off the address bar.
  useEffect(() => {
    if (!sso.enabled || sso.isAuthHost || !isAuthenticated || !hasReturnMarker(window.location.href)) return;
    window.history.replaceState(window.history.state, '', stripReturnMarker(window.location.href));
  }, [sso, isAuthenticated]);

  // Follower: this host never renders the form. Whoever lands on its /auth goes to the host.
  useEffect(() => {
    if (!sso.enabled || sso.isAuthHost || isAuthenticated) return;
    if (normalizePath(pathname) !== normalizePath(routes.auth)) return;
    const back =
      safeNext(queryParams.get('next'), sso.apex, sso.authPath) ??
      `${window.location.origin}${routes.defaultCallback}`;
    const url = buildSsoLoginUrl(sso, back);
    if (url) {
      authTrace('sso.to-host', { to: url });
      router.hardReplace(url);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sso, pathname, isAuthenticated]);

  // ── Redirect authenticated users away from the auth page ──────────────────
  // Stands down while a login flow on this page owns navigation (success
  // screen / 2FA continuation — see pendingManualNavRef). When it does fire
  // (an already-authenticated user landing on /auth), it honors the saved
  // back-url with the same priority rule as every other consumer.
  useEffect(() => {
    if (!isAuthenticated || pendingManualNavRef.current) return;
    // `sso_error`: the follower could not see the shared session; leaving would send the visitor straight back.
    if (pathname === routes.auth && !queryParams.get('flow') && !queryParams.get('sso_error')) {
      const saved = redirectManager.hasRedirect() ? redirectManager.getRedirect() : null;
      if (saved) redirectManager.clearRedirect();
      authTrace('leave-auth', { to: saved || routes.defaultCallback, saved: Boolean(saved) });
      router.push(saved || routes.defaultCallback);
    }
  }, [isAuthenticated, pathname, queryParams, routes, router, redirectManager]);

  // ── Profile actions (delegated to AccountsContext) ─────────────────────────

  const loadCurrentProfile = useCallback(async (callerId?: string): Promise<void> => {
    if (!auth.isAuthenticated()) {
      throw new Error('No valid authentication token');
    }
    await accountsRef.current.refreshProfile({
      callerId: callerId || 'AuthContext.loadCurrentProfile',
    });
  }, []);

  const checkAuthAndRedirect = useCallback(async (): Promise<void> => {
    if (auth.isAuthenticated()) {
      try {
        await loadCurrentProfile('checkAuthAndRedirect');
      } catch (error) {
        authLogger.warn('checkAuthAndRedirect: profile load failed', error);
      }
      router.push(routesRef.current.defaultCallback);
    } else {
      router.push(routesRef.current.defaultAuthCallback);
    }
  }, [loadCurrentProfile, router]);

  // ── OTP login flow ─────────────────────────────────────────────────────────

  const requestOTP = useCallback(
    async (identifier: string, sourceUrl?: string, consent?: OTPRequestConsent): Promise<OTPRequestResult> => {
      // A login attempt invalidates whatever session was lying around.
      authTrace('otp.request');
      auth.clearSession();

      try {
        const body: OTPRequestRequest = {
          identifier,
          source_url: sourceUrl,
          // Absent when the consuming app didn't enable the opt-in checkbox —
          // the backend treats absent/null as "not asked".
          ...(consent && {
            marketing_consent: consent.marketingConsent,
            consent_disclosure_version: consent.disclosureVersion,
          }),
        };
        const result = await accountsRef.current.requestOTP(body);

        Analytics.event(AnalyticsEvent.AUTH_OTP_REQUEST, {
          category: AnalyticsCategory.AUTH,
          label: 'email',
        });

        return {
          success: true,
          message: result.message || 'OTP code sent to your email address',
          webmail: result.webmail ?? null,
          resendIn: result.resend_in,
        };
      } catch (error) {
        logAuthFailure(authLogger, 'Request OTP failed:', error);

        if (error instanceof APIError) {
          const body = error.response as
            | { retry_after?: number; retryAfter?: number }
            | undefined;
          const retryAfter = body?.retry_after ?? body?.retryAfter;
          return {
            success: false,
            statusCode: error.statusCode,
            message: formatAuthError(error),
            retryAfter: typeof retryAfter === 'number' ? retryAfter : undefined,
          };
        }
        return { success: false, message: formatAuthError(error, 'Failed to send OTP') };
      }
    },
    [],
  );

  const verifyOTP = useCallback(
    async (
      identifier: string,
      otpCode: string,
      sourceUrl?: string,
      redirectUrl?: string,
      skipRedirect?: boolean,
    ): Promise<{
      success: boolean;
      message: string;
      user?: UserProfile;
      requires_2fa?: boolean;
      session_id?: string | null;
      should_prompt_2fa?: boolean;
    }> => {
      try {
        // The caller opting out of redirect commits to handling ALL navigation
        // for this login — including the 2FA continuation and success screen.
        pendingManualNavRef.current = Boolean(skipRedirect);
        authTrace('otp.verify', { skipRedirect: Boolean(skipRedirect) });

        const result = await accountsRef.current.verifyOTP({
          identifier,
          otp: otpCode,
          source_url: sourceUrl,
        });

        if (result.requires_2fa && result.session_id) {
          authLogger.info('2FA required, session:', result.session_id);
          return {
            success: true,
            message: 'OTP verified, 2FA required',
            requires_2fa: true,
            session_id: result.session_id,
            should_prompt_2fa: result.should_prompt_2fa,
          };
        }

        if (!result.access || !result.refresh) {
          authLogger.error('Verify OTP returned invalid response:', result);
          return { success: false, message: 'Invalid OTP verification response' };
        }
        if (identifier.includes('@')) {
          setStoredEmail(identifier);
        }

        Analytics.event(AnalyticsEvent.AUTH_LOGIN_SUCCESS, {
          category: AnalyticsCategory.AUTH,
          label: 'email',
        });
        if (result.user?.id) {
          Analytics.setUser(String(result.user.id));
        }

        if (!skipRedirect) {
          // Priority: saved back-url (per-visit intent from the guard) >
          // explicit redirectUrl (static app default) > config default.
          // hardPush = full page load so every context reinitializes cleanly.
          const saved = redirectManager.hasRedirect() ? redirectManager.getRedirect() : null;
          if (saved) redirectManager.clearRedirect();
          const finalRedirectUrl = saved || redirectUrl || routesRef.current.defaultCallback;
          authLogger.info('Redirecting after auth to:', finalRedirectUrl);
          router.hardPush(finalRedirectUrl);
        }

        return {
          success: true,
          message: 'Login successful',
          user: result.user as UserProfile,
          should_prompt_2fa: result.should_prompt_2fa,
        };
      } catch (error) {
        logAuthFailure(authLogger, 'Verify OTP failed:', error);
        Analytics.event(AnalyticsEvent.AUTH_OTP_VERIFY_FAIL, {
          category: AnalyticsCategory.AUTH,
          label: 'email',
        });
        if (error instanceof APIError) {
          return { success: false, message: formatAuthError(error) };
        }
        return { success: false, message: formatAuthError(error, 'Failed to verify OTP') };
      }
    },
    [setStoredEmail, redirectManager, router],
  );

  // ── Password login flow ────────────────────────────────────────────────────

  // Same envelope, same branches and the same single session owner as
  // verifyOTP — only the credential differs. Anything that diverges here
  // (a second token store, a bespoke fetch) forks the session.
  const login = useCallback(
    async (
      email: string,
      password: string,
      options?: PasswordLoginOptions,
    ): Promise<PasswordLoginResult> => {
      const { redirectUrl, skipRedirect } = options || {};

      try {
        // The caller opting out of redirect commits to handling ALL navigation
        // for this login — including the 2FA continuation and success screen.
        pendingManualNavRef.current = Boolean(skipRedirect);
        authTrace('password.login', { skipRedirect: Boolean(skipRedirect) });

        const result = await accountsRef.current.loginWithPassword({
          email,
          password,
        });

        if (result.requires_2fa && result.session_id) {
          authLogger.info('2FA required, session:', result.session_id);
          return {
            success: true,
            message: 'Password verified, 2FA required',
            requires_2fa: true,
            session_id: result.session_id,
            should_prompt_2fa: result.should_prompt_2fa,
          };
        }

        if (!result.access || !result.refresh) {
          authLogger.error('Password login returned invalid response:', result);
          return { success: false, message: 'Invalid login response' };
        }
        setStoredEmail(email);

        Analytics.event(AnalyticsEvent.AUTH_LOGIN_SUCCESS, {
          category: AnalyticsCategory.AUTH,
          label: 'password',
        });
        if (result.user?.id) {
          Analytics.setUser(String(result.user.id));
        }

        if (!skipRedirect) {
          // Priority: saved back-url (per-visit intent from the guard) >
          // explicit redirectUrl (static app default) > config default.
          // hardPush = full page load so every context reinitializes cleanly.
          const saved = redirectManager.hasRedirect() ? redirectManager.getRedirect() : null;
          if (saved) redirectManager.clearRedirect();
          const finalRedirectUrl = saved || redirectUrl || routesRef.current.defaultCallback;
          authLogger.info('Redirecting after auth to:', finalRedirectUrl);
          router.hardPush(finalRedirectUrl);
        }

        return {
          success: true,
          message: 'Login successful',
          user: result.user as UserProfile,
          should_prompt_2fa: result.should_prompt_2fa,
        };
      } catch (error) {
        logAuthFailure(authLogger, 'Password login failed:', error);
        Analytics.event(AnalyticsEvent.AUTH_PASSWORD_LOGIN_FAIL, {
          category: AnalyticsCategory.AUTH,
          label: 'password',
        });
        if (error instanceof APIError) {
          // 429 carries `retry_after`; 401 carries only `error_code`. Both are
          // surfaced so a form can show a countdown instead of a dead message.
          const body = error.response as
            | { error_code?: string; retry_after?: number }
            | undefined;
          return {
            success: false,
            statusCode: error.statusCode,
            message: formatAuthError(error),
            errorCode: body?.error_code,
            retryAfter: typeof body?.retry_after === 'number' ? body.retry_after : undefined,
          };
        }
        return { success: false, message: formatAuthError(error, 'Failed to sign in') };
      }
    },
    [setStoredEmail, redirectManager, router],
  );

  // ── Session actions ────────────────────────────────────────────────────────

  const refreshToken = useCallback(async (): Promise<{ success: boolean; message: string }> => {
    // Same single-flight + Web-Locks path as the 401 interceptor — rotation,
    // dedup and rotated-token persistence come for free.
    const access = await auth.refreshNow();
    if (access) {
      Analytics.event(AnalyticsEvent.AUTH_TOKEN_REFRESH, {
        category: AnalyticsCategory.AUTH,
      });
      return { success: true, message: 'Token refreshed' };
    }
    Analytics.event(AnalyticsEvent.AUTH_TOKEN_REFRESH_FAIL, {
      category: AnalyticsCategory.AUTH,
    });
    return { success: false, message: 'Error refreshing token' };
  }, []);

  const logout = useCallback((): void => {
    authTrace('logout');
    Analytics.event(AnalyticsEvent.AUTH_LOGOUT, {
      category: AnalyticsCategory.AUTH,
    });
    accountsRef.current.logout(); // clears session + profile + cache
    // hardReplace = full reload + history replace, so contexts reinitialize
    // and Back doesn't return to a protected page.
    router.hardReplace(routesRef.current.defaultAuthCallback, { next: false });
  }, [router]);

  // ── Derived state ──────────────────────────────────────────────────────────

  // Hydration-safe: AccountsProvider keeps the profile undefined until after the hydration commit,
  // so `user` / `isAdminUser` render as a guest on the server and on the first client render alike.
  const isHydrated = clientReady && accountsHydrated;
  const user = (accounts.profile as UserProfile | undefined) ?? null;
  const isAdminUser = Boolean(user?.is_staff || user?.is_superuser);

  // Role-aware console verbosity: admins (and dev) get debug logs, regular
  // users in production get a clean console.
  useEffect(() => {
    applyRoleLogPolicy({ isAdmin: isAdminUser });
  }, [isAdminUser]);

  const updateProfile = useCallback(
    async (data: {
      first_name?: string;
      last_name?: string;
      username?: string;
    }): Promise<UserProfile> => {
      const result = await accountsRef.current.partialUpdateProfile(data);
      return result as UserProfile;
    },
    [],
  );

  const uploadAvatar = useCallback(async (avatar: File | Blob): Promise<UserProfile> => {
    const result = await accountsRef.current.uploadAvatar(avatar);
    return result as UserProfile;
  }, []);

  const value = useMemo<AuthContextType>(
    () => ({
      user,
      isLoading,
      status,
      isHydrated,
      // Reactive: flips via the store snapshot (token writes, refreshes,
      // expiry timer, cross-tab/cross-store sync) — no ticks, no polling.
      isAuthenticated,
      isAdminUser,
      routes,
      sso,
      loadCurrentProfile,
      checkAuthAndRedirect,
      getToken: () => auth.getToken(),
      getRefreshToken: () => auth.getRefreshToken(),
      getSavedEmail: () => storedEmail,
      saveEmail: setStoredEmail,
      clearSavedEmail: clearStoredEmail,
      requestOTP,
      verifyOTP,
      login,
      refreshToken,
      logout,
      saveRedirectUrl: redirectManager.setRedirect,
      getRedirectUrl: redirectManager.getFinalRedirectUrl,
      clearRedirectUrl: redirectManager.clearRedirect,
      hasRedirectUrl: redirectManager.hasRedirect,
      updateProfile,
      uploadAvatar,
    }),
    [
      user,
      isLoading,
      status,
      isHydrated,
      isAuthenticated,
      isAdminUser,
      routes,
      sso,
      loadCurrentProfile,
      checkAuthAndRedirect,
      storedEmail,
      setStoredEmail,
      clearStoredEmail,
      requestOTP,
      verifyOTP,
      login,
      refreshToken,
      logout,
      redirectManager,
      updateProfile,
      uploadAvatar,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * AuthProvider — wraps AccountsProvider + AuthProviderInternal.
 *
 * Memoised: re-renders only when `config` reference or `children` change.
 */
function AuthProviderRaw({ children, config, enabled = true }: AuthProviderProps) {
  if (!enabled) return <>{children}</>;

  // Configure synchronously, before AccountsProvider effects or any child can
  // issue a generated operation. This is deliberately not an effect: the
  // first browser bootstrap request must already target the direct API host.
  if (config?.apiUrl !== undefined) configureApi({ apiUrl: config.apiUrl });

  return (
    <AccountsProvider>
      <AuthProviderInternal config={config}>{children}</AuthProviderInternal>
    </AccountsProvider>
  );
}

export const AuthProvider = memo(AuthProviderRaw);

/**
 * Default auth state for SSR/outside provider.
 * Safe defaults that read as "not authenticated, not loading".
 */
const defaultAuthState: AuthContextType = {
  user: null,
  isLoading: false,
  status: 'anonymous',
  // Outside a provider nothing is ever applied after mount: the value is final.
  isHydrated: true,
  isAuthenticated: false,
  isAdminUser: false,
  routes: resolveAuthRoutes(),
  loadCurrentProfile: async () => {
    authLogger.warn('useAuth: loadCurrentProfile called outside AuthProvider');
  },
  checkAuthAndRedirect: async () => {
    authLogger.warn('useAuth: checkAuthAndRedirect called outside AuthProvider');
  },
  getToken: () => null,
  getRefreshToken: () => null,
  getSavedEmail: () => null,
  saveEmail: () => {
    authLogger.warn('useAuth: saveEmail called outside AuthProvider');
  },
  clearSavedEmail: () => {},
  requestOTP: async () => {
    authLogger.warn('useAuth: requestOTP called outside AuthProvider');
    return { success: false, message: 'AuthProvider not available' };
  },
  verifyOTP: async () => {
    authLogger.warn('useAuth: verifyOTP called outside AuthProvider');
    return { success: false, message: 'AuthProvider not available' };
  },
  login: async () => {
    authLogger.warn('useAuth: login called outside AuthProvider');
    return { success: false, message: 'AuthProvider not available' };
  },
  refreshToken: async () => {
    authLogger.warn('useAuth: refreshToken called outside AuthProvider');
    return { success: false, message: 'AuthProvider not available' };
  },
  logout: () => {
    authLogger.warn('useAuth: logout called outside AuthProvider');
  },
  saveRedirectUrl: () => {},
  getRedirectUrl: () => '',
  clearRedirectUrl: () => {},
  hasRedirectUrl: () => false,
  updateProfile: async () => {
    authLogger.warn('useAuth: updateProfile called outside AuthProvider');
    return {} as UserProfile;
  },
  uploadAvatar: async () => {
    authLogger.warn('useAuth: uploadAvatar called outside AuthProvider');
    return {} as UserProfile;
  },
};

/**
 * Hook to access auth context.
 *
 * SSR-safe: returns default unauthenticated state when called outside
 * AuthProvider (e.g. during static page generation).
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    if (isBrowser && isDev) {
      authLogger.debug('useAuth called outside AuthProvider, returning default state');
    }
    return defaultAuthState;
  }
  return context;
};

export default AuthContext;
