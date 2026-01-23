/**
 * Admin Layout
 *
 * Layout for admin dashboard pages
 * Uses routes from @/_routes with group support
 */

'use client';

import { ReactNode } from 'react';

import {
    AdminLayout as BaseAdminLayout, HeaderConfig, SidebarConfig, SidebarGroupConfig
} from '@djangocfg/layouts';
import { adminMenuGroups, routes } from '@routes/index';

import type { I18nLayoutConfig } from '@djangocfg/layouts';

interface AdminLayoutProps {
  children: ReactNode;
  i18n?: I18nLayoutConfig;
}

/**
 * Convert MenuGroup[] to SidebarConfig with groups
 */
function convertMenuGroupsToSidebar(menuGroups: Array<{ label: string; items: Array<{ path: string; label: string; icon?: string | any; badge?: string | number }>; dynamic?: boolean }>): SidebarConfig {
  const groups: SidebarGroupConfig[] = menuGroups
    .filter(group => group.items.length > 0 || !group.dynamic)
    .map(group => ({
      label: group.label,
      items: group.items
        .filter(item => item.path && item.path !== 'undefined')
        .map(item => ({
          label: item.label,
          href: item.path || '#',
          icon: typeof item.icon === 'string' ? item.icon : item.icon?.name || undefined,
          badge: item.badge,
        })),
      dynamic: group.dynamic,
    }));

  return {
    homeHref: routes.admin.overview?.path || '/admin',
    groups,
  };
}

/**
 * Admin Layout Component
 * 
 * Wrapper around base AdminLayout from @djangocfg/layouts
 * Converts routes to layout props
 */
export function AdminLayout({ children, i18n }: AdminLayoutProps) {
  const sidebarMenu = convertMenuGroupsToSidebar(adminMenuGroups);

  const header: HeaderConfig = {
    title: 'Admin Dashboard',
  };

  return (
    <BaseAdminLayout
      sidebar={sidebarMenu}
      header={header}
      contentPadding="default"
      i18n={i18n}
    >
      {children}
    </BaseAdminLayout>
  );
}

