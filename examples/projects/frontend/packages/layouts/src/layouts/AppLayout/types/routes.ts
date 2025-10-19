/**
 * Route Types
 */

/**
 * Route configuration
 */
export interface RouteConfig {
  /** Authentication route */
  auth: string;

  /** Default redirect after login */
  defaultCallback: string;

  /** Redirect for authenticated users on auth page */
  defaultAuthCallback?: string;

  /** Route detector functions */
  detectors: RouteDetectors;
}

/**
 * Route detection functions
 */
export interface RouteDetectors {
  /** Check if route is public */
  isPublicRoute: (path: string) => boolean;

  /** Check if route is private/protected */
  isPrivateRoute: (path: string) => boolean;

  /** Check if route is auth page */
  isAuthRoute: (path: string) => boolean;

  /** Get redirect URL for unauthenticated users */
  getUnauthenticatedRedirect: (path: string) => string | null;

  /** Get page title for route */
  getPageTitle: (path: string) => string;
}

/**
 * Layout mode based on route
 */
export type LayoutMode = 'public' | 'private' | 'auth';
