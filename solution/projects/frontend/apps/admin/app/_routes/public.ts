/**
 * Public Domain
 *
 * All public routes and navigation
 */

import { defineRoute, routesToMenuItems } from '@djangocfg/nextjs/navigation';

import type { MenuGroup, RouteDefinition, NavigationSection } from '@djangocfg/nextjs/navigation';

// ─────────────────────────────────────────────────────────────────────────
// Routes
// ─────────────────────────────────────────────────────────────────────────

export const home = defineRoute('/', {
  label: 'Home',
  description: 'Dashboard home',
  icon: 'LayoutDashboard',
  protected: false,
  group: 'main',
  order: 1,
});

export const adminDemo = defineRoute('/admin', {
  label: 'Admin Demo',
  description: 'Django-CFG admin integration demo',
  icon: 'LayoutDashboard',
  protected: false,
  group: 'demo',
  order: 1,
});

export const privateDemo = defineRoute('/private', {
  label: 'Private Demo',
  description: 'Protected area demo',
  icon: 'Lock',
  protected: false,
  group: 'demo',
  order: 2,
});

export const auth = defineRoute('/auth', {
  label: 'Sign In',
  description: 'User authentication',
  icon: 'LogIn',
  protected: false,
});

export const contact = defineRoute('/contact', {
  label: 'Contact',
  description: 'Get in touch with us',
  icon: 'Mail',
  protected: false,
  group: 'contact',
  order: 1,
});

export const privacy = defineRoute('/legal/privacy', {
  label: 'Privacy Policy',
  description: 'Privacy policy and data protection',
  icon: 'Shield',
  protected: false,
  group: 'legal',
  order: 1,
});

export const terms = defineRoute('/legal/terms', {
  label: 'Terms of Service',
  description: 'Terms and conditions',
  icon: 'FileText',
  protected: false,
  group: 'legal',
  order: 2,
});

export const cookies = defineRoute('/legal/cookies', {
  label: 'Cookie Policy',
  description: 'Cookie usage and preferences',
  icon: 'Cookie',
  protected: false,
  group: 'legal',
  order: 3,
});

export const security = defineRoute('/legal/security', {
  label: 'Security Policy',
  description: 'Security practices and policies',
  icon: 'Shield',
  protected: false,
  group: 'legal',
  order: 4,
});

// All routes as array
export const allRoutes: RouteDefinition[] = [
  home,
  adminDemo,
  privateDemo,
  auth,
  contact,
  privacy,
  terms,
  cookies,
  security,
];

// Routes object (for backwards compatibility)
export const routes = {
  home,
  adminDemo,
  privateDemo,
  auth,
  contact,
  privacy,
  terms,
  cookies,
  security,
  allRoutes,
};

// ─────────────────────────────────────────────────────────────────────────
// Navigation Generation
// ─────────────────────────────────────────────────────────────────────────

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
      title: 'Demo',
      items: getGroupItems('demo'),
    },
    {
      title: 'Contact',
      items: getGroupItems('contact'),
    },
  ].filter((s) => s.items.length > 0);
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
  ].filter((s) => s.items.length > 0);
}

// Helper
function getGroupItems(groupName: string) {
  return allRoutes
    .filter(
      (r) =>
        r.metadata.group === groupName &&
        (r.metadata.show === undefined || r.metadata.show === true)
    )
    .sort((a, b) => (a.metadata.order || 0) - (b.metadata.order || 0))
    .map((r) => ({ label: r.metadata.label, path: r.path }));
}

