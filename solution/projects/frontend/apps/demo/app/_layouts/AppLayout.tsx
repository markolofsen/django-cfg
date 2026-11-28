'use client';

import { ReactNode } from 'react';

import { settings } from '@core/settings';
import { routes } from '@routes/public';
import { privateRoutes } from '@routes/private';
import { BaseApp } from '@djangocfg/layouts';
import { useLocaleSwitcher } from '@djangocfg/nextjs/i18n/client';

/**
 * Top-level app shell — wires theme, i18n, and the framework auth
 * context exactly the way every real `@djangocfg/*` Next.js app does.
 * Page-specific chrome (navbars, sidebars) sits inside the route
 * groups under `(pages)/...`.
 *
 * BaseApp provides the one QueryClient (django-cfg's defaults) the generated
 * hooks use; a query whose view is `invalidated_by` a topic refetches on it.
 *
 * Realtime is BaseApp's default: the socket is ws(s)://<auth.apiUrl>/ws
 * (NEXT_PUBLIC_API_URL) and opens only when a page calls useTopic (/realtime).
 */
export function AppLayout({ children }: { children: ReactNode }) {
  const { locale, locales, changeLocale } = useLocaleSwitcher();

  return (
    <BaseApp
      project={settings.app.name}
      theme={{ defaultTheme: 'system', storageKey: 'djangocfg-demo-theme' }}
      i18n={{ locale, locales, onLocaleChange: changeLocale }}
      auth={{
        apiUrl: settings.api.baseUrl,
        // One sign-in host for the subdomains (README → "Single sign-in host"). Off unless NEXT_PUBLIC_SSO=true; the host is
        // derived from NEXT_PUBLIC_SITE_URL (auth.<apex>), and on that very host the same flag means "I am the sign-in".
        ...(process.env.NEXT_PUBLIC_SSO === 'true' ? { sso: true as const } : {}),
        routes: {
          auth: routes.auth,
          defaultCallback: privateRoutes.dashboard,
          defaultAuthCallback: routes.auth,
        },
      }}
    >
      {children}
    </BaseApp>
  );
}
