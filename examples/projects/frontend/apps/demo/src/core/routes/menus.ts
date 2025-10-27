/**
 * Menu Generation
 *
 * All menu generation logic in one place
 */

import type { LucideIcon } from 'lucide-react';
import type { NavigationSection } from '@djangocfg/layouts';
import type { PublicRoutes, PrivateRoutes, LegalRoutes, RouteDefinition } from './definitions';

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
      .filter(r => r.metadata.group === config.name && r.metadata.icon && r.metadata.show !== false)
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
      .filter(r => r.metadata.group === config.name && r.metadata.show !== false)
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
    { name: 'account', title: 'Account', order: 2 },
    { name: 'developer', title: 'Developer', order: 3 },
  ]);
}

/**
 * Generate public navigation for PublicLayout
 */
export function generatePublicNavigation(publicRoutes: PublicRoutes, documentationUrl?: string): NavigationSection[] {
  const sections = generateNavigationSections(publicRoutes.getAllRoutes(), [
    { name: 'main', title: 'Home', order: 1 },
    { name: 'admin', title: 'Admin', order: 2 },
    { name: 'components', title: 'Components', order: 3 },
    { name: 'legal', title: 'Legal', order: 4 },
    { name: 'debug', title: 'Debug', order: 5 },
  ]);

  // Add external documentation link if provided (after Admin, before Components)
  if (documentationUrl) {
    sections.splice(2, 0, {
      title: 'Docs',
      items: [
        {
          label: 'Documentation',
          path: documentationUrl,
        },
      ],
    });
  }

  return sections;
}

/**
 * Generate footer navigation
 */
export function generateFooterNavigation(publicRoutes: PublicRoutes, legalRoutes: LegalRoutes, documentationUrl?: string): NavigationSection[] {
  const legalItems = legalRoutes.getAllRoutes();

  return [
    {
      title: 'Product',
      items: [
        { label: 'Home', path: publicRoutes.home },
        { label: 'Django Admin', path: publicRoutes.admin },
        { label: 'UI Components', path: publicRoutes.ui },
      ],
    },
    {
      title: 'Resources',
      items: [
        ...(documentationUrl ? [{ label: 'Documentation', path: documentationUrl }] : []),
        { label: 'Debug Tools', path: publicRoutes.debug },
      ],
    },
    {
      title: 'Legal',
      items: legalItems
        .filter(r => r.metadata.show !== false)
        .sort((a, b) => (a.metadata.order || 0) - (b.metadata.order || 0))
        .map(r => ({
          label: r.metadata.label,
          path: r.path,
        })),
    },
    {
      title: 'Company',
      items: [
        { label: 'About', path: publicRoutes.home },
        { label: 'Sign In', path: publicRoutes.auth },
      ],
    },
  ];
}
