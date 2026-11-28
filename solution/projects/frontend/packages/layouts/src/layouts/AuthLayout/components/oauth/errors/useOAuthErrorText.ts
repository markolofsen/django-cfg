'use client';

import { useCallback } from 'react';

import type { OAuthFailureCode } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';

import { providerName } from '../providers/registry';
import { OAUTH_ERROR_KEYS, oauthErrorKey } from './errorCopy';

/**
 * The visitor-facing sentence for a failure: the translated copy of its code
 * (`{provider}` filled with the brand name), else the text the hook carried
 * (server prose), else the generic sentence.
 */
export const useOAuthErrorText = () => {
  const t = useAppT();
  return useCallback(
    (code?: OAuthFailureCode | null, fallback?: string | null, provider?: string | null): string => {
      if (code) return t(oauthErrorKey(code), { provider: providerName(provider ?? '') });
      return fallback || t(OAUTH_ERROR_KEYS.generic);
    },
    [t],
  );
};
