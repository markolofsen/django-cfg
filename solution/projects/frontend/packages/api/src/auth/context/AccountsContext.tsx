/**
 * CfgAccounts Context
 *
 * Manages user authentication and profile operations using generated Orval
 * operations. React Query hooks remain available to UI consumers; this root
 * context uses direct operations so auth bootstrap does not depend on a
 * QueryClientProvider being mounted by the host app.
 *
 * Features:
 * - OTP-based authentication
 * - User profile management
 * - Avatar upload
 * - Profile updates
 * - localStorage cache with TTL (1 hour)
 */

"use client";

import {
    ReactNode, useCallback, useContext, useEffect, useLayoutEffect, useMemo, useRef, useState
} from 'react';

import {
    cfgAccountsProfileAvatarCreate,
    cfgAccountsProfilePartialUpdate,
    cfgAccountsProfileUpdateUpdate,
    cfgAccountsProfileRetrieve,
    cfgAccountsOtpRequestCreate,
    cfgAccountsOtpVerifyCreate,
    cfgAccountsTokenCreate,
    cfgAccountsTokenBlacklistCreate,
} from '../../_api/endpoints';
import { hasApiOrigin } from '../../runtime/api-origin';
import { auth } from '../../runtime/auth';
import { clearProfileCache, getCachedProfile, setCachedProfile } from '../hooks/useProfileCache';
import { authLogger } from '../utils/logger';

import type {
    User,
    CfgUserUpdateRequest,
    PatchedCfgUserUpdateRequest,
    OTPRequestRequest,
    OTPVerifyRequest,
    OTPRequestResponse,
    OTPVerifyResponse,
    PasswordLoginRequest,
    PasswordLoginResponse,
} from '../../_api/models';
import { authTrace } from '../trace';
import { sharedContext } from './sharedContext';

export type { PatchedCfgUserUpdateRequest, User, CfgUserUpdateRequest as UserProfileUpdateRequest };

/** `useLayoutEffect` in the browser, `useEffect` on the server (where neither runs). */
const useIsomorphicLayoutEffect = typeof window === 'undefined' ? useEffect : useLayoutEffect;

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface AccountsContextValue {
  /**
   * The signed-in user's profile. `undefined` on the server AND on the first client render (the
   * hydration render), so a server-rendered tree draws the same guest markup on both sides; the
   * cached profile is applied right after mount (see `isHydrated`).
   */
  profile?: User;
  /** `false` on the server and during the hydration render; `true` once the stored profile has been applied. */
  isHydrated: boolean;
  isLoadingProfile: boolean;
  profileError: Error | null;

  updateProfile: (data: CfgUserUpdateRequest) => Promise<User>;
  partialUpdateProfile: (data: PatchedCfgUserUpdateRequest) => Promise<User>;
  uploadAvatar: (avatar: File | Blob) => Promise<User>;
  refreshProfile: (options?: { callerId?: string; force?: boolean }) => Promise<User | undefined>;

  requestOTP: (data: OTPRequestRequest) => Promise<OTPRequestResponse>;
  verifyOTP: (data: OTPVerifyRequest) => Promise<OTPVerifyResponse>;
  loginWithPassword: (data: PasswordLoginRequest) => Promise<PasswordLoginResponse>;
  logout: () => void;
}

const AccountsContext = sharedContext<AccountsContextValue | undefined>('accounts', undefined);

interface AccountsProviderProps {
  children: ReactNode;
}

export function AccountsProvider({ children }: AccountsProviderProps) {
  // The server never sees localStorage, so it always renders a guest. Reading the cache in a
  // `useState` initializer made the FIRST client render differ from that HTML (React #418 wherever
  // `user` / `isAdminUser` changes the markup). The cache is applied after mount instead.
  const [profile, setProfile] = useState<User | undefined>(undefined);
  const [isHydrated, setIsHydrated] = useState(false);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [profileError, setProfileError] = useState<Error | null>(null);

  const profileRef = useRef<User | undefined>(profile);

  // Layout effect: runs after the hydration commit but before paint, so a signed-in visitor does not
  // see a guest frame. A fetch that already landed (profileRef set) wins over the cache.
  useIsomorphicLayoutEffect(() => {
    // A cached profile is only a head start for a live session; with no session (tokens gone after the
    // move to cookies, or signed out elsewhere) it would render the private UI with nothing behind it.
    if (!auth.isAuthenticated()) {
      clearProfileCache();
    } else if (!profileRef.current) {
      const cached = getCachedProfile() as User | null;
      if (cached) {
        profileRef.current = cached;
        setProfile(cached);
      }
    }
    authTrace('accounts.hydrated', { cached: Boolean(profileRef.current) });
    setIsHydrated(true);
  }, []);
  const isLoadingRef = useRef(false);
  // Monotonic id per fetch. A forced re-read can now overlap the bootstrap
  // one, and the slower response must not overwrite the newer profile.
  const fetchSeqRef = useRef(0);

  useEffect(() => {
    profileRef.current = profile;
  }, [profile]);

  useEffect(() => {
    isLoadingRef.current = isLoadingProfile;
  }, [isLoadingProfile]);

  const refreshProfile = useCallback(async (options?: { callerId?: string; force?: boolean }): Promise<User | undefined> => {
    const { callerId, force } = options || {};

    // No API origin configured → skip the request instead of letting it resolve
    // against the current page. A relative URL on an i18n-prefixed route turns
    // `/cfg/accounts/profile` into `/<locale>/cfg/accounts/profile` on the
    // site's own origin — a 404 that only ever shows up in production.
    // `hasApiOrigin` is the transport's own resolver (`runtime/api-origin.ts`), so
    // the guard and the request agree; a same-origin proxy or a static build counts
    // as configured.
    if (!hasApiOrigin()) {
      authLogger.debug(`No API origin configured, skipping profile fetch (caller: ${callerId})`);
      return undefined;
    }

    // `force` is how a write says "I just changed the server, re-read it".
    // Honouring the in-flight guard there would hand the caller back the
    // pre-write profile and never fetch again, so the UI keeps showing the
    // old value indefinitely.
    if (isLoadingRef.current && !force) {
      authLogger.debug(`Profile loading in progress, skipping (caller: ${callerId})`);
      return profileRef.current;
    }

    const seq = ++fetchSeqRef.current;
    setIsLoadingProfile(true);
    isLoadingRef.current = true;
    setProfileError(null);
    try {
      authLogger.debug(`Fetching profile from API (caller: ${callerId}, force: ${force})`);
      const result = await cfgAccountsProfileRetrieve();
      // A newer fetch already landed — its profile is the current one, and
      // this older response would roll it back.
      if (seq !== fetchSeqRef.current) return result;
      setProfile(result);
      profileRef.current = result;
      setCachedProfile(result);
      return result;
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Failed to fetch profile');
      if (seq === fetchSeqRef.current) setProfileError(err);
      throw err;
    } finally {
      if (seq === fetchSeqRef.current) {
        setIsLoadingProfile(false);
        isLoadingRef.current = false;
      }
    }
  }, []);

  // These five are `useCallback`ed because they are dependencies of the context
  // `useMemo` below. Rebuilt each render, they made that memo return a new object
  // every time — so every consumer of this root provider re-rendered on every
  // render of it, and the memo bought nothing. Direct generated operations are
  // stable module functions, so the context can keep this memo narrow.
  const updateProfile = useCallback(async (data: CfgUserUpdateRequest): Promise<User> => {
    await cfgAccountsProfileUpdateUpdate(data);
    const user = await refreshProfile({ callerId: 'updateProfile', force: true });
    return user as User;
  }, [refreshProfile]);

  const partialUpdateProfile = useCallback(async (data: PatchedCfgUserUpdateRequest): Promise<User> => {
    await cfgAccountsProfilePartialUpdate(data);
    const user = await refreshProfile({ callerId: 'partialUpdateProfile', force: true });
    return user as User;
  }, [refreshProfile]);

  const uploadAvatar = useCallback(async (avatar: File | Blob): Promise<User> => {
    await cfgAccountsProfileAvatarCreate({ avatar });
    const user = await refreshProfile({ callerId: 'uploadAvatar', force: true });
    return user as User;
  }, [refreshProfile]);

  const requestOTP = useCallback(async (data: OTPRequestRequest): Promise<OTPRequestResponse> => {
    return cfgAccountsOtpRequestCreate(data);
  }, []);

  // OTP verify and password login return the SAME envelope by design, so both
  // settle it here — one 2FA branch, one token write, one profile refresh. A
  // second copy of this is a second session owner.
  const settleLoginEnvelope = useCallback(async (
    result: OTPVerifyResponse | PasswordLoginResponse,
    callerId: string,
  ): Promise<void> => {
    if (result.requires_2fa && result.session_id) {
      authLogger.info('2FA required, session:', result.session_id);
      return;
    }

    if (result.access && result.refresh) {
      // The ONE write path — atomic pair, notifies every session subscriber.
      // Storage is always localStorage: session length is the token lifetime
      // the server chose. A sessionStorage switch would strand the tokens — the
      // module reinitializes to localStorage on the next page load.
      authTrace('accounts.otp.session');
      auth.setSession({ access: result.access, refresh: result.refresh });
      try {
        await refreshProfile({ callerId, force: true });
      } catch (profileError) {
        authLogger.warn(`Profile refresh failed after ${callerId} (tokens are saved):`, profileError);
      }
    }
  }, [refreshProfile]);

  const verifyOTP = useCallback(async (data: OTPVerifyRequest): Promise<OTPVerifyResponse> => {
    const result = await cfgAccountsOtpVerifyCreate(data);
    await settleLoginEnvelope(result, 'verifyOTP');
    return result;
  }, [settleLoginEnvelope]);

  const loginWithPassword = useCallback(async (
    data: PasswordLoginRequest,
  ): Promise<PasswordLoginResponse> => {
    // Errors propagate from the generated transport. Nothing is written to the
    // session on a failure.
    const result = await cfgAccountsTokenCreate(data);
    await settleLoginEnvelope(result, 'loginWithPassword');
    return result;
  }, [settleLoginEnvelope]);

  const logout = useCallback(() => {
    // Best-effort server-side revocation: without blacklisting, a stolen
    // refresh token survives "logout" until it expires. Fire-and-forget —
    // local logout must never block on the network.
    const refresh = auth.getRefreshToken();
    if (refresh) {
      cfgAccountsTokenBlacklistCreate({ refresh }).catch(() => {
        authLogger.warn('Refresh-token blacklist failed (logged out locally anyway)');
      });
    }
    authTrace('accounts.logout');
    auth.clearSession();
    setProfile(undefined);
    setProfileError(null);
    clearProfileCache();
  }, []);

  const value: AccountsContextValue = useMemo(() => ({
    profile,
    isHydrated,
    isLoadingProfile,
    profileError,
    updateProfile,
    partialUpdateProfile,
    uploadAvatar,
    refreshProfile,
    requestOTP,
    verifyOTP,
    loginWithPassword,
    logout,
  }), [
    profile,
    isHydrated,
    isLoadingProfile,
    profileError,
    updateProfile,
    partialUpdateProfile,
    uploadAvatar,
    refreshProfile,
    requestOTP,
    verifyOTP,
    loginWithPassword,
    logout,
  ]);

  return (
    <AccountsContext.Provider value={value}>
      {children}
    </AccountsContext.Provider>
  );
}

export function useAccountsContext(): AccountsContextValue {
  const context = useContext(AccountsContext);
  if (!context) {
    throw new Error('useAccountsContext must be used within AccountsProvider');
  }
  return context;
}
