/**
 * Admin Domain
 *
 * All admin routes and menu
 */

import { defineRoute, routesToMenuItems } from '@djangocfg/nextjs/navigation';
import type { MenuGroup, RouteDefinition } from '@djangocfg/nextjs/navigation';

// ─────────────────────────────────────────────────────────────────────────
// Routes
// ─────────────────────────────────────────────────────────────────────────

export const overview = defineRoute('/admin', {
  label: 'Overview',
  description: 'Dashboard overview',
  icon: 'LayoutDashboard',
  protected: true,
  group: 'main',
  order: 1,
});

export const crypto = defineRoute('/admin/crypto', {
  label: 'Cryptocurrency',
  description: 'Manage cryptocurrency data and wallets',
  icon: 'Bitcoin',
  protected: true,
  group: 'main',
  order: 2,
});

export const trading = defineRoute('/admin/trading', {
  label: 'Trading',
  description: 'Manage trading portfolio and orders',
  icon: 'TrendingUp',
  protected: true,
  group: 'main',
  order: 3,
});

// All routes as array
export const allRoutes: RouteDefinition[] = [
  overview,
  crypto,
  trading,
];

// Routes object (for backwards compatibility)
export const routes = {
  overview,
  crypto,
  trading,
};

// ─────────────────────────────────────────────────────────────────────────
// Menu Generation
// ─────────────────────────────────────────────────────────────────────────

/**
 * Generate admin dashboard menu
 */
export function generateMenu(): MenuGroup[] {
  return [
    {
      label: 'Main',
      order: 1,
      items: routesToMenuItems(allRoutes, 'main'),
    },
  ].filter((g) => g.items.length > 0);
}

