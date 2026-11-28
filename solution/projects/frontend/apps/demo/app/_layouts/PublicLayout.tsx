'use client';

import { ReactNode } from 'react';

import { settings } from '@core/settings';
import { routes } from '@routes/public';
import { privateRoutes } from '@routes/private';
import {
  FloatingNavbar,
  PublicLayout as PublicShell,
} from '@djangocfg/layouts';
import { useAppTranslations } from '@i18n';

import { Footer } from '@components/Footer';

/**
 * Public chrome for the demo, built on the real `@djangocfg/layouts` shell
 * rather than a hand-rolled navbar — so the drawer, the locale switcher and
 * the responsive overflow behaviour exercised here are the ones shipped to
 * consumers.
 *
 * Navigation maps to the demo's actual routes; the one nested section exists
 * so the drawer's parent/child density is observable at all.
 */
export function PublicLayout({ children }: { children: ReactNode }) {
  const { app } = useAppTranslations();

  return (
    <PublicShell
      navbar={
        <FloatingNavbar
          config={{
            brand: settings.app.name,
            brandHref: routes.home,
            // `brand-left` anchors the links to the brand. The `default` layout
            // centres them in the leftover space, which with a short menu on a
            // wide screen strands them mid-bar with a gulf on either side.
            navLayout: 'brand-left',
            // Reclaim the whole viewport while reading: the bar slides away on
            // scroll-down and snaps back the instant you scroll up.
            hideNavOnScroll: true,
            navigation: [
              { label: app('nav.home'), href: routes.home },
              {
                label: app('nav.dashboard'),
                href: privateRoutes.dashboard,
                items: [
                  { label: app('nav.settings'), href: privateRoutes.settings },
                ],
              },
              { label: app('nav.realtime'), href: routes.realtime },
              { label: 'Privacy', href: routes.legal.privacy },
              { label: 'Terms', href: routes.legal.terms },
              { label: app('nav.signIn'), href: routes.auth },
            ],
            controls: {
              showThemeSwitcher: true,
              showLocaleSwitcher: true,
            },
          }}
        />
      }
      footer={<Footer />}
    >
      {children}
    </PublicShell>
  );
}
