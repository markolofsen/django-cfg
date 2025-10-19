/**
 * Navigation Types
 */

import type { LucideIcon } from 'lucide-react';

/**
 * Navigation menu item
 */
export interface NavigationItem {
  label: string;
  path: string;
}

/**
 * Navigation menu section
 */
export interface NavigationSection {
  title: string;
  items: NavigationItem[];
}

/**
 * Dashboard menu item with icon
 */
export interface DashboardMenuItem {
  path: string;
  label: string;
  icon: LucideIcon;
  badge?: string | number;
  subItems?: DashboardMenuItem[]; // Support nested menu items
}

/**
 * Dashboard menu group
 */
export interface DashboardMenuGroup {
  label: string;
  order: number;
  items: DashboardMenuItem[];
}
