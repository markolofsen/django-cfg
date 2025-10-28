/**
 * Route Guards
 *
 * Route protection and redirect logic
 */

import type { DjangoCfgRoutes } from './definitions';

/**
 * Check if path is a public route
 */
export function isPublicRoute(routes: DjangoCfgRoutes, path: string): boolean {
  return routes.public.getAllRoutes().some((r) => path === r.path || path.startsWith(r.path));
}

/**
 * Check if path is a private route
 */
export function isPrivateRoute(path: string): boolean {
  return path.startsWith('/private');
}

/**
 * Check if path is the auth route
 */
export function isAuthRoute(routes: DjangoCfgRoutes, path: string): boolean {
  return path.startsWith(routes.public.auth);
}

/**
 * Get redirect path for unauthenticated users
 */
export function getUnauthenticatedRedirect(routes: DjangoCfgRoutes, path: string): string | null {
  if (isPrivateRoute(path)) {
    return routes.public.auth;
  }
  return null;
}

/**
 * Get auth redirect path
 */
export function redirectToAuth(routes: DjangoCfgRoutes): string {
  return routes.public.auth;
}
