'use client';

import React, { memo } from 'react';

import type { OAuthProviderId } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';

import { OAUTH_PROVIDERS } from '../providers/registry';
import { OAuthProviderButton } from './OAuthProviderButton';

export interface OAuthButtonListProps {
  providers: readonly OAuthProviderId[];
  /** The provider whose flow is in flight: it shows progress, the others are disabled. */
  loadingProvider?: OAuthProviderId | null;
  /** Disables every button, e.g. while the email form is submitting. */
  disabled?: boolean;
  onSelect: (provider: OAuthProviderId) => void;
}

/**
 * The provider buttons as a labelled group, one per provider, stacked at full
 * width (a column holds at 320px and in long translations). Stateless: the
 * flow lives in `OAuthButtons`, which keeps this list easy to render in any state.
 */
function OAuthButtonListRaw({ providers, loadingProvider = null, disabled = false, onSelect }: OAuthButtonListProps) {
  const t = useAppT();
  const busy = loadingProvider !== null;

  return (
    <div className="auth-oauth" role="group" aria-label={t('layouts.auth.identifier.oauth.groupLabel')}>
      {providers.map((id) => {
        const { name, Icon } = OAUTH_PROVIDERS[id];
        return (
          <OAuthProviderButton
            key={id}
            Icon={Icon}
            label={t('layouts.auth.identifier.oauth.continueWith', { provider: name })}
            data-provider={id}
            loading={loadingProvider === id}
            disabled={disabled || (busy && loadingProvider !== id)}
            onClick={() => onSelect(id)}
          />
        );
      })}
    </div>
  );
}

export const OAuthButtonList = memo(OAuthButtonListRaw);
