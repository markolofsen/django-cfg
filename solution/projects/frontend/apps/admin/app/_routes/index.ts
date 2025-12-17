/**
 * Routes Module
 *
 * Domain-based route structure
 * Everything organized by domain: public, user, admin
 *
 * ## Usage
 * ```ts
 * import { public, user, admin } from '@core/routes';
 *
 * // Access routes
 * const homePath = public.routes.home.path;
 * const userDashboardPath = user.routes.home.path;
 * const adminOverviewPath = admin.routes.overview.path;
 * const adminRQPath = admin.routes.rq.path;
 *
 * // Generate menus
 * const publicNav = public.generateNavigation();
 * const userMenu = user.generateMenu();
 * const adminMenu = admin.generateMenu();
 * ```
 */

import * as adminDomain from './admin';
import * as privateDomain from './private';
import * as publicDomain from './public';

// ─────────────────────────────────────────────────────────────────────────
// Domain Exports
// ─────────────────────────────────────────────────────────────────────────

export {
  publicDomain as public,
  privateDomain as private,
  adminDomain as admin,
};

// ─────────────────────────────────────────────────────────────────────────
// Shared Utilities (re-exported from @djangocfg/nextjs/navigation)
// ─────────────────────────────────────────────────────────────────────────

export * from '@djangocfg/nextjs/navigation';

// ─────────────────────────────────────────────────────────────────────────
// Convenience Exports (for backwards compatibility)
// ─────────────────────────────────────────────────────────────────────────

/**
 * Pre-generated menus
 */
export const privateMenuGroups = privateDomain.generateMenu();
export const adminMenuGroups = adminDomain.generateMenu();
export const menuGroups = privateMenuGroups;  // Backwards compatibility

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
  admin: adminDomain.routes,
  private: privateDomain.routes,

  getAllRoutes() {
    return [
      ...publicDomain.allRoutes,
      ...privateDomain.allRoutes,
      ...adminDomain.allRoutes,
    ];
  },
};
