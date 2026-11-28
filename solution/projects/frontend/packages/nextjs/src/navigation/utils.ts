/**
 * Navigation Utilities
 *
 * Common utilities for route definitions and navigation
 */

import type { RouteDefinition, RouteMetadata, MenuItem, NavGroup, NavGroupWithRoutes } from './types';

// ─────────────────────────────────────────────────────────────────────────
// Route Definition Helper
// ─────────────────────────────────────────────────────────────────────────

/**
 * Define a route with metadata
 *
 * IMPORTANT: Next.js automatically handles basePath for <Link> components when
 * basePath is set in next.config.ts. We should NOT add basePath manually here,
 * as it would cause double-prefixing in static builds.
 *
 * @param path - Route path (e.g., '/dashboard', '/admin/users')
 * @param metadata - Route metadata (label, icon, etc.)
 */
export function defineRoute(
  path: string,
  metadata: RouteMetadata,
): RouteDefinition {
  // Always return path as-is. Next.js will handle basePath automatically
  // for <Link> components when basePath is set in next.config.ts
  return {
    path,
    metadata,
  };
}

// ─────────────────────────────────────────────────────────────────────────
// Route Guards
// ─────────────────────────────────────────────────────────────────────────

/**
 * Get redirect path for unauthenticated users
 */
export function getUnauthenticatedRedirect(
  path: string,
  authPath: string = '/auth',
): string | null {
  if (path.startsWith('/private') || path.startsWith('/admin')) {
    // Return path as-is. Next.js will handle basePath automatically for router.push()
    // when basePath is set in next.config.ts
    return authPath;
  }
  return null;
}

/**
 * Get redirect path to auth page
 */
export function redirectToAuth(
  authPath: string = '/auth',
): string {
  // Return path as-is. Next.js will handle basePath automatically for router.push()
  // when basePath is set in next.config.ts
  return authPath;
}

// ─────────────────────────────────────────────────────────────────────────
// Route Lookup
// ─────────────────────────────────────────────────────────────────────────

export function findRoute(
  routes: RouteDefinition[],
  path: string
): RouteDefinition | undefined {
  return routes.find((r) => r.path === path);
}

export function findRouteByPattern(
  routes: RouteDefinition[],
  path: string
): RouteDefinition | undefined {
  const exact = findRoute(routes, path);
  if (exact) return exact;

  const segments = path.split('/').filter(Boolean);
  for (let i = segments.length; i > 0; i--) {
    const parentPath = '/' + segments.slice(0, i).join('/');
    const parent = findRoute(routes, parentPath);
    if (parent) return parent;
  }

  return undefined;
}

// ─────────────────────────────────────────────────────────────────────────
// Page Title
// ─────────────────────────────────────────────────────────────────────────

export function getPageTitle(
  routes: RouteDefinition[],
  path: string,
  fallback = 'Dashboard'
): string {
  const route = findRouteByPattern(routes, path);
  return route?.metadata.label || fallback;
}

// ─────────────────────────────────────────────────────────────────────────
// Active Route
// ─────────────────────────────────────────────────────────────────────────

/**
 * Check if a route is active
 *
 * @param current - Current pathname
 * @param target - Target route path to check
 * @param allRoutes - Optional array of all routes to prevent parent paths from being active when child paths are active
 * @returns true if the route is active
 */
export function isActive(
  current: string,
  target: string,
  allRoutes?: RouteDefinition[]
): boolean {
  const matches =
    current === target || (target !== '/' && current.startsWith(target + '/'));

  // If allRoutes is provided, check for more specific paths
  if (matches && allRoutes) {
    return !allRoutes.some(
      (otherRoute) =>
        otherRoute.path !== target &&
        otherRoute.path.startsWith(target + '/') &&
        (current === otherRoute.path ||
          current.startsWith(otherRoute.path + '/'))
    );
  }

  return matches;
}

// ─────────────────────────────────────────────────────────────────────────
// Menu Generation Helper
// ─────────────────────────────────────────────────────────────────────────

/**
 * Filter and convert routes to menu items
 */
export function routesToMenuItems(
  routes: RouteDefinition[],
  groupName: string
): MenuItem[] {
  return routes
    .filter(
      (r) =>
        r.metadata.group === groupName &&
        r.metadata.icon &&
        (r.metadata.show === undefined || r.metadata.show === true)
    )
    .sort((a, b) => (a.metadata.order || 0) - (b.metadata.order || 0))
    .map((r) => ({
      path: r.path,
      label: r.metadata.label,
      icon: r.metadata.icon!,
      ...(r.metadata.badge !== undefined && { badge: r.metadata.badge }),
    }));
}

// ─────────────────────────────────────────────────────────────────────────
// Navigation Groups Helper
// ─────────────────────────────────────────────────────────────────────────

/**
 * Group routes by navigation groups
 *
 * @param routes - Array of route definitions
 * @param groups - Array of navigation group definitions
 * @returns Array of groups with their routes, filtered by dynamic flag
 *
 * @example
 * ```ts
 * const navGroups = [
 *   { id: 'dashboard', label: 'Dashboard', order: 1 },
 *   { id: 'extensions', label: 'Extensions', order: 2, dynamic: true },
 * ];
 *
 * const groupedRoutes = groupRoutesByNavGroups(allRoutes, navGroups);
 * // Returns groups with routes, hiding dynamic groups with no routes
 * ```
 */
export function groupRoutesByNavGroups(
  routes: RouteDefinition[],
  groups: NavGroup[]
): NavGroupWithRoutes[] {
  return groups
    .map((group) => ({
      ...group,
      routes: routes
        .filter(
          (r) =>
            r.metadata.group === group.id &&
            (r.metadata.show === undefined || r.metadata.show === true)
        )
        .sort((a, b) => (a.metadata.order || 0) - (b.metadata.order || 0)),
    }))
    .filter((group) => {
      // Dynamic groups are only shown if they have routes
      if (group.dynamic) {
        return group.routes.length > 0;
      }
      // Non-dynamic groups are always shown
      return true;
    })
    .sort((a, b) => a.order - b.order);
}

