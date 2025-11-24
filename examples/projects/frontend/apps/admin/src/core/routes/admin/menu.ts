/**
 * Admin Menu
 *
 * Dashboard menu for admin routes
 */

import type { MenuGroup } from '../shared';
import { routesToMenuItems } from '../shared';
import { allRoutes } from './routes';

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
    {
      label: 'System',
      order: 2,
      items: routesToMenuItems(allRoutes, 'system'),
    },
    {
      label: 'Account',
      order: 3,
      items: routesToMenuItems(allRoutes, 'account'),
    },
  ].filter(g => g.items.length > 0);
}
