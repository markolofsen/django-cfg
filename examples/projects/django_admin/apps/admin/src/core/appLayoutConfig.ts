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
  isAdminRoute,
  isAuthRoute,
  getUnauthenticatedRedirect,
  getPageTitle,
  generatePublicNavigation,
  generateFooterNavigation,
  menuGroups,
  adminMenuGroups,
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
    auth: routes.public.auth.path,
    defaultCallback: routes.private.home.path,
    defaultAuthCallback: routes.public.auth.path,
    detectors: {
      isPublicRoute,
      isPrivateRoute,
      isAdminRoute,
      isAuthRoute,
      getUnauthenticatedRedirect,
      getPageTitle: (path: string) => getPageTitle(routes.getAllRoutes(), path),
    },
  },

  // Public layout configuration
  publicLayout: {
    navigation: {
      homePath: routes.public.home.path,
      menuSections: generatePublicNavigation(),
    },
    userMenu: {
      dashboardPath: routes.private.home.path,
      profilePath: routes.private.profile.path,
    },
    footer: {
      badge: {
        icon: Car,
        text: settings.app.name,
      },
      links: {
        privacy: routes.public.privacy.path,
        terms: routes.public.terms.path,
        security: routes.public.security.path,
        cookies: routes.public.cookies.path,
      },
      menuSections: generateFooterNavigation(),
    },
  },

  // Private layout configuration
  privateLayout: {
    homeHref: routes.private.home.path,
    profileHref: routes.private.profile.path,
    showChat: settings.layouts.showChat,
    menuGroups,
    contentPadding: 'none',
    // headerActions can be added dynamically
  },

  // Admin layout configuration
  adminLayout: {
    menuSections: adminMenuGroups.map(group => ({
      title: group.label,
      items: group.items.map(item => ({
        label: item.label,
        path: item.path,
        icon: item.icon,
        badge: item.badge,
      })),
    })),
  },
};
