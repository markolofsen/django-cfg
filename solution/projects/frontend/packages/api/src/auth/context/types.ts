import React from 'react';

import type { User } from '../../';
import type {
  OTPRequestConsent,
  OTPRequestResult,
  PasswordLoginOptions,
  PasswordLoginResult,
} from '../types';

// User profile type
export type UserProfile = User;

import type { SsoConfig, SsoState } from '../utils/sso';

// Auth configuration
export interface AuthConfig {
  /**
   * Django API origin used by all generated operations and refresh: an absolute URL, or a same-origin prefix such
   * as `/apix`. Applied with `configureApi` during render, so an invalid value is ignored with a warning, and an
   * empty one leaves the choice to `NEXT_PUBLIC_*` (see `runtime/api-origin.ts`).
   */
  apiUrl?: string;
  routes?: {
    auth?: string;
    defaultCallback?: string;
    defaultAuthCallback?: string;
  };
  onLogout?: () => void;
  /**
   * One sign-in host for every subdomain of a domain. Off unless set. `sso: true` derives the host as `auth.<apex of NEXT_PUBLIC_SITE_URL>`; `NEXT_PUBLIC_AUTH_HOST` overrides.
   * Followers redirect to `{host}/auth?next=<url>` and are sent back after sign-in; the host renders the form.
   * Ignored (with one console line) on a host outside the apex, e.g. localhost.
   */
  sso?: SsoConfig | true;
}

/**
 * AuthConfig.routes resolved against the framework conventions — no field is
 * optional here. This is what components consume (via `useAuth().routes`)
 * instead of defaulting to route constants themselves.
 */
export interface ResolvedAuthRoutes {
  auth: string;
  defaultCallback: string;
  defaultAuthCallback: string;
}

// Auth context interface
export interface AuthContextType {
  user: UserProfile | null;
  isLoading: boolean;
  /** The one linear auth state: 'resolving' until the client has read the session and its profile, then 'authenticated' or 'anonymous'. */
  status: 'resolving' | 'authenticated' | 'anonymous';
  /**
   * `false` on the server and during the hydration render, `true` from the first commit after mount.
   * Until then `user` is `null` and `isAdminUser` `false` even for a signed-in visitor (the stored
   * profile is applied after mount), so the client's first render matches the server HTML.
   * Gate client-only UI on it when "guest" and "not known yet" must look different.
   */
  isHydrated: boolean;
  isAuthenticated: boolean;
  isAdminUser: boolean;
  /** Resolved route conventions (config override or framework default). */
  routes: ResolvedAuthRoutes;
  /** Single sign-in host state (`enabled: false` when not configured or on localhost). Settles after mount. */
  sso?: SsoState;
  loadCurrentProfile: (callerId?: string) => Promise<void>;
  checkAuthAndRedirect: () => Promise<void>;

  // Token Methods
  getToken: () => string | null;
  getRefreshToken: () => string | null;

  // Email Methods
  getSavedEmail: () => string | null;
  saveEmail: (email: string) => void;
  clearSavedEmail: () => void;

  // OTP Methods - email only
  requestOTP: (identifier: string, sourceUrl?: string, consent?: OTPRequestConsent) => Promise<OTPRequestResult>;
  verifyOTP: (identifier: string, otpCode: string, sourceUrl?: string, redirectUrl?: string, skipRedirect?: boolean) => Promise<{
    success: boolean;
    message: string;
    user?: UserProfile;
    requires_2fa?: boolean;
    session_id?: string | null;
    should_prompt_2fa?: boolean;
  }>;
  // Password Method - same envelope and the same session owner as verifyOTP;
  // `requires_2fa` hands off to the existing 2FA flow with a session id.
  login: (email: string, password: string, options?: PasswordLoginOptions) => Promise<PasswordLoginResult>;

  refreshToken: () => Promise<{ success: boolean; message: string }>;
  logout: () => void;

  // Redirect URL Methods - for saving URL before auth redirect
  saveRedirectUrl: (url: string) => void;
  getRedirectUrl: () => string;
  clearRedirectUrl: () => void;
  hasRedirectUrl: () => boolean;

  // Profile Management Methods
  updateProfile: (data: { first_name?: string; last_name?: string; username?: string }) => Promise<UserProfile>;
  uploadAvatar: (avatar: File | Blob) => Promise<UserProfile>;
}

// Provider props
export interface AuthProviderProps {
  children: React.ReactNode;
  config?: AuthConfig;
  /** Set false to skip all auth logic and render children directly. */
  enabled?: boolean;
}
