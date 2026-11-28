'use client';

import React, { memo, useCallback } from 'react';

import { isOAuthProviderId, useOAuthLogin } from '@djangocfg/api/auth';

import type { OAuthFailure } from '../../../types';
import { OAuthNoticeView } from './OAuthNoticeView';

export interface OAuthNoticeProps {
  failure: OAuthFailure;
  sourceUrl?: string;
  /** Closes the notice (button or Escape). */
  onDismiss: () => void;
}

/** The failure notice with its retry wired to `useOAuthLogin`. */
function OAuthNoticeRaw({ failure, sourceUrl, onDismiss }: OAuthNoticeProps) {
  const { start, isLoading } = useOAuthLogin({ sourceUrl });
  const { provider } = failure;

  const handleRetry = useCallback(() => {
    if (isOAuthProviderId(provider)) void start(provider);
  }, [start, provider]);

  return (
    <OAuthNoticeView
      provider={provider}
      code={failure.code}
      origin={typeof window === 'undefined' ? undefined : window.location.origin}
      onRetry={isOAuthProviderId(provider) ? handleRetry : undefined}
      retrying={isLoading}
      onDismiss={onDismiss}
    />
  );
}

export const OAuthNotice = memo(OAuthNoticeRaw);
