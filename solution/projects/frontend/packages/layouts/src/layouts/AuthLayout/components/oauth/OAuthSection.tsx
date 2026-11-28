'use client';

import React, { memo, useCallback, useEffect } from 'react';

import { isOAuthProviderId } from '@djangocfg/api/auth';

import { useAuthFormContext } from '../../context';
import { AuthDivider } from '../shared/AuthDivider';
import { OAuthButtons } from './buttons/OAuthButtons';
import { describeOAuthFailure } from './errors/errorCopy';
import { OAuthNotice } from './notice/OAuthNotice';

export interface OAuthSectionProps {
  sourceUrl?: string;
  /** Disables every provider button, e.g. while the email form is submitting. */
  disabled?: boolean;
  /** A provider sign-in that could not start: the sentence to show under the form field. */
  onError?: (message: string) => void;
  /** Called when a notice appears whose only way forward is email: put the cursor in the email field. */
  onFocusEmail: () => void;
}

/**
 * Everything provider sign-in puts above the email form, in order: the failure
 * notice (if the last round trip failed), the buttons, the "or" divider.
 *
 * Reads the server's provider list and the notice from the form context. While
 * the list loads it holds the room the buttons will take, so the email field
 * does not jump; with no providers it renders nothing.
 */
function OAuthSectionRaw({ sourceUrl, disabled, onError, onFocusEmail }: OAuthSectionProps) {
  const { oauth, oauthNotice, setOAuthNotice } = useAuthFormContext();

  const dismissNotice = useCallback(() => setOAuthNotice(null), [setOAuthNotice]);

  // The email field is right below: when the notice says email is the way
  // forward (nothing to retry), the cursor goes there instead of a button.
  useEffect(() => {
    if (!oauthNotice) return;
    const action = describeOAuthFailure(oauthNotice.code)?.action;
    // A retry for a provider this client has no button for is email too.
    if (action === 'email' || (action === 'retry' && !isOAuthProviderId(oauthNotice.provider))) onFocusEmail();
  }, [oauthNotice, onFocusEmail]);

  return (
    <>
      {oauthNotice && <OAuthNotice failure={oauthNotice} sourceUrl={sourceUrl} onDismiss={dismissNotice} />}

      {oauth.providers.length > 0 && (
        <>
          <OAuthButtons providers={oauth.providers} sourceUrl={sourceUrl} disabled={disabled} onError={onError} />
          <AuthDivider />
        </>
      )}
      {!oauth.isReady && (
        <div className="auth-oauth-reserve" aria-hidden="true">
          <span className="auth-oauth-skeleton" />
          <span className="auth-oauth-skeleton" />
        </div>
      )}
    </>
  );
}

export const OAuthSection = memo(OAuthSectionRaw);
