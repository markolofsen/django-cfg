'use client';

import { useSearchParams } from 'next/navigation';
import React, { memo, useCallback, useEffect, useRef, useState } from 'react';

import {
    beginTwoFactorChallenge, clearOAuthAttempt, isOAuthProviderId, type OAuthFailureCode, useOAuthLogin
} from '@djangocfg/api/auth';

import { useAuthFormContext } from '../../../context';
import { describeOAuthFailure } from '../errors/errorCopy';
import { useOAuthErrorText } from '../errors/useOAuthErrorText';
import { readOAuthCallback, stripOAuthCallbackParams } from './callbackParams';
import { OAuthCallbackOverlay } from './OAuthCallbackOverlay';

export interface OAuthCallbackProps {
  /** `user` is the provider callback's user payload, untyped upstream — narrow it before reading fields. */
  onSuccess?: (user: unknown, isNewUser: boolean, provider: string) => void;
  onError?: (error: string) => void;
  redirectUrl?: string;
}

type CallbackStatus = 'idle' | 'processing' | 'challenge';

/**
 * Finishes a provider sign-in on the page the provider returned to.
 *
 * Mounted by `AuthLayout`; it renders nothing unless the URL carries
 * `?provider=<id>`. It reads the URL once, strips the single-use parameters
 * from the address bar, then either exchanges the code (the stored `state`
 * must match, see `useOAuthLogin`) or hands the failure (Cancel, a provider
 * error, an unknown provider) to the sign-in form as a dismissible notice.
 * The page is never blocked by a failure: the visitor lands on the form.
 *
 * Success hands over to the layout's success screen, which consumes the saved
 * return URL; this component never navigates itself.
 *
 * Memoised: re-renders only when `onSuccess`, `onError`, or `redirectUrl`
 * change. Callbacks are compared by reference; stabilise them with useCallback.
 */
function OAuthCallbackRaw({ onSuccess, onError, redirectUrl }: OAuthCallbackProps) {
  const searchParams = useSearchParams();
  const { setStep, setOAuthNotice } = useAuthFormContext();
  const errorText = useOAuthErrorText();

  const [status, setStatus] = useState<CallbackStatus>('idle');
  const [provider, setProvider] = useState<string | null>(null);

  // One attempt per page load: strict mode runs effects twice, and the
  // stripped URL re-renders this component with no provider left to read.
  const handledRef = useRef(false);

  const fail = useCallback(
    (providerId: string, code: OAuthFailureCode | undefined, message?: string) => {
      // Cancel is not an error: the visitor is simply back at the form.
      if (describeOAuthFailure(code)) setOAuthNotice({ provider: providerId, code });
      setStatus('idle');
      onError?.(errorText(code, message, providerId));
    },
    [errorText, setOAuthNotice, onError],
  );

  const failRef = useRef(fail);
  failRef.current = fail;
  const providerRef = useRef<string | null>(null);

  const { complete } = useOAuthLogin({
    redirectUrl,
    skipRedirect: true, // The success screen navigates.
    onSuccess: (user, isNewUser, providerId) => {
      setStep('success');
      onSuccess?.(user, isNewUser, providerId);
    },
    onError: (message, code) => failRef.current(providerRef.current ?? '', code, message),
    onRequires2FA: (sessionId) => {
      // The dialog needs the page; this overlay would cover it.
      setStatus('challenge');
      beginTwoFactorChallenge({ sessionId });
    },
  });

  useEffect(() => {
    if (handledRef.current) return;
    const intent = readOAuthCallback(searchParams, isOAuthProviderId);
    if (intent.kind === 'none') return;
    handledRef.current = true;

    window.history.replaceState(window.history.state, '', stripOAuthCallbackParams(window.location.href));
    providerRef.current = intent.provider;
    setProvider(intent.provider);

    if (intent.kind === 'failure') {
      // The attempt is over: no exchange will spend the stored state.
      clearOAuthAttempt();
      fail(intent.provider, intent.code, intent.description);
      return;
    }

    setStatus('processing');
    void complete(intent.provider, intent.code, intent.state);
  }, [searchParams, complete, fail]);

  if (status !== 'processing') return null;

  // Success is the layout's success screen (setStep('success')), a failure is
  // the notice on the form; this overlay covers only the wait for the exchange.
  return <OAuthCallbackOverlay provider={provider} />;
}

export const OAuthCallback = memo(OAuthCallbackRaw);
