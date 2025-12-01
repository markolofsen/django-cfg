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
  userMenuGroups,
  adminMenuGroups,
  generatePublicNavigation,
  generateFooterNavigation,

  // Page utilities
  getPageTitle,
  isActive,

  // Route guards
  getUnauthenticatedRedirect,
  redirectToAuth,
} from '../_routes/index';

// Route types
export type {
  RouteMetadata,
  RouteDefinition,
  MenuGroup,
  MenuItem,
  NavigationItem,
  NavigationSection,
  BreadcrumbItem,
} from '@djangocfg/nextjs/navigation';

// ─────────────────────────────────────────────────────────────────────────
// Deprecated Exports (for backwards compatibility)
// TODO: Remove these after migration complete
// ─────────────────────────────────────────────────────────────────────────

// export { layoutConfig } from './layoutConfig';        // Replaced by appLayoutConfig.publicLayout
// export { dashboardConfig } from './dashboardConfig';  // Replaced by appLayoutConfig.privateLayout
// export { smartLayoutConfig } from './smartLayoutConfig'; // Replaced by appLayoutConfig
