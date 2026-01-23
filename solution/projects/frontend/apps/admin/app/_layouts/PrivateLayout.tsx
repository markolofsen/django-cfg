/**
 * Private Layout
 *
 * Layout for authenticated user pages
 * Uses routes from @/_routes with group support
 */

'use client';

import { ReactNode } from 'react';

import {
    HeaderConfig, PrivateLayout as BasePrivateLayout, SidebarConfig, SidebarGroupConfig
} from '@djangocfg/layouts';
import { menuGroups, routes } from '@routes/index';

import type { I18nLayoutConfig } from '@djangocfg/layouts';

interface PrivateLayoutProps {
  children: ReactNode;
  i18n?: I18nLayoutConfig;
}

/**
 * Convert MenuGroup[] to SidebarConfig with groups
 */
function convertMenuGroupsToSidebar(menuGroups: Array<{ label: string; items: Array<{ path: string; label: string; icon?: string | any; badge?: string | number }> }>): SidebarConfig {
  return {
    homeHref: routes.private.home.path,
    groups: menuGroups.map(group => ({
      label: group.label,
      items: group.items.map(item => ({
        label: item.label,
        href: item.path,
        icon: typeof item.icon === 'string' ? item.icon : item.icon?.name || undefined,
        badge: item.badge,
      })),
    })),
  };
}

/**
 * Private Layout Component
 * 
 * Wrapper around base PrivateLayout from @djangocfg/layouts
 * Converts routes to layout props
 */
export function PrivateLayout({ children, i18n }: PrivateLayoutProps) {
  const sidebarMenu = convertMenuGroupsToSidebar(menuGroups);

  const header: HeaderConfig = {
    title: 'Dashboard',
  };

  return (
    <BasePrivateLayout
      sidebar={sidebarMenu}
      header={header}
      contentPadding="default"
      i18n={i18n}
    >
      {children}
    </BasePrivateLayout>
  );
}

