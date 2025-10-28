import type { AppProps } from 'next/app';
import type { ReactElement, ReactNode } from 'react';
import type { NextPage } from 'next';
import { Inter } from 'next/font/google';

// Import global styles (includes Tailwind v4, UI package, and layouts)
import '@/styles/globals.css';

import { AppLayout } from '@djangocfg/layouts';
import { appLayoutConfig } from '@/core';
import { AppProviders } from '@/contexts';

// Load Manrope font from Google Fonts
const inter = Inter({
  subsets: ['latin', 'cyrillic'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-inter',
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
 * Single AppLayout wrapper with Django CFG admin mode enabled
 * All layout and iframe logic handled automatically by AppLayout
 */
export default function App({ Component, pageProps }: AppPropsWithLayout) {
  // Check if page has custom layout
  const hasCustomLayout = !!Component.getLayout;

  return (
    <AppProviders>
      <AppLayout
        config={appLayoutConfig}
        fontFamily={inter.style.fontFamily}
        forceLayout="admin"
      >
        {hasCustomLayout ? (
          Component.getLayout!(<Component {...pageProps} />)
        ) : (
          <Component {...pageProps} />
        )}
      </AppLayout>
    </AppProviders>
  );
}
