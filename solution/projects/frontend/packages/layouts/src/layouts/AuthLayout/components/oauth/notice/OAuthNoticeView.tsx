'use client';

import { Info, X } from 'lucide-react';
import React, { memo, useEffect } from 'react';

import type { OAuthFailureCode } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';
import { Button } from '@djangocfg/ui-core/components';

import { describeOAuthFailure } from '../errors/errorCopy';
import { providerName } from '../providers/registry';

export interface OAuthNoticeViewProps {
  /** Provider id as it came back in the URL. */
  provider: string;
  code?: OAuthFailureCode;
  /** The page origin, shown in the developer hint for `origin_not_allowed`. */
  origin?: string;
  /** Runs the provider again. Absent when this client has no button for the provider: the notice then offers no retry. */
  onRetry?: () => void;
  retrying?: boolean;
  /** Closes the notice (button or Escape). */
  onDismiss: () => void;
}

/**
 * What the sign-in form says after a provider round trip failed: one calm
 * sentence, at most one retry, and a way to close it. Not a dialog: the form
 * underneath stays usable and focus stays where it was. The email field is
 * already on the page, so the notice never offers a button for it.
 *
 * One fixed layout for every code: icon | text | close, the close button
 * centred on the first line. `role="status"` (polite): the visitor did nothing
 * wrong, so it informs without interrupting. Renders nothing for a cancelled
 * sign-in.
 */
function OAuthNoticeViewRaw({ provider, code, origin, onRetry, retrying = false, onDismiss }: OAuthNoticeViewProps) {
  const t = useAppT();
  const copy = describeOAuthFailure(code);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onDismiss();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [onDismiss]);

  if (!copy) return null;

  const name = providerName(provider);
  // A retry for a provider this client has no button for would go nowhere.
  const canRetry = copy.action === 'retry' && !!onRetry;

  return (
    <div role="status" className="auth-oauth-notice">
      <Info className="auth-oauth-notice-icon" aria-hidden="true" />
      <div className="auth-oauth-notice-text">
        {copy.titleKey && <p className="auth-oauth-notice-title">{t(copy.titleKey)}</p>}
        <p className="auth-oauth-notice-body">{t(copy.bodyKey, { provider: name })}</p>
        {copy.developerHintKey && origin && (
          <p className="auth-oauth-hint">{t(copy.developerHintKey, { origin, id: provider })}</p>
        )}
        {canRetry && (
          <Button type="button" variant="outline" size="sm" className="mt-3" disabled={retrying} onClick={onRetry}>
            {t('layouts.auth.oauth.notice.retry', { provider: name })}
          </Button>
        )}
      </div>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="auth-oauth-notice-close"
        aria-label={t('layouts.auth.oauth.notice.dismiss')}
        onClick={onDismiss}
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </Button>
    </div>
  );
}

export const OAuthNoticeView = memo(OAuthNoticeViewRaw);
