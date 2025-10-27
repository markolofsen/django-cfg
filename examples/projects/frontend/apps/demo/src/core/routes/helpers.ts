/**
 * Route Helpers
 *
 * Utility functions for routes
 */

import type { UnrealonRoutes } from './definitions';

// ─────────────────────────────────────────────────────────────────────────
// Page Titles
// ─────────────────────────────────────────────────────────────────────────

/**
 * Get page title for a given path
 */
export function getPageTitle(routes: UnrealonRoutes, path: string): string {
  // Try exact match first
  const label = routes.getRouteLabel(path);
  if (label) {
    return label;
  }

  // Handle dynamic workspace routes
  // if (path.startsWith('/private/workspaces/')) {
  //   return 'Workspace Details';
  // }

  return 'No label';
}

// ─────────────────────────────────────────────────────────────────────────
// Active Route Checking
// ─────────────────────────────────────────────────────────────────────────

/**
 * Check if a route is active
 */
export function isActive(current: string, target: string): boolean {
  if (current === target) return true;

  // Check if current path starts with target (for nested routes)
  if (target !== '/' && current.startsWith(target)) {
    return true;
  }

  return false;
}

// ─────────────────────────────────────────────────────────────────────────
// Breadcrumbs
// ─────────────────────────────────────────────────────────────────────────

export interface BreadcrumbItem {
  label: string;
  path: string;
  isActive: boolean;
}

/**
 * Generate breadcrumbs for current path
 */
export function generateBreadcrumbs(routes: UnrealonRoutes, currentPath: string): BreadcrumbItem[] {
  const breadcrumbs: BreadcrumbItem[] = [];

  // Add home if not on home page
  if (currentPath !== routes.public.home) {
    breadcrumbs.push({
      label: 'Home',
      path: routes.public.home,
      isActive: false,
    });
  }

  // Add current page
  const currentRoute = routes.getRouteByPath(currentPath);
  if (currentRoute) {
    breadcrumbs.push({
      label: currentRoute.metadata.label,
      path: currentRoute.path,
      isActive: true,
    });
  } else {
    // Handle dynamic routes
    const title = getPageTitle(routes, currentPath);
    breadcrumbs.push({
      label: title,
      path: currentPath,
      isActive: true,
    });
  }

  return breadcrumbs;
}
