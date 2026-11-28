'use client';

import React, { createContext, useContext, useMemo, useState } from 'react';

import { useAuthForm, useOAuthProviders } from '@djangocfg/api/auth';

import { resolveOAuthProviders } from './components/oauth/providers/resolveProviders';
import type { AuthFormContextType, AuthLayoutProps, OAuthFailure } from './types';

// Exported so test/mock providers (storybook) can supply their own value
// without re-implementing AuthFormProvider end-to-end.
export const AuthFormContext = createContext<AuthFormContextType | undefined>(undefined);

/**
 * AuthFormProvider — wraps useAuthForm and merges UI config into context.
 *
 * The context value is memoised so that object reference churn from the
 * hook does not re-render the entire auth subtree when only internal
 * form state (e.g. `isLoading`) changes. Consumers that select specific
 * fields via useAuthFormContext will still re-render as expected.
 */
export const AuthFormProvider: React.FC<AuthLayoutProps> = ({
  children,
  sourceUrl: sourceUrlProp,
  supportUrl,
  termsUrl,
  privacyUrl,
  oauthProviders,
  logo,
  redirectUrl,
  marketingConsent,
  onIdentifierSuccess,
  onOTPSuccess,
  onError,
}) => {
  const sourceUrl = sourceUrlProp || (typeof window !== 'undefined' ? window.location.origin : '');

  // Require terms acceptance only if terms or privacy URL is provided
  const requireTermsAcceptance = Boolean(termsUrl || privacyUrl);

  // The server's provider list, narrowed by the optional `oauthProviders` prop.
  const { providers: serverProviders, isReady: oauthReady } = useOAuthProviders();
  const oauth = useMemo(
    () => ({
      providers: resolveOAuthProviders(serverProviders.map((p) => p.id), oauthProviders),
      isReady: oauthReady,
    }),
    [serverProviders, oauthProviders, oauthReady],
  );

  const [oauthNotice, setOAuthNotice] = useState<OAuthFailure | null>(null);

  // Use the auth form hook

  const authForm = useAuthForm({
    onIdentifierSuccess,
    onOTPSuccess,
    onError,
    sourceUrl,
    redirectUrl,
    requireTermsAcceptance,
    // Presence of this option is what makes the OTP request carry consent fields.
    marketingConsent: marketingConsent?.enabled
      ? { disclosureVersion: marketingConsent.disclosureVersion }
      : undefined,
  });

  const value: AuthFormContextType = useMemo(
    () => ({
      ...authForm,
      // UI-specific configuration
      sourceUrl,
      supportUrl,
      termsUrl,
      privacyUrl,
      oauth,
      oauthNotice,
      setOAuthNotice,
      logo,
      redirectUrl,
      // Renamed: `marketingConsent` (the name) is the checkbox STATE from the form hook.
      marketingConsentConfig: marketingConsent,
    }),
    [
      authForm,
      sourceUrl,
      supportUrl,
      termsUrl,
      privacyUrl,
      oauth,
      oauthNotice,
      logo,
      redirectUrl,
      marketingConsent,
    ]
  );

  return <AuthFormContext.Provider value={value}>{children}</AuthFormContext.Provider>;
};

export const useAuthFormContext = (): AuthFormContextType => {
  const context = useContext(AuthFormContext);
  if (context === undefined) {
    throw new Error('useAuthFormContext must be used within an AuthFormProvider');
  }
  return context;
};
