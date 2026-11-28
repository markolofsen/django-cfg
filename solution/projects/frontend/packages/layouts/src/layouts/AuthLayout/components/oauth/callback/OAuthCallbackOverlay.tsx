'use client';

import { Loader2 } from 'lucide-react';
import React, { memo } from 'react';

import { useAppT } from '@djangocfg/i18n';
import { Card, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui-core/components';

import { providerName } from '../providers/registry';

export interface OAuthCallbackOverlayProps {
  /** Provider id as it came back in the URL. */
  provider: string | null;
}

/**
 * Covers the page while the provider's code is exchanged for a session.
 * A polite live region: the wait is announced once, then the page changes.
 */
function OAuthCallbackOverlayRaw({ provider }: OAuthCallbackOverlayProps) {
  const t = useAppT();
  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <Card className="w-full max-w-md mx-4 shadow-lg">
        <CardHeader className="text-center">
          <div role="status" aria-live="polite">
            <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
              <Loader2 className="w-6 h-6 text-primary animate-spin" aria-hidden="true" />
            </div>
            <CardTitle>{t('layouts.auth.oauth.signingIn')}</CardTitle>
            <CardDescription>
              {t('layouts.auth.oauth.signingInBody', { provider: providerName(provider ?? '') })}
            </CardDescription>
          </div>
        </CardHeader>
      </Card>
    </div>
  );
}

export const OAuthCallbackOverlay = memo(OAuthCallbackOverlayRaw);
