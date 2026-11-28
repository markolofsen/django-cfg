'use client';

import React, { useMemo, useRef, useState } from 'react';

import {
  type AuthStep,
  type OAuthProviderId,
  useOAuthProviders,
  type WebmailLink,
} from '@djangocfg/api/auth';

import { AuthFormContext } from '../layouts/AuthLayout/context';
import { resolveOAuthProviders } from '../layouts/AuthLayout/components/oauth/providers/resolveProviders';
import type { AuthFormContextType, AuthLayoutConfig, OAuthFailure } from '../layouts/AuthLayout/types';

// Storybook-only provider. Reproduces the AuthFormContext shape with
// in-memory state and no-op async handlers, so step components and the
// full AuthLayout can be exercised without hitting @djangocfg/api/auth.

export interface MockAuthFormProviderProps extends Partial<AuthLayoutConfig> {
  children: React.ReactNode;

  // Initial state — every field has a sensible default. Override per story.
  step?: AuthStep;
  identifier?: string;
  otp?: string;
  isLoading?: boolean;
  acceptedTerms?: boolean;
  error?: string;
  rateLimitSeconds?: number;
  resendSeconds?: number;
  webmail?: WebmailLink | null;

  /** Simulates the server's list still loading: the provider block shows its reserved space. */
  oauthPending?: boolean;

  /**
   * Read the provider list through the real `useOAuthProviders` (`GET /oauth/providers/`),
   * as `AuthLayout` does; `oauthProviders` then only narrows it. Pair it with
   * `oauthApiMock` so the request is answered. Off: `oauthProviders` is the list.
   */
  oauthFromServer?: boolean;
}

const NO_PROVIDERS: OAuthProviderId[] = [];

function formatRateLimit(seconds: number): string {
  if (seconds <= 0) return '';
  if (seconds >= 60) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  }
  return `${seconds}s`;
}

function WithServerOAuth({ oauthProviders, oauthFromServer: _, ...rest }: MockAuthFormProviderProps) {
  const { providers, isReady } = useOAuthProviders();
  const ids = useMemo(() => providers.map((p) => p.id), [providers]);
  const resolved = useMemo(() => resolveOAuthProviders(ids, oauthProviders), [ids, oauthProviders]);
  return <MockAuthFormProviderBase {...rest} oauthProviders={resolved} oauthPending={!isReady} />;
}

export const MockAuthFormProvider: React.FC<MockAuthFormProviderProps> = (props) =>
  props.oauthFromServer ? (
    <WithServerOAuth {...props} />
  ) : (
    <MockAuthFormProviderBase {...props} />
  );

const MockAuthFormProviderBase: React.FC<MockAuthFormProviderProps> = ({
  children,

  // Layout config
  sourceUrl = 'https://example.com',
  supportUrl,
  termsUrl,
  privacyUrl,
  oauthProviders = NO_PROVIDERS,
  logo,
  redirectUrl = '/dashboard',
  marketingConsent: marketingConsentConfig,

  // Initial state
  step: initialStep = 'identifier',
  identifier: initialIdentifier = '',
  otp: initialOtp = '',
  isLoading: initialLoading = false,
  acceptedTerms: initialAcceptedTerms = false,
  error: initialError = '',
  rateLimitSeconds: initialRateLimitSeconds = 0,
  resendSeconds: initialResendSeconds = 0,
  webmail: initialWebmail = null,
  oauthPending = false,
}) => {
  const [step, setStep] = useState<AuthStep>(initialStep);
  const [identifier, setIdentifier] = useState(initialIdentifier);
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState(initialOtp);
  const [isLoading, setIsLoading] = useState(initialLoading);
  const [acceptedTerms, setAcceptedTerms] = useState(initialAcceptedTerms);
  const [marketingConsent, setMarketingConsent] = useState<boolean | null>(null);
  const [error, setError] = useState(initialError);
  const [rateLimitSeconds, setRateLimitSeconds] = useState(initialRateLimitSeconds);
  const [resendSeconds, setResendSeconds] = useState(initialResendSeconds);
  const [webmail, setWebmail] = useState<WebmailLink | null>(initialWebmail);

  const oauth = useMemo(
    () => ({ providers: oauthProviders, isReady: !oauthPending }),
    [oauthProviders, oauthPending],
  );

  const isAutoSubmittingFromUrl = useRef(false);
  const [oauthNotice, setOAuthNotice] = useState<OAuthFailure | null>(null);

  const value: AuthFormContextType = useMemo(() => {
    const stop = (e: React.FormEvent) => {
      e.preventDefault?.();
    };

    return {
      // State
      identifier,
      password,
      otp,
      isLoading,
      acceptedTerms,
      marketingConsent,
      step,
      error,
      rateLimitSeconds,
      isRateLimited: rateLimitSeconds > 0,
      rateLimitLabel: formatRateLimit(rateLimitSeconds),
      resendSeconds,
      resendLabel: formatRateLimit(resendSeconds),
      webmail,

      // State handlers
      setIdentifier,
      setPassword,
      setOtp,
      setAcceptedTerms,
      setMarketingConsent,
      setError,
      clearError: () => setError(''),
      setStep,
      setIsLoading,
      startRateLimitCountdown: (seconds: number) => setRateLimitSeconds(seconds),
      startResendCountdown: (seconds: number) => setResendSeconds(seconds),
      setWebmail,

      // Submit handlers — all no-op (preventDefault only) so the visible
      // step never changes from under the storyteller. To preview a
      // different step, render a new story with `step="..."`.
      handleIdentifierSubmit: async (e) => stop(e),
      handlePasswordSubmit: async (e) => stop(e),
      handleOTPSubmit: async (e) => stop(e),
      handleResendOTP: async () => {},
      handleBackToIdentifier: () => setStep('identifier'),
      forceOTPStep: () => setStep('otp'),

      // Validation — accept anything that looks email-ish or 10+ digits.
      validateIdentifier: (id: string) =>
        /.+@.+\..+/.test(id) || /^\+?\d{10,}$/.test(id),

      // Auto-submit ref
      isAutoSubmittingFromUrl,

      // Layout config
      sourceUrl,
      supportUrl,
      termsUrl,
      privacyUrl,
      oauth,
      oauthNotice,
      setOAuthNotice,
      logo,
      redirectUrl,
      marketingConsentConfig,
    };
  }, [
    identifier,
    otp,
    isLoading,
    acceptedTerms,
    marketingConsent,
    step,
    error,
    rateLimitSeconds,
    resendSeconds,
    webmail,
    sourceUrl,
    supportUrl,
    termsUrl,
    privacyUrl,
    oauth,
    oauthNotice,
    logo,
    redirectUrl,
    marketingConsentConfig,
  ]);

  return <AuthFormContext.Provider value={value}>{children}</AuthFormContext.Provider>;
};
