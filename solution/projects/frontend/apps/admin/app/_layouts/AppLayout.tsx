'use client';

import { ReactNode } from 'react';
import { AppLayout as BaseAppLayout, type AppLayoutProps } from '@djangocfg/layouts';
import { settings } from '@core/settings';
import { routes } from '@routes/index';
import { PublicLayout } from './PublicLayout';
import { PrivateLayout } from './PrivateLayout';
import { AdminLayout } from './AdminLayout';

interface AppLayoutComponentProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutComponentProps) {
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
        defaultCallback: routes.admin.overview?.path || routes.user.home.path,
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
      enabled: false,
      autoConnect: false,
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
  };

  return <BaseAppLayout {...appLayoutProps} />;
}

