/**
 * Navigation Types
 *
 * Common types used for route definitions and navigation
 */

import type { LucideIcon } from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────────
// Route Types
// ─────────────────────────────────────────────────────────────────────────

export interface RouteMetadata {
  label: string;
  description?: string;
  icon?: LucideIcon | string;
  /** Shown on sidebar menu items when set */
  badge?: string | number;
  protected: boolean;
  group?: string;
  order?: number;
  show?: boolean;
  // Extension mapping (for dynamic filtering based on API response)
  extensionName?: string;
  // SEO
  priority?: number; // Sitemap priority 0.0-1.0
  changefreq?: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
  noindex?: boolean; // Exclude from sitemap
}

export interface RouteDefinition {
  path: string;
  metadata: RouteMetadata;
}

// ─────────────────────────────────────────────────────────────────────────
// Navigation Group Types (for horizontal tabs with labels)
// ─────────────────────────────────────────────────────────────────────────

export interface NavGroup {
  /** Unique group identifier (matches RouteMetadata.group) */
  id: string;
  /** Display label for the group */
  label: string;
  /** Sort order */
  order: number;
  /** If true, group is only shown when it has items (e.g., extensions) */
  dynamic?: boolean;
}

export interface NavGroupWithRoutes extends NavGroup {
  /** Routes in this group (populated at runtime) */
  routes: RouteDefinition[];
}

// ─────────────────────────────────────────────────────────────────────────
// Menu Types
// ─────────────────────────────────────────────────────────────────────────

export interface MenuItem {
  path: string;
  label: string;
  icon: LucideIcon | string;
  badge?: string | number;
}

export interface MenuGroup {
  label: string;
  order: number;
  items: MenuItem[];
}

// ─────────────────────────────────────────────────────────────────────────
// Navigation Types
// ─────────────────────────────────────────────────────────────────────────

export interface NavigationItem {
  label: string;
  path: string;
}

export interface NavigationSection {
  title: string;
  items: NavigationItem[];
}

// ─────────────────────────────────────────────────────────────────────────
// Breadcrumb Types
// ─────────────────────────────────────────────────────────────────────────

export interface BreadcrumbItem {
  label: string;
  path: string;
  isActive: boolean;
}

