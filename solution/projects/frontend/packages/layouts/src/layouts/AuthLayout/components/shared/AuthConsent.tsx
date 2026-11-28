'use client';

import React, { memo } from 'react';

export interface AuthConsentProps {
  termsUrl?: string;
  privacyUrl?: string;
  className?: string;
}

/**
 * AuthConsent — passive consent line shown under the submit button.
 *
 * Replaces the old opt-in checkbox: continuing *is* the consent, so this only
 * informs and links out. Shared by both the Centered and Split forms.
 *
 * The legal copy is intentionally hardcoded English and NOT translated:
 * "Terms"/"Privacy Policy" are proper names of legal documents that stay in
 * English across locales, and the one-line "By continuing…" boilerplate isn't
 * worth a 17-locale i18n key. Links always open in a new tab.
 *
 * Renders nothing when neither legal URL is provided (no empty line).
 *
 * Memoised: re-renders only when the URL props or className change.
 */
function AuthConsentRaw({ termsUrl, privacyUrl, className = '' }: AuthConsentProps) {
  if (!termsUrl && !privacyUrl) return null;

  const link = (href: string, label: string) => (
    <a href={href} target="_blank" rel="noopener noreferrer" className="auth-consent-link">
      {label}
    </a>
  );

  return (
    <p className={`auth-consent ${className}`}>
      By continuing you agree to the{' '}
      {termsUrl && link(termsUrl, 'Terms')}
      {termsUrl && privacyUrl && ' and '}
      {privacyUrl && link(privacyUrl, 'Privacy Policy')}
      .
    </p>
  );
}

export const AuthConsent = memo(AuthConsentRaw);
