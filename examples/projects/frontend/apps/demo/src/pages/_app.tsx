import type { AppProps } from 'next/app';
import type { ReactElement, ReactNode } from 'react';
import type { NextPage } from 'next';
import { Manrope } from 'next/font/google';

// Import global styles (includes Tailwind v4, UI package, and layouts)
import '@/styles/globals.css';

import { AppLayout } from '@djangocfg/layouts';
import { appLayoutConfig } from '@/core';
import { AppProviders, PrivateProvider } from '@/contexts';

// Load Manrope font from Google Fonts
const manrope = Manrope({
  subsets: ['latin', 'cyrillic'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-manrope',
  display: 'swap',
});

// Add support for per-page layouts
export type NextPageWithLayout<P = {}, IP = P> = NextPage<P, IP> & {
  getLayout?: (page: ReactElement) => ReactNode;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};



/**
 * Next.js App Component
 *
 * Single AppLayout wrapper - that's it!
 * All layout logic handled automatically by AppLayout
 */
export default function App({ Component, pageProps }: AppPropsWithLayout) {
  // Check if page has custom layout
  const hasCustomLayout = !!Component.getLayout;

  return (
    <AppProviders>
      <AppLayout
        config={appLayoutConfig}
        disableLayout={false}
        fontFamily={manrope.style.fontFamily}
        showPackageVersions={true}
      >
        {hasCustomLayout ? (
          Component.getLayout!(<Component {...pageProps} />)
        ) : (
          <PrivateProvider>
            <Component {...pageProps} />
          </PrivateProvider>
        )}
      </AppLayout>
    </AppProviders>
  );
}
