/**
 * Public Navigation
 *
 * Navigation for public pages (header, footer)
 */

import type { NavigationSection, RouteDefinition } from '../shared';
import { allRoutes } from './routes';

/**
 * Generate public navigation (header)
 */
export function generateNavigation(): NavigationSection[] {
  return [
    {
      title: 'Home',
      items: getGroupItems('main'),
    },
    {
      title: 'Components',
      items: getGroupItems('components'),
    },
    {
      title: 'Packages',
      items: getGroupItems('packages'),
    },
    {
      title: 'Projects',
      items: getGroupItems('projects'),
    },
    {
      title: 'Demo',
      items: getGroupItems('demo'),
    },
    {
      title: 'Contact',
      items: getGroupItems('contact'),
    },
  ].filter(s => s.items.length > 0);
}

/**
 * Generate footer navigation
 */
export function generateFooter(): NavigationSection[] {
  return [
    {
      title: 'Legal',
      items: getGroupItems('legal'),
    },
  ].filter(s => s.items.length > 0);
}

// Helper
function getGroupItems(groupName: string) {
  return allRoutes
    .filter(r => r.metadata.group === groupName && (r.metadata.show === undefined || r.metadata.show === true))
    .sort((a, b) => (a.metadata.order || 0) - (b.metadata.order || 0))
    .map(r => ({ label: r.metadata.label, path: r.path }));
}
