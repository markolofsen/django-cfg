/**
 * Routes Module
 *
 * Domain-based route structure
 * Everything organized by domain: public, user, admin
 *
 * ## Usage
 * ```ts
 * import { public, user, admin } from '@/core/routes';
 *
 * // Access routes
 * const homePath = public.routes.home.path;
 * const dashboardPath = user.routes.home.path;
 * const adminPath = admin.routes.overview.path;
 *
 * // Generate menus
 * const publicNav = public.generateNavigation();
 * const userMenu = user.generateMenu();
 * const adminMenu = admin.generateMenu();
 * ```
 */

import * as publicDomain from './public';
import * as userDomain from './private';
import * as adminDomain from './admin';

// ─────────────────────────────────────────────────────────────────────────
// Domain Exports
// ─────────────────────────────────────────────────────────────────────────

export { publicDomain as public, userDomain as user, adminDomain as admin };

// ─────────────────────────────────────────────────────────────────────────
// Shared Utilities
// ─────────────────────────────────────────────────────────────────────────

export * from './shared';

// ─────────────────────────────────────────────────────────────────────────
// Convenience Exports (for backwards compatibility)
// ─────────────────────────────────────────────────────────────────────────

/**
 * Pre-generated menus
 */
export const userMenuGroups = userDomain.generateMenu();
export const adminMenuGroups = adminDomain.generateMenu();
export const menuGroups = userMenuGroups;  // Backwards compatibility

/**
 * Pre-generated navigation
 */
export const generatePublicNavigation = () => publicDomain.generateNavigation();
export const generateFooterNavigation = () => publicDomain.generateFooter();

/**
 * All routes combined
 */
export const routes = {
  public: publicDomain.routes,
  user: userDomain.routes,
  admin: adminDomain.routes,
  private: userDomain.routes,  // Alias for backwards compatibility

  getAllRoutes() {
    return [
      ...publicDomain.routes.allRoutes,
      ...userDomain.routes.allRoutes,
      ...adminDomain.routes.allRoutes,
    ];
  },
};
