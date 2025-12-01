/**
 * Admin Layout
 * 
 * Layout for admin dashboard pages
 * Uses routes from @/_routes
 */

'use client';

import { ReactNode } from 'react';
import { AdminLayout as BaseAdminLayout, type SidebarItem, type SidebarConfig, type HeaderConfig } from '@djangocfg/layouts';
import { routes, adminMenuGroups } from '@routes/index';

interface AdminLayoutProps {
  children: ReactNode;
}

/**
 * Convert MenuGroup[] to SidebarConfig
 */
function convertMenuGroupsToSidebar(menuGroups: Array<{ label: string; items: Array<{ path: string; label: string; icon?: string | any; badge?: string | number }> }>): SidebarConfig {
  return {
    homeHref: routes.admin.overview?.path || '/admin',
    items: menuGroups.flatMap(group => 
      group.items
        .filter(item => item.path && item.path !== 'undefined') // Filter out invalid paths
        .map(item => ({
          label: item.label,
          href: item.path || '#', // Fallback to '#' if path is invalid
          icon: typeof item.icon === 'string' ? item.icon : item.icon?.name || undefined,
          badge: item.badge,
        }))
    ),
  };
}

/**
 * Admin Layout Component
 * 
 * Wrapper around base AdminLayout from @djangocfg/layouts
 * Converts routes to layout props
 */
export function AdminLayout({ children }: AdminLayoutProps) {
  const sidebarMenu = convertMenuGroupsToSidebar(adminMenuGroups);
  
  const header: HeaderConfig = {
    title: 'Admin Dashboard',
    profilePath: routes.user.profile.path,
  };
  
  return (
    <BaseAdminLayout
      sidebar={sidebarMenu}
      header={header}
      contentPadding="default"
    >
      {children}
    </BaseAdminLayout>
  );
}

