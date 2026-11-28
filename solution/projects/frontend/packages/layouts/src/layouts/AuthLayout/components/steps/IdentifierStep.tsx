'use client';

import React, { memo, useCallback, useEffect, useMemo, useRef } from 'react';

import { useAppT } from '@djangocfg/i18n';
import { Checkbox, Input } from '@djangocfg/ui-core/components';

import { useAuthLayoutContext } from '../../layoutContext';
import { useAuthFormContext } from '../../context';
import { OAuthSection } from '../oauth';
import {
  AuthButton,
  AuthConsent,
  AuthContainer,
  AuthError,
  AuthHeader,
} from '../shared';

/**
 * IdentifierStep - Apple-style email input step.
 *
 * Clean, minimal design with:
 * - Optional logo, stood down on desktop when the media half carries the brand
 * - Single email input field, with its error directly beneath it
 * - Provider buttons first (only those the server enables), then "or", then
 *   the email path: one tap signs a returning visitor in
 * - Passive consent line under both (continuing = consent; no opt-in checkbox)
 *
 * Memoised: this component has no props; it reads everything from
 * context. The memo wrapper prevents re-renders when the parent
 * (AuthContent) re-renders due to step changes in a sibling branch.
 * Internal context selectors still trigger updates when relevant
 * fields change.
 */
function IdentifierStepRaw() {
  const { hideHeader, hasBrandPanel } = useAuthLayoutContext();

  const {
    identifier,
    isLoading,
    error,
    isRateLimited,
    rateLimitLabel,
    logo,
    termsUrl,
    privacyUrl,
    oauth,
    sourceUrl,
    marketingConsent,
    marketingConsentConfig,
    setIdentifier,
    setMarketingConsent,
    setError,
    handleIdentifierSubmit,
  } = useAuthFormContext();

  // Derived consent values — computed before the JSX return.
  const consentEnabled = Boolean(marketingConsentConfig?.enabled);
  const consentChecked = marketingConsent === true;
  const consentDefaultChecked = marketingConsentConfig?.defaultChecked;

  // Once the user toggles the checkbox, no default may overwrite their choice.
  const consentTouchedRef = useRef(false);

  // Default checked-state resolution: explicit `defaultChecked` (typically the
  // server-decided consent policy) wins; the timezone heuristic is only the
  // fallback while it is undefined (policy loading/unavailable). The policy
  // usually arrives async after mount, so a late explicit default still
  // replaces the fallback — but never a user's own choice.
  useEffect(() => {
    if (!consentEnabled || consentTouchedRef.current) return;
    if (consentDefaultChecked !== undefined) {
      if (marketingConsent !== consentDefaultChecked) setMarketingConsent(consentDefaultChecked);
      return;
    }
    if (marketingConsent !== null) return;
    // Jurisdiction heuristic v1: European timezones default to UNCHECKED
    // (opt-in regimes), everywhere else defaults to checked.
    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone ?? '';
    setMarketingConsent(!timeZone.startsWith('Europe/'));
  }, [consentEnabled, consentDefaultChecked, marketingConsent, setMarketingConsent]);

  // Translations
  const t = useAppT();
  const content = useMemo(() => ({
    title: t('layouts.auth.identifier.title'),
    subtitle: {
      email: t('layouts.auth.identifier.subtitle.email'),
    },
    placeholder: {
      email: t('layouts.auth.identifier.placeholder.email'),
    },
    button: t('layouts.auth.identifier.button'),
  }), [t]);

  const hasOAuth = oauth.providers.length > 0;

  // With buttons above it, the field must not grab focus: on a phone the
  // keyboard would cover them. Without providers the page behaves as it always
  // did, once we know that (the list arrives after mount).
  const emailRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (oauth.isReady && !hasOAuth && document.activeElement === document.body) {
      emailRef.current?.focus();
    }
  }, [oauth.isReady, hasOAuth]);

  // A notice that points at email moves the cursor to the field.
  const focusEmail = useCallback(() => emailRef.current?.focus(), []);

  return (
    <AuthContainer step="identifier">
      {!hideHeader && (
        <AuthHeader
          logo={logo}
          brandElsewhere={hasBrandPanel}
          title={content.title}
          subtitle={content.subtitle.email}
        />
      )}

      <OAuthSection sourceUrl={sourceUrl} disabled={isLoading} onError={setError} onFocusEmail={focusEmail} />

      <form onSubmit={handleIdentifierSubmit} className="auth-form-group">
        <Input
          ref={emailRef}
          type="email"
          name="email"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          placeholder={content.placeholder.email}
          disabled={isLoading}
          required
          autoComplete="email"
          inputMode="email"
          autoCapitalize="off"
          spellCheck={false}
          className="auth-input"
        />

        <AuthError message={error} />

                {consentEnabled && (
          <label className="auth-optin">
            <Checkbox
              checked={consentChecked}
              onCheckedChange={(checked) => {
                consentTouchedRef.current = true;
                setMarketingConsent(checked === true);
              }}
              disabled={isLoading}
              className="auth-optin-checkbox"
            />
            {/* Label copy comes from the consuming app — no product wording here. */}
            <span className="auth-optin-label">
              {marketingConsentConfig?.label}
            </span>
          </label>
        )}

        <AuthButton
          loading={isLoading}
          disabled={!identifier || isRateLimited}
        >
          {isRateLimited ? `${content.button} (${rateLimitLabel})` : content.button}
        </AuthButton>

        {/* Continuing implies consent — passive line, no opt-in checkbox. */}
        <AuthConsent termsUrl={termsUrl} privacyUrl={privacyUrl} />
      </form>

    </AuthContainer>
  );
}

export const IdentifierStep = memo(IdentifierStepRaw);
