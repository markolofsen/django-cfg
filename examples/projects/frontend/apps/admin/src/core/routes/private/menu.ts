/**
 * User Menu
 *
 * Dashboard menu for user routes
 */

import type { MenuGroup } from '../shared';
import { routesToMenuItems } from '../shared';
import { allRoutes } from './routes';

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
      label: 'Account',
      order: 2,
      items: routesToMenuItems(allRoutes, 'account'),
    },
    {
      label: 'Development',
      order: 3,
      items: routesToMenuItems(allRoutes, 'development'),
    },
  ].filter(g => g.items.length > 0);
}
