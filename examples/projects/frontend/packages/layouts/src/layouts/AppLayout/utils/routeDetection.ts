/**
 * Route Detection Utilities
 */

import type { LayoutMode, RouteDetectors } from '../types';

/**
 * Determine layout mode from pathname
 */
export function determineLayoutMode(
  pathname: string,
  detectors: RouteDetectors
): LayoutMode {
  if (detectors.isAuthRoute(pathname)) return 'auth';
  if (detectors.isPrivateRoute(pathname)) return 'private';
  return 'public';
}

/**
 * Check if redirect is needed for unauthenticated user
 */
export function getRedirectUrl(
  pathname: string,
  isAuthenticated: boolean,
  detectors: RouteDetectors
): string | null {
  if (!isAuthenticated) {
    return detectors.getUnauthenticatedRedirect(pathname);
  }
  return null;
}
