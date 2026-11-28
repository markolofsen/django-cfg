/**
 * Auth Form Types
 *
 * Single source of truth for auth form state and handlers.
 * Used by both @djangocfg/api/auth hooks and @djangocfg/layouts/AuthLayout.
 */

import type { MutableRefObject } from 'react';

import type { User, WebmailLink } from '../../_api/models';

export type { WebmailLink };

// ─────────────────────────────────────────────────────────────────────────────
// Step Types
// ─────────────────────────────────────────────────────────────────────────────

export type AuthStep = 'identifier' | 'otp' | 'success';

// ─────────────────────────────────────────────────────────────────────────────
// OTP Result Types
// ─────────────────────────────────────────────────────────────────────────────

export interface OTPRequestResult {
  success: boolean;
  message: string;
  statusCode?: number;
  retryAfter?: number;
  /** Webmail deep-link for the recipient's provider, or null if unknown. */
  webmail?: WebmailLink | null;
  /** Seconds until a new code may be requested. */
  resendIn?: number;
}

/**
 * Marketing-consent payload attached to an OTP request when the consuming
 * app enables the opt-in checkbox. Absent ⇒ the request body is unchanged.
 */
export interface OTPRequestConsent {
  /** Checkbox value at submit time. */
  marketingConsent: boolean;
  /** Version tag of the disclosure copy the user saw (e.g. "product-updates-reg-v1"). */
  disclosureVersion: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Password Login Types
// ─────────────────────────────────────────────────────────────────────────────

export interface PasswordLoginOptions {
  /** URL to redirect to after a successful login (ignored when skipRedirect). */
  redirectUrl?: string;
  /** Caller owns ALL navigation for this login, including the 2FA continuation. */
  skipRedirect?: boolean;
}

/**
 * Result of a password login.
 *
 * Deliberately the same shape as the verifyOTP result plus the failure codes
 * the password endpoint adds: a sign-in form branches on `requires_2fa` the
 * same way whichever credential it collected.
 */
export interface PasswordLoginResult {
  success: boolean;
  message: string;
  user?: User;
  requires_2fa?: boolean;
  session_id?: string | null;
  should_prompt_2fa?: boolean;
  /** HTTP status of a failure — 401 for bad credentials, 429 when throttled. */
  statusCode?: number;
  /** Machine-readable failure code, e.g. `invalid_credentials`, `locked_out`. */
  errorCode?: string;
  /** Seconds until a throttled caller may retry (429 only). */
  retryAfter?: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Form State
// ─────────────────────────────────────────────────────────────────────────────

export interface AuthFormState {
  /** Email address */
  identifier: string;
  /** OTP code input */
  otp: string;
  /** Password input (password sign-in; empty for the OTP-only flow) */
  password: string;
  /** Loading state */
  isLoading: boolean;
  /** Terms acceptance state */
  acceptedTerms: boolean;
  /**
   * Marketing-consent checkbox state. `null` = feature not initialised (no
   * checkbox rendered, or default not yet resolved); the layout owns the
   * jurisdiction-aware default on mount.
   */
  marketingConsent: boolean | null;
  /** Current form step */
  step: AuthStep;
  /** Error message */
  error: string;
  /** Seconds remaining until rate limit lifts (0 = not rate limited) */
  rateLimitSeconds: number;
  /** True when rateLimitSeconds > 0 — submit should be disabled */
  isRateLimited: boolean;
  /** Formatted countdown label, e.g. "19:00" or "42s" */
  rateLimitLabel: string;
  /** Seconds until another code may be requested (0 = may resend now) */
  resendSeconds: number;
  /** Formatted resend countdown, e.g. "28s" */
  resendLabel: string;
  /** Webmail deep-link for the current identifier's provider (null = no button). */
  webmail: WebmailLink | null;
}

// ─────────────────────────────────────────────────────────────────────────────
// Form Handlers
// ─────────────────────────────────────────────────────────────────────────────

export interface AuthFormStateHandlers {
  setIdentifier: (identifier: string) => void;
  setOtp: (otp: string) => void;
  setPassword: (password: string) => void;
  setAcceptedTerms: (accepted: boolean) => void;
  setMarketingConsent: (consent: boolean | null) => void;
  setError: (error: string) => void;
  clearError: () => void;
  setStep: (step: AuthStep) => void;
  setIsLoading: (loading: boolean) => void;
  /** Start a countdown timer that disables submit for `seconds` seconds */
  startRateLimitCountdown: (seconds: number) => void;
  /** Start the countdown before another code may be requested */
  startResendCountdown: (seconds: number) => void;
  /** Set (or clear) the webmail deep-link for the current identifier */
  setWebmail: (webmail: WebmailLink | null) => void;
}

export interface AuthFormSubmitHandlers {
  handleIdentifierSubmit: (e: React.FormEvent) => Promise<void>;
  handleOTPSubmit: (e: React.FormEvent) => Promise<void>;
  /** Submit email + password against the password grant */
  handlePasswordSubmit: (e: React.FormEvent) => Promise<void>;
  handleResendOTP: () => Promise<void>;
  handleBackToIdentifier: () => void;
  forceOTPStep: () => void;
}

// ─────────────────────────────────────────────────────────────────────────────
// Validation
// ─────────────────────────────────────────────────────────────────────────────

export interface AuthFormValidation {
  /** Validate identifier format */
  validateIdentifier: (identifier: string) => boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Auto-submit (for URL-based OTP)
// ─────────────────────────────────────────────────────────────────────────────

export interface AuthFormAutoSubmit {
  /** Ref to track if auto-submit from URL is in progress */
  isAutoSubmittingFromUrl: MutableRefObject<boolean>;
}

// ─────────────────────────────────────────────────────────────────────────────
// Combined Form Interface
// ─────────────────────────────────────────────────────────────────────────────

export interface AuthFormReturn extends
  AuthFormState,
  AuthFormStateHandlers,
  AuthFormSubmitHandlers,
  AuthFormValidation,
  AuthFormAutoSubmit {}

// ─────────────────────────────────────────────────────────────────────────────
// Hook Options
// ─────────────────────────────────────────────────────────────────────────────

export interface UseAuthFormOptions {
  /** Callback when identifier step succeeds */
  onIdentifierSuccess?: (identifier: string) => void;
  /** Callback when OTP verification succeeds */
  onOTPSuccess?: () => void;
  /** Callback on any error */
  onError?: (message: string) => void;
  /** Source URL for tracking */
  sourceUrl: string;
  /** URL to redirect after successful OTP verification */
  redirectUrl?: string;
  /** If true, user must accept terms before submitting. Default: false */
  requireTermsAcceptance?: boolean;
  /**
   * Enables the marketing-consent opt-in: when set, the checkbox value +
   * this disclosure version are sent with the OTP request. Absent ⇒ the
   * request body is unchanged (backward compatible).
   */
  marketingConsent?: {
    /** Version tag of the disclosure copy shown next to the checkbox. */
    disclosureVersion: string;
  };
  /** Path to auth page for auto-OTP detection. Default: '/auth' */
  authPath?: string;
}
