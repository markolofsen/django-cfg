/**
 * AppLayout Configuration
 *
 * Unified configuration for all layouts
 * Single source of truth for the entire application
 */

import type { AppLayoutConfig } from '@djangocfg/layouts';
import { Zap } from 'lucide-react';
import { settings } from './settings';
import {
  routes,
  isPublicRoute,
  isPrivateRoute,
  isAuthRoute,
  getUnauthenticatedRedirect,
  getPageTitle,
  generatePublicNavigation,
  generateFooterNavigation,
  menuGroups,
} from './routes';

/**
 * Complete AppLayout configuration
 *
 * This single config object controls:
 * - Public layout (MainLayout)
 * - Private layout (DashboardLayout)
 * - Route detection
 * - All navigation menus
 */
export const appLayoutConfig: AppLayoutConfig = {
  // Application metadata
  app: {
    name: settings.app.name,
    description: settings.app.description,
    logoPath: settings.app.icons.logoVector,
    siteUrl: settings.app.siteUrl,
    icons: settings.app.icons,
  },

  // API configuration
  api: {
    baseUrl: settings.api.baseUrl,
  },

  // Route configuration
  routes: {
    auth: routes.public.auth,
    defaultCallback: routes.private.overview,
    defaultAuthCallback: routes.private.overview,
    detectors: {
      isPublicRoute,
      isPrivateRoute,
      isAuthRoute,
      getUnauthenticatedRedirect,
      getPageTitle,
    },
  },

  // Public layout configuration
  publicLayout: {
    navigation: {
      homePath: routes.public.home,
      menuSections: generatePublicNavigation(settings.links.documentationUrl),
    },
    userMenu: {
      dashboardPath: routes.private.overview,
      profilePath: routes.private.profile,
    },
    footer: {
      badge: {
        icon: Zap,
        text: settings.app.name,
      },
      links: {
        docs: settings.links.documentationUrl,
        privacy: routes.legal.privacy,
        terms: routes.legal.terms,
        security: routes.legal.security,
        cookies: routes.legal.cookies,
      },
      menuSections: generateFooterNavigation(),
    },
  },

  // Private layout configuration
  privateLayout: {
    homeHref: routes.public.home,
    profileHref: routes.private.profile,
    showChat: settings.layouts.showChat,
    menuGroups,
    contentPadding: 'none',
    // headerActions can be added dynamically
  },

  // Error handling configuration
  errors: {
    enableErrorBoundary: true, // Auto-catch React errors
    supportEmail: settings.contact.email, // Global support email for error pages
    // Optional: Custom error handler
    // onError: (error, errorInfo) => {
    //   console.error('App error:', error, errorInfo);
    //   // Send to error tracking service (Sentry, etc.)
    // },
  },

  // Auth configuration
  auth: {
    termsUrl: routes.legal.terms,
    privacyUrl: routes.legal.privacy,
    supportUrl: routes.public.support,
    enablePhoneAuth: settings.layouts.enablePhoneAuth,
  },
};
