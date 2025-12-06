/**
 * User Domain (Private)
 *
 * All user routes and menu
 */

import { defineRoute, routesToMenuItems } from '@djangocfg/nextjs/navigation';
import type { MenuGroup, RouteDefinition } from '@djangocfg/nextjs/navigation';

// ─────────────────────────────────────────────────────────────────────────
// Routes
// ─────────────────────────────────────────────────────────────────────────

export const home = defineRoute('/private', {
  label: 'Home',
  description: 'Dashboard home',
  icon: 'LayoutDashboard',
  protected: true,
  group: 'main',
  order: 1,
});

export const profile = defineRoute('/private/profile', {
  label: 'Profile',
  description: 'User profile and settings',
  icon: 'User',
  protected: true,
  group: 'account',
  order: 1,
});


// All routes as array
export const allRoutes: RouteDefinition[] = [home, profile];

// Routes object (for backwards compatibility)
export const routes = {
  home,
  profile,
  allRoutes,
};

// ─────────────────────────────────────────────────────────────────────────
// Menu Generation
// ─────────────────────────────────────────────────────────────────────────

/**
 * Generate user dashboard menu
 */
export function generateMenu(): MenuGroup[] {
  return [
    {
      label: 'Main',
      order: 1,
      items: routesToMenuItems(allRoutes, 'main'),
    },
    {
      label: 'Tools',
      order: 2,
      items: routesToMenuItems(allRoutes, 'tools'),
    },
    {
      label: 'Account',
      order: 3,
      items: routesToMenuItems(allRoutes, 'account'),
    },
  ].filter((g) => g.items.length > 0);
}

