/**
 * Public Layout
 * 
 * Simple layout for public pages (home, docs, contact, legal pages)
 * Uses routes from @/_routes
 */

'use client';

import { ReactNode } from 'react';

import { settings } from '@core/settings';
import {
    NavigationItem as BaseNavigationItem, PublicLayout as BasePublicLayout, UserMenuConfig
} from '@djangocfg/layouts';
import { generatePublicNavigation, routes } from '@routes/index';

interface PublicLayoutProps {
  children: ReactNode;
}

/**
 * Convert NavigationSection[] to flat NavigationItem[]
 */
function convertNavigationSections(sections: Array<{ title: string; items: Array<{ label: string; path: string }> }>): BaseNavigationItem[] {
  return sections.flatMap(section => 
    section.items.map(item => ({
      label: item.label,
      href: item.path,
    }))
  );
}

/**
 * Public Layout Component
 * 
 * Wrapper around base PublicLayout from @djangocfg/layouts
 * Converts routes to layout props
 */
export function PublicLayout({ children }: PublicLayoutProps) {
  const publicNavSections = generatePublicNavigation();

  const navigation: BaseNavigationItem[] = convertNavigationSections(publicNavSections);

  const userMenu: UserMenuConfig = {
    groups: [
      {
        title: 'Cabinet',
        items: [
          { label: 'Profile', href: routes.private.profile.path },
          { label: 'Dashboard', href: routes.private.home.path },
        ],
      },
    ],
    authPath: routes.public.auth.path,
  };

  return (
    <BasePublicLayout
      logo={settings.app.media.logoVector}
      siteName={settings.app.name}
      navigation={navigation}
      userMenu={userMenu}
    >
      {children}
    </BasePublicLayout>
  );
}

