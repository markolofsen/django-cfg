/**
 * AppLayout Configuration
 *
 * Unified configuration for all layouts
 * Single source of truth for the entire application
 */

import type { AppLayoutConfig } from '@djangocfg/layouts';
import { Car } from 'lucide-react';
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
    defaultCallback: settings.basePath + routes.private.overview,
    defaultAuthCallback: settings.basePath + routes.private.overview,
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
      menuSections: generatePublicNavigation(),
    },
    userMenu: {
      dashboardPath: routes.private.overview,
      profilePath: routes.private.profile,
    },
    footer: {
      badge: {
        icon: Car,
        text: settings.app.name,
      },
      links: {
        docs: routes.public.docsExternal,
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
};
