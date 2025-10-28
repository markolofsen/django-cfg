/**
 * Menu Generation
 *
 * All menu generation logic in one place
 */

import type { LucideIcon } from 'lucide-react';
import type { NavigationSection } from '@djangocfg/layouts';
import type { PublicRoutes, PrivateRoutes, RouteDefinition } from './definitions';

// ─────────────────────────────────────────────────────────────────────────
// Menu Types
// ─────────────────────────────────────────────────────────────────────────

export interface MenuItem {
  path: string;
  label: string;
  icon: LucideIcon;
  badge?: string | number;
  subItems?: MenuItem[];
}

export interface MenuGroup {
  label: string;
  order: number;
  items: MenuItem[];
}

interface GroupConfig {
  name: string;
  title: string;
  order: number;
}

// ─────────────────────────────────────────────────────────────────────────
// Core Generators
// ─────────────────────────────────────────────────────────────────────────

/**
 * Generate menu groups from routes with metadata
 */
function generateMenuGroups(
  routes: RouteDefinition[],
  configs: GroupConfig[]
): MenuGroup[] {
  const groups: MenuGroup[] = [];

  for (const config of configs) {
    const groupRoutes = routes
      .filter(r => r.metadata.group === config.name && r.metadata.icon)
      .sort((a, b) => (a.metadata.order || 0) - (b.metadata.order || 0));

    if (groupRoutes.length > 0) {
      groups.push({
        label: config.title,
        order: config.order,
        items: groupRoutes.map(r => ({
          path: r.path,
          label: r.metadata.label,
          icon: r.metadata.icon!,
        })),
      });
    }
  }

  return groups.sort((a, b) => a.order - b.order);
}

/**
 * Generate navigation sections from routes
 */
function generateNavigationSections(
  routes: RouteDefinition[],
  configs: GroupConfig[]
): NavigationSection[] {
  const sections: NavigationSection[] = [];

  for (const config of configs) {
    const groupRoutes = routes
      .filter(r => r.metadata.group === config.name)
      .sort((a, b) => (a.metadata.order || 0) - (b.metadata.order || 0));

    if (groupRoutes.length > 0) {
      sections.push({
        title: config.title,
        items: groupRoutes.map(r => ({
          label: r.metadata.label,
          path: r.path,
        })),
      });
    }
  }

  return sections.sort((a, b) => {
    const orderA = configs.find(c => c.title === a.title)?.order || 0;
    const orderB = configs.find(c => c.title === b.title)?.order || 0;
    return orderA - orderB;
  });
}

// ─────────────────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────────────────

/**
 * Generate dashboard menu for PrivateLayout
 */
export function generateDashboardMenu(privateRoutes: PrivateRoutes): MenuGroup[] {
  return generateMenuGroups(privateRoutes.getAllRoutes(), [
    { name: 'main', title: 'Main', order: 1 },
    { name: 'trading', title: 'Trading', order: 2 },
    { name: 'system', title: 'System', order: 3 },
    { name: 'account', title: 'Account', order: 4 },
    { name: 'development', title: 'Development', order: 5 },
  ]);
}

/**
 * Generate public navigation for PublicLayout
 */
export function generatePublicNavigation(publicRoutes: PublicRoutes): NavigationSection[] {
  return generateNavigationSections(publicRoutes.getAllRoutes(), [
    { name: 'main', title: 'Home', order: 1 },
    { name: 'resources', title: 'Resources', order: 2 },
    { name: 'security', title: 'Security', order: 3 },
  ]);
}

/**
 * Generate footer navigation
 */
export function generateFooterNavigation(publicRoutes: PublicRoutes): NavigationSection[] {
  const allRoutes = publicRoutes.getAllRoutes();

  return [
    {
      title: 'Legal',
      items: allRoutes
        .filter(r => r.metadata.group === 'resources' || r.metadata.group === 'security')
        .sort((a, b) => {
          // Resources first, then security
          if (a.metadata.group !== b.metadata.group) {
            return a.metadata.group === 'resources' ? -1 : 1;
          }
          return (a.metadata.order || 0) - (b.metadata.order || 0);
        })
        .map(r => ({
          label: r.metadata.label,
          path: r.path,
        })),
    },
  ];
}
