/**
 * Public Layout
 * 
 * Simple layout for public pages (home, docs, contact, legal pages)
 * Uses routes from @/_routes
 */

'use client';

import { ReactNode } from 'react';
import { PublicLayout as BasePublicLayout, type NavigationItem as BaseNavigationItem, type FooterConfig } from '@djangocfg/layouts';
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
  
  const footer: FooterConfig = {
    links: {
      privacy: routes.public.privacy.path,
      terms: routes.public.terms.path,
      security: routes.public.security.path,
      cookies: routes.public.cookies.path,
      docs: settings.links.docsUrl,
    },
    // copyright will be auto-generated from siteName
  };
  
  const userMenu = {
    profilePath: routes.user.profile.path,
    dashboardPath: routes.user.home.path,
    authPath: routes.public.auth.path,
  };
  
  return (
    <BasePublicLayout
      logo={settings.app.icons.logoVector}
      siteName={settings.app.name}
      navigation={navigation}
      footer={footer}
      userMenu={userMenu}
    >
      {children}
    </BasePublicLayout>
  );
}

