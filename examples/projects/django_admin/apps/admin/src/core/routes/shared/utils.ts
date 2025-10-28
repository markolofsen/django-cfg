/**
 * Shared Utilities
 *
 * Common utilities used across all route domains
 */

import { settings } from '@/core/settings';
import type { RouteDefinition, RouteMetadata, MenuItem, BreadcrumbItem } from './types';

// ─────────────────────────────────────────────────────────────────────────
// Route Definition Helper
// ─────────────────────────────────────────────────────────────────────────

/**
 * Define a route with automatic basePath injection
 *
 * NOTE: For static builds, Next.js automatically prepends basePath to <Link> hrefs,
 * so we don't add it here. For dev mode, we need to add it manually.
 */
export function defineRoute(path: string, metadata: RouteMetadata): RouteDefinition {
  // In static builds, Next.js handles basePath automatically
  // In dev mode, we need to add it manually for consistency
  const fullPath = settings.isStaticBuild ? path : `${settings.basePath}${path}`;

  return {
    path: fullPath,
    metadata,
  };
}

// ─────────────────────────────────────────────────────────────────────────
// Route Guards
// ─────────────────────────────────────────────────────────────────────────

export function isPublicRoute(path: string): boolean {
  const publicPaths = ['/', '/auth', '/legal'];
  return publicPaths.some(p => path === p || path.startsWith(p + '/'));
}

export function isPrivateRoute(path: string): boolean {
  return path.startsWith('/private');
}

export function isAdminRoute(path: string): boolean {
  return path.startsWith('/admin');
}

export function isAuthRoute(path: string): boolean {
  return path.startsWith('/auth');
}

export function getUnauthenticatedRedirect(path: string): string | null {
  if (isPrivateRoute(path) || isAdminRoute(path)) {
    // In static builds, Next.js handles basePath automatically
    return settings.isStaticBuild ? '/auth' : `${settings.basePath}/auth`;
  }
  return null;
}

export function redirectToAuth(): string {
  // In static builds, Next.js handles basePath automatically
  return settings.isStaticBuild ? '/auth' : `${settings.basePath}/auth`;
}

// ─────────────────────────────────────────────────────────────────────────
// Menu Generation Helper
// ─────────────────────────────────────────────────────────────────────────

/**
 * Filter and convert routes to menu items
 */
export function routesToMenuItems(routes: RouteDefinition[], groupName: string): MenuItem[] {
  return routes
    .filter(r =>
      r.metadata.group === groupName &&
      r.metadata.icon &&
      (r.metadata.show === undefined || r.metadata.show === true)
    )
    .sort((a, b) => (a.metadata.order || 0) - (b.metadata.order || 0))
    .map(r => ({
      path: r.path,
      label: r.metadata.label,
      icon: r.metadata.icon!,
    }));
}

// ─────────────────────────────────────────────────────────────────────────
// Route Lookup
// ─────────────────────────────────────────────────────────────────────────

export function findRoute(routes: RouteDefinition[], path: string): RouteDefinition | undefined {
  return routes.find(r => r.path === path);
}

export function findRouteByPattern(routes: RouteDefinition[], path: string): RouteDefinition | undefined {
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

export function getPageTitle(routes: RouteDefinition[], path: string, fallback = 'Dashboard'): string {
  const route = findRouteByPattern(routes, path);
  return route?.metadata.label || fallback;
}

// ─────────────────────────────────────────────────────────────────────────
// Breadcrumbs
// ─────────────────────────────────────────────────────────────────────────

export function generateBreadcrumbs(
  routes: RouteDefinition[],
  currentPath: string,
  options: { homeLabel?: string; homePath?: string; includeHome?: boolean } = {}
): BreadcrumbItem[] {
  // In static builds, Next.js handles basePath automatically
  const defaultHomePath = settings.isStaticBuild ? '/' : settings.basePath || '/';
  const { homeLabel = 'Home', homePath = defaultHomePath, includeHome = true } = options;
  const breadcrumbs: BreadcrumbItem[] = [];

  if (includeHome && currentPath !== homePath) {
    breadcrumbs.push({ label: homeLabel, path: homePath, isActive: false });
  }

  const segments = currentPath.split('/').filter(Boolean);
  let currentSegmentPath = '';

  segments.forEach((segment, index) => {
    currentSegmentPath += '/' + segment;
    const isLast = index === segments.length - 1;
    const route = findRoute(routes, currentSegmentPath);

    if (route) {
      breadcrumbs.push({ label: route.metadata.label, path: route.path, isActive: isLast });
    } else if (isLast) {
      breadcrumbs.push({
        label: segment.charAt(0).toUpperCase() + segment.slice(1),
        path: currentSegmentPath,
        isActive: true,
      });
    }
  });

  return breadcrumbs;
}

// ─────────────────────────────────────────────────────────────────────────
// Active Route
// ─────────────────────────────────────────────────────────────────────────

export function isActive(current: string, target: string): boolean {
  if (current === target) return true;
  if (target !== '/' && current.startsWith(target + '/')) return true;
  return false;
}
