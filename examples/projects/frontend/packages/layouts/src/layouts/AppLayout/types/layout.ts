/**
 * Layout Configuration Types
 */

import type { ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';
import type { NavigationSection, DashboardMenuGroup } from './navigation';

/**
 * Public layout configuration
 */
export interface PublicLayoutConfig {
  navigation: {
    homePath: string;
    menuSections: NavigationSection[];
  };
  userMenu: {
    dashboardPath?: string;
    profilePath: string;
  };
  footer: {
    badge: {
      icon: LucideIcon;
      text: string;
    };
    links: {
      docs?: string;
      privacy?: string;
      terms?: string;
      security?: string;
      cookies?: string;
    };
    menuSections: NavigationSection[];
  };
}

/**
 * Private/Dashboard layout configuration
 */
export interface PrivateLayoutConfig {
  homeHref: string;
  profileHref: string;
  showChat?: boolean;
  menuGroups: DashboardMenuGroup[];
  contentPadding?: 'default' | 'none';
  headerActions?: ReactNode;
}
