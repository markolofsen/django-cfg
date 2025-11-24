/**
 * Shared Types
 *
 * Common types used across all route domains
 */

import type { LucideIcon } from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────────
// Route Types
// ─────────────────────────────────────────────────────────────────────────

export interface RouteMetadata {
  label: string;
  description?: string;
  icon?: LucideIcon;
  protected: boolean;
  group?: string;
  order?: number;
  show?: boolean;
}

export interface RouteDefinition {
  path: string;
  metadata: RouteMetadata;
}

// ─────────────────────────────────────────────────────────────────────────
// Menu Types
// ─────────────────────────────────────────────────────────────────────────

export interface MenuItem {
  path: string;
  label: string;
  icon: LucideIcon;
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
