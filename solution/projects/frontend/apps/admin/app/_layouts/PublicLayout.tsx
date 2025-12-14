/**
 * Public Layout
 * 
 * Simple layout for public pages (home, docs, contact, legal pages)
 * Uses routes from @/_routes
 */

'use client';

import { ReactNode } from 'react';
import { PublicLayout as BasePublicLayout, type NavigationItem as BaseNavigationItem, type UserMenuConfig } from '@djangocfg/layouts';
import { routes, generatePublicNavigation } from '@routes/index';
import { settings } from '@core/settings';

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
      logo={settings.app.icons.logoVector}
      siteName={settings.app.name}
      navigation={navigation}
      userMenu={userMenu}
    >
      {children}
    </BasePublicLayout>
  );
}

