/**
 * Routes Module
 *
 * Simple, flat structure with all routing functionality
 *
 * ## Usage
 * ```ts
 * import { routes, generatePublicNavigation } from '@/core/routes';
 *
 * // Access routes
 * const home = routes.public.home;
 * const dashboard = routes.private.overview;
 *
 * // Generate menus
 * const menu = generatePublicNavigation();
 * ```
 */

import {
  generateDashboardMenu,
  generatePublicNavigation,
  generateFooterNavigation,
} from './menus';
import {
  isPublicRoute as isPublicRouteFn,
  isPrivateRoute,
  isAuthRoute as isAuthRouteFn,
  getUnauthenticatedRedirect as getUnauthenticatedRedirectFn,
  redirectToAuth as redirectToAuthFn,
} from './guards';
import {
  getPageTitle as getPageTitleFn,
  isActive,
  generateBreadcrumbs as generateBreadcrumbsFn,
} from './helpers';
import { DjangoCfgRoutes } from './definitions';

// ─────────────────────────────────────────────────────────────────────────
// Singleton Instance
// ─────────────────────────────────────────────────────────────────────────

/**
 * Global routes instance
 */
export const routes = new DjangoCfgRoutes();

// ─────────────────────────────────────────────────────────────────────────
// Pre-generated Menus
// ─────────────────────────────────────────────────────────────────────────

/**
 * Dashboard menu (pre-generated)
 */
export const menuGroups = generateDashboardMenu(routes.private);

// ─────────────────────────────────────────────────────────────────────────
// Menu Generators (with routes bound)
// ─────────────────────────────────────────────────────────────────────────

export function generatePublicNav() {
  return generatePublicNavigation(routes.public);
}

export function generateFooterNav() {
  return generateFooterNavigation(routes.public);
}

// Aliases for backwards compatibility
export { generatePublicNav as generatePublicNavigation };
export { generateFooterNav as generateFooterNavigation };

// ─────────────────────────────────────────────────────────────────────────
// Route Guards (with routes bound)
// ─────────────────────────────────────────────────────────────────────────

export function isPublicRoute(path: string) {
  return isPublicRouteFn(routes, path);
}

export function isAuthRoute(path: string) {
  return isAuthRouteFn(routes, path);
}

export function getUnauthenticatedRedirect(path: string) {
  return getUnauthenticatedRedirectFn(routes, path);
}

export function redirectToAuth(path: string) {
  return redirectToAuthFn(routes);
}

export { isPrivateRoute };

// ─────────────────────────────────────────────────────────────────────────
// Helpers (with routes bound)
// ─────────────────────────────────────────────────────────────────────────

export function getPageTitle(path: string) {
  return getPageTitleFn(routes, path);
}

export function generateBreadcrumbs(path: string) {
  return generateBreadcrumbsFn(routes, path);
}

export { isActive };

// ─────────────────────────────────────────────────────────────────────────
// Type Exports
// ─────────────────────────────────────────────────────────────────────────

export type {
  RouteMetadata,
  RouteDefinition,
  PublicRoutes,
  PrivateRoutes,
} from './definitions';

export type {
  MenuItem,
  MenuGroup,
} from './menus';

export type {
  BreadcrumbItem,
} from './helpers';
