'use client';

import React, { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { useAppT } from '@djangocfg/i18n';

import { AUTH } from '../../constants';
import { useAuthFormContext } from '../../context';
import {
  AuthButton,
  AuthContainer,
  AuthError,
  AuthHeader,
  AuthLink,
  AuthOTPInput,
  WebmailIcon,
} from '../shared';

type SubmitState = 'idle' | 'submitting';

/**
 * OTPStep - Apple-style OTP verification.
 *
 * Minimal design focused on the OTP input:
 * - Clear title
 * - Masked identifier for privacy
 * - Large OTP input
 * - Text links for actions
 *
 * Memoised: no props; reads from context. Prevents re-renders when
 * AuthContent switches steps or when sibling branches update.
 */
function OTPStepRaw() {
  const {
    identifier,
    otp,
    isLoading,
    error,
    isRateLimited,
    rateLimitLabel,
    resendSeconds,
    resendLabel,
    webmail,
    setOtp,
    handleOTPSubmit,
    handleResendOTP,
    handleBackToIdentifier,
    isAutoSubmittingFromUrl,
  } = useAuthFormContext();

  const [submitState, setSubmitState] = useState<SubmitState>('idle');

  // Translations
  const t = useAppT();
  const content = useMemo(() => ({
    title: t('layouts.auth.otp.title'),
    subtitle: t('layouts.auth.otp.subtitle'),
    button: t('layouts.auth.otp.button'),
    resend: t('layouts.auth.otp.resend'),
    changeEmail: t('layouts.auth.otp.changeEmail'),
  }), [t]);

  // "Open Gmail / Outlook / …" — jumps straight to a search for our email.
  const openMailboxLabel = useMemo(
    () => (webmail ? t('layouts.auth.otp.openMailbox', { provider: webmail.provider_name }) : ''),
    [t, webmail]
  );

  const handleOpenMailbox = useCallback(() => {
    if (!webmail) return;
    window.open(webmail.url, '_blank', 'noopener,noreferrer');
  }, [webmail]);

  // Mask identifier for privacy
  const maskedIdentifier = useMemo(() => {
    const [local, domain] = identifier.split('@');
    if (!local || !domain) return identifier;
    return `${local[0]}${'*'.repeat(Math.min(local.length - 1, 5))}@${domain}`;
  }, [identifier]);

  const waitLabel = isRateLimited ? rateLimitLabel : resendLabel;
  const resendLabelText = waitLabel ? `${content.resend} (${waitLabel})` : content.resend;

  const autoSubmitTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(
    () => () => {
      if (autoSubmitTimerRef.current) clearTimeout(autoSubmitTimerRef.current);
    },
    []
  );

  // Auto-submit on complete (state machine approach)
  const handleOTPComplete = useCallback(
    async (completedValue: string) => {
      if (submitState !== 'idle' || isLoading || isAutoSubmittingFromUrl.current) return;
      if (completedValue.length !== AUTH.EMAIL_OTP_LENGTH) return;

      setSubmitState('submitting');
      const fakeEvent = { preventDefault: () => {} } as React.FormEvent;

      // Tracked so leaving the step cancels it. This component unmounts when
      // the user goes back to the identifier, and an uncancelled timer would
      // submit the code they just abandoned.
      autoSubmitTimerRef.current = setTimeout(async () => {
        autoSubmitTimerRef.current = null;
        try {
          await handleOTPSubmit(fakeEvent);
        } finally {
          setSubmitState('idle');
        }
      }, AUTH.AUTO_SUBMIT_DELAY);
    },
    [handleOTPSubmit, isLoading, isAutoSubmittingFromUrl, submitState]
  );

  return (
    <AuthContainer step="otp">
      <AuthHeader
        title={content.title}
        subtitle={content.subtitle}
        identifier={maskedIdentifier}
      />

      <form onSubmit={handleOTPSubmit} className="auth-form-group">
        <AuthOTPInput
          value={otp}
          onChange={setOtp}
          onComplete={handleOTPComplete}
          disabled={isLoading}
          length={AUTH.EMAIL_OTP_LENGTH}
          size="lg"
        />

        {webmail && (
          <AuthButton
            type="button"
            variant="secondary"
            onClick={handleOpenMailbox}
            className="auth-webmail-button"
          >
            <WebmailIcon provider={webmail.provider} />
            {openMailboxLabel}
          </AuthButton>
        )}

        <AuthError message={error} />

        <AuthButton loading={isLoading} disabled={otp.length < AUTH.EMAIL_OTP_LENGTH}>
          {content.button}
        </AuthButton>

        <div className="auth-actions">
          <AuthLink
            onClick={handleResendOTP}
            disabled={isLoading || isRateLimited || resendSeconds > 0}
          >
            {resendLabelText}
          </AuthLink>
          <AuthLink onClick={handleBackToIdentifier} disabled={isLoading}>
            {content.changeEmail}
          </AuthLink>
        </div>
      </form>
    </AuthContainer>
  );
}

export const OTPStep = memo(OTPStepRaw);
