/**
 * Core Module Exports
 *
 * Centralized export for all core configurations and utilities
 * Optimized for AppLayout unified system
 */

// ─────────────────────────────────────────────────────────────────────────
// Settings
// ─────────────────────────────────────────────────────────────────────────

export { settings } from './settings';

// ─────────────────────────────────────────────────────────────────────────
// Routes - Complete routing system with metadata
// ─────────────────────────────────────────────────────────────────────────

export {
  // Route instances
  routes,

  // Menu generation
  menuGroups,
  generatePublicNavigation,
  generateFooterNavigation,

  // Page utilities
  getPageTitle,
  generateBreadcrumbs,

  // Active state
  isActive,

  // Route guards
  isPublicRoute,
  isPrivateRoute,
  isAuthRoute,
  getUnauthenticatedRedirect,
  redirectToAuth,
} from './routes';

// Route types
export type {
  RouteMetadata,
  RouteDefinition,
  MenuGroup,
  MenuItem,
  BreadcrumbItem,
} from './routes';

// ─────────────────────────────────────────────────────────────────────────
// AppLayout Configuration (Main)
// ─────────────────────────────────────────────────────────────────────────

/**
 * Unified AppLayout configuration
 *
 * This is the ONLY config you need!
 * Controls both PublicLayout and PrivateLayout
 */
export { appLayoutConfig } from './appLayoutConfig';

// ─────────────────────────────────────────────────────────────────────────
// Deprecated Exports (for backwards compatibility)
// TODO: Remove these after migration complete
// ─────────────────────────────────────────────────────────────────────────

// export { layoutConfig } from './layoutConfig';        // Replaced by appLayoutConfig.publicLayout
// export { dashboardConfig } from './dashboardConfig';  // Replaced by appLayoutConfig.privateLayout
// export { smartLayoutConfig } from './smartLayoutConfig'; // Replaced by appLayoutConfig
