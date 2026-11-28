/**
 * AppErrorFallback — the one localized crash screen for Next app layouts.
 *
 * Exactly ONE action: "Refresh Page" (hard reload). A soft `reset()` re-mounts
 * the same broken tree and usually crashes again, so it is not offered as a
 * second near-identical button. Used by `BaseApp` (via UiProviders) and
 * `ErrorBoundary`.
 */

'use client';

import { getT } from '@djangocfg/i18n';

export interface AppErrorFallbackProps {
  supportEmail?: string;
}

export function AppErrorFallback({ supportEmail }: AppErrorFallbackProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="max-w-md w-full space-y-4 text-center">
        <h1 className="text-2xl font-bold text-foreground">{getT('layouts.errors.somethingWentWrong')}</h1>
        <p className="text-muted-foreground">{getT('layouts.errors.tryRefreshing')}</p>
        {supportEmail && (
          <p className="text-sm text-muted-foreground">
            {getT('layouts.errors.persistsContact', { email: '' })}{' '}
            <a href={`mailto:${supportEmail}`} className="text-primary hover:underline">
              {supportEmail}
            </a>
          </p>
        )}
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
        >
          {getT('layouts.errors.refreshPage')}
        </button>
      </div>
    </div>
  );
}
