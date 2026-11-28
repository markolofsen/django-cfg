'use client';

import { ReactNode, useMemo } from 'react';

import {
  PrivateLayout as BasePrivateLayout,
  type HeaderConfig,
  type SidebarConfig,
} from '@djangocfg/layouts';
import { usePathname } from '@djangocfg/nextjs/i18n/navigation';

import { settings } from '@core/settings';
import { routes } from '@routes/public';
import { privateRoutes } from '@routes/private';
import { useAppTranslations } from '@i18n';

/**
 * Demo cabinet shell — a thin config wrapper over the production
 * `BasePrivateLayout` from `@djangocfg/layouts` (grouped sidebar, header,
 * account footer, built-in auth guard). Same pattern every real `@djangocfg/*`
 * Next.js app uses; page-specific content sits inside `(pages)/private/*`.
 */
export function PrivateLayout({ children }: { children: ReactNode }) {
  const { app } = useAppTranslations();
  const pathname = usePathname();

  const sidebar = useMemo<SidebarConfig>(
    () => ({
      homeHref: privateRoutes.dashboard,
      activeIndicator: 'rail',
      groupLabelStyle: 'uppercase',
      groups: [
        {
          label: 'Overview',
          items: [
            {
              label: app('nav.dashboard'),
              href: privateRoutes.dashboard,
              icon: 'LayoutDashboard',
              tooltip: app('nav.dashboard'),
            },
            {
              label: app('nav.settings'),
              href: privateRoutes.settings,
              icon: 'Settings',
              tooltip: app('nav.settings'),
            },
          ],
        },
      ],
    }),
    [app],
  );

  // Account footer = dropdown menu (`'menu'`) with account links + the built-in
  // locale/theme controls and sign-out. `groups` are the app-provided links.
  const header = useMemo<HeaderConfig>(
    () => ({
      title: settings.app.name,
      brandIcon: 'Boxes',
      authPath: routes.auth,
      accountAction: 'menu',
      groups: [
        {
          items: [
            { label: app('nav.dashboard'), href: privateRoutes.dashboard },
            { label: app('nav.settings'), href: privateRoutes.settings },
          ],
        },
      ],
    }),
    [app],
  );

  return (
    <BasePrivateLayout
      sidebar={sidebar}
      header={header}
      pathname={pathname}
      visual={{ variant: 'boxed', inset: 12, radius: '2xl', border: true }}
    >
      {children}
    </BasePrivateLayout>
  );
}
