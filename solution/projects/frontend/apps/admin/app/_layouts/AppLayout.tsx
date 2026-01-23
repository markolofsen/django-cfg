'use client';

import { ReactNode } from 'react';

import { settings } from '@core/settings';
import { AppLayout as BaseAppLayout, AppLayoutProps } from '@djangocfg/layouts';
import { useLocaleSwitcher } from '@djangocfg/nextjs/i18n/client';
import { routes } from '@routes/index';

import { AdminLayout } from './AdminLayout';
import { PrivateLayout } from './PrivateLayout';
import { PublicLayout } from './PublicLayout';

interface AppLayoutComponentProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutComponentProps) {
  const { locale, locales, changeLocale } = useLocaleSwitcher();
  const appLayoutProps: AppLayoutProps = {
    children,

    // Use ready-made layout components instead of passing all props
    publicLayout: {
      component: PublicLayout,
      enabledPath: ['/', '/legal', '/contact'],
    },

    privateLayout: {
      component: PrivateLayout,
      enabledPath: ['/private', '/dashboard'],
    },

    adminLayout: {
      component: AdminLayout,
      enabledPath: '/admin',
    },

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
    // url is optional - will auto-detect from NEXT_PUBLIC_CENTRIFUGO_URL if not provided
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
      enabled: true,
      showInstallHint: true,
      logo: settings.app.media.logo192,
      delayMs: 5000,
      resetAfterDays: 7,
    },

    // Push notifications configuration
    pushNotifications: {
      enabled: true,
      vapidPublicKey: settings.push.vapidPublicKey,
      requirePWA: false,
      delayMs: 10000,
      resetAfterDays: 14,
    },

    // i18n configuration for locale switcher
    i18n: {
      locale,
      locales,
      onLocaleChange: changeLocale,
    },
  };

  return <BaseAppLayout {...appLayoutProps} />;
}

