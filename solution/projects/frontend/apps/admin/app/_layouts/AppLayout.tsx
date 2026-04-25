'use client';

import { ReactNode } from 'react';

import { settings } from '@core/settings';
import { AppLayout as BaseAppLayout, AppLayoutProps } from '@djangocfg/layouts';
import { useLocaleSwitcher } from '@djangocfg/nextjs/i18n/client';
import { routing } from '@djangocfg/nextjs/i18n/routing';
import { routes } from '@routes/index';

import { AdminLayout } from './AdminLayout';
import { PrivateLayout } from './PrivateLayout';
import { PublicLayout } from './PublicLayout';

interface AppLayoutComponentProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutComponentProps) {
  const { locale, locales, changeLocale } = useLocaleSwitcher();

  const appLayoutProps: Omit<AppLayoutProps, 'children'> = {
    layouts: {
      public: {
        component: PublicLayout,
        enabledPath: ['/', '/legal', '/contact'],
      },
      private: {
        component: PrivateLayout,
        enabledPath: ['/private', '/dashboard'],
      },
      admin: {
        component: AdminLayout,
        enabledPath: '/admin',
      },
    },
    baseApp: {
      // Theme configuration
      theme: {
        defaultTheme: 'system', // Use system preference
        storageKey: 'djangocfg-theme',
      },

      // Auth provider configuration
      auth: {
        apiUrl: settings.api.baseUrl,
        routes: {
          auth: routes.public.auth.path,
          defaultCallback: routes.private.home.path,
          defaultAuthCallback: routes.public.auth.path,
        },
      },

      // Analytics configuration
      analytics: {
        googleTrackingId: settings.analytics.googleTrackingId,
      },

      // Centrifugo configuration
      centrifugo: {
        enabled: true,
        autoConnect: true,
      },

      // Error tracking configuration
      errorTracking: {
        validation: { enabled: true, showToast: true },
        cors: { enabled: true, showToast: true },
        network: { enabled: true, showToast: true },
        onError: (error) => {
          console.error('AppLayout Error:', error);
        },
      },

      // Error boundary configuration
      errorBoundary: {
        enabled: true,
        supportEmail: settings.contact.email,
        onError: (error, errorInfo) => {
          console.error('AppLayout ErrorBoundary caught:', error, errorInfo);
        },
      },

      // PWA install prompt configuration
      pwaInstall: {
        enabled: false,
        showInstallHint: true,
        logo: settings.app.media.logo192,
        delayMs: 5000,
        resetAfterDays: 7,
      },

      // Project name — used by monitor and debug panel
      project: settings.app.name,
    },
    // i18n configuration for locale switcher.
    // Passing `routing` (from `defineRouting()`) makes BaseApp build a
    // locale-aware Link adapter so every <Link> rendered inside layouts keeps
    // the active locale prefix on click.
    i18n: {
      locale,
      locales,
      onLocaleChange: changeLocale,
      routing,
    },
  };

  return <BaseAppLayout {...appLayoutProps}>{children}</BaseAppLayout>;
}
