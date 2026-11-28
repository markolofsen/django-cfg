'use client';

import React, { memo, useCallback, useRef } from 'react';

import { type OAuthProviderId, useOAuthLogin } from '@djangocfg/api/auth';

import { useOAuthErrorText } from '../errors/useOAuthErrorText';
import { OAuthButtonList } from './OAuthButtonList';

export interface OAuthButtonsProps {
  providers: readonly OAuthProviderId[];
  sourceUrl?: string;
  /** Disables every button, e.g. while the email form is submitting. */
  disabled?: boolean;
  /** Receives the visitor-facing sentence for a sign-in that could not start. */
  onError?: (message: string) => void;
}

/**
 * The provider buttons wired to `useOAuthLogin`: a click starts that
 * provider's flow, progress shows on the one clicked and the rest are disabled
 * until the page leaves or the start fails.
 */
function OAuthButtonsRaw({ providers, sourceUrl, disabled, onError }: OAuthButtonsProps) {
  const errorText = useOAuthErrorText();
  const startedRef = useRef<OAuthProviderId | null>(null);

  const { start, loadingProvider } = useOAuthLogin({
    sourceUrl,
    onError: (message, code) => onError?.(errorText(code, message, startedRef.current)),
  });

  const handleSelect = useCallback(
    (id: OAuthProviderId) => {
      startedRef.current = id;
      void start(id);
    },
    [start],
  );

  return <OAuthButtonList providers={providers} loadingProvider={loadingProvider} disabled={disabled} onSelect={handleSelect} />;
}

export const OAuthButtons = memo(OAuthButtonsRaw);
