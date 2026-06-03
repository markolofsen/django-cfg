'use client';

import { ReactNode } from 'react';

import { settings } from '@core/settings';
import { BaseApp } from '@djangocfg/layouts';
import { useLocaleSwitcher } from '@djangocfg/nextjs/i18n/client';
import { routing } from '@djangocfg/nextjs/i18n/routing';
import { routes } from '@routes/index';

/**
 * Providers root — thin wrapper over `BaseApp` (theme, auth, i18n, analytics,
 * centrifugo, error tracking, monitor). Mounted once in `[locale]/layout.tsx`.
 *
 * Per-section shells are chosen by native route-group `layout.tsx` files:
 *   - `(pages)/private/layout.tsx` → `PrivateLayout`
 *   - `(pages)/admin/layout.tsx`   → `AdminLayout` (PrivateLayout + admin menu)
 *   - public pages wrap themselves in `PublicLayout`
 *   - `/auth` stays fullscreen (no shell)
 */
export function AppLayout({ children }: { children: ReactNode }) {
  const { locale, locales, changeLocale } = useLocaleSwitcher();

  return (
    <BaseApp
      project={settings.app.name}
      theme={{ defaultTheme: 'system', storageKey: 'djangocfg-theme' }}
      auth={{
        apiUrl: settings.api.baseUrl,
        routes: {
          auth: routes.public.auth.path,
          defaultCallback: routes.private.home.path,
          defaultAuthCallback: routes.public.auth.path,
        },
      }}
      analytics={{ googleTrackingId: settings.analytics.googleTrackingId }}
      centrifugo={{ enabled: true, autoConnect: true }}
      errorTracking={{
        validation: { enabled: true, showToast: true },
        cors: { enabled: true, showToast: true },
        network: { enabled: true, showToast: true },
        onError: (error) => console.error('AppLayout Error:', error),
      }}
      errorBoundary={{
        enabled: true,
        supportEmail: settings.contact.email,
        onError: (error, errorInfo) =>
          console.error('AppLayout ErrorBoundary caught:', error, errorInfo),
      }}
      // Passing `routing` (from `defineRouting()`) makes BaseApp build a
      // locale-aware Link adapter so every <Link> inside layouts keeps the
      // active locale prefix on click.
      i18n={{ locale, locales, onLocaleChange: changeLocale, routing }}
    >
      {children}
    </BaseApp>
  );
}
