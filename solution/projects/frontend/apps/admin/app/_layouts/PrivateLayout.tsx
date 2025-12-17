/**
 * Private Layout
 * 
 * Layout for authenticated user pages
 * Uses routes from @/_routes
 */

'use client';

import { ReactNode } from 'react';

import {
    HeaderConfig, PrivateLayout as BasePrivateLayout, SidebarConfig, SidebarItem
} from '@djangocfg/layouts';
import { menuGroups, routes } from '@routes/index';

interface PrivateLayoutProps {
  children: ReactNode;
}

/**
 * Convert MenuGroup[] to SidebarConfig
 */
function convertMenuGroupsToSidebar(menuGroups: Array<{ label: string; items: Array<{ path: string; label: string; icon?: string | any; badge?: string | number }> }>): SidebarConfig {
  return {
    homeHref: routes.private.home.path,
    items: menuGroups.flatMap(group => 
      group.items.map(item => ({
        label: item.label,
        href: item.path,
        icon: typeof item.icon === 'string' ? item.icon : item.icon?.name || undefined,
        badge: item.badge,
      }))
    ),
  };
}

/**
 * Private Layout Component
 * 
 * Wrapper around base PrivateLayout from @djangocfg/layouts
 * Converts routes to layout props
 */
export function PrivateLayout({ children }: PrivateLayoutProps) {
  const sidebarMenu = convertMenuGroupsToSidebar(menuGroups);
  
  const header: HeaderConfig = {
    title: 'Dashboard',
  };
  
  return (
    <BasePrivateLayout
      sidebar={sidebarMenu}
      header={header}
      contentPadding="default"
    >
      {children}
    </BasePrivateLayout>
  );
}

