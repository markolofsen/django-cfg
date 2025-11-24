import type { AppProps } from 'next/app';
import { Inter } from 'next/font/google';

// Import global styles (includes Tailwind v4, UI package, and layouts)
import '@/styles/globals.css';

import { AppLayout, type PageWithLayout } from '@djangocfg/layouts';
import { appLayoutConfig } from '@/core';
import { CentrifugoProvider, CentrifugoMonitorFAB } from '@djangocfg/centrifugo';

// Load Inter font from Google Fonts
const inter = Inter({
  subsets: ['latin', 'cyrillic'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-inter',
  display: 'swap',
});

type AppPropsWithLayout = AppProps & {
  Component: PageWithLayout;
};

/**
 * Next.js App Component
 *
 * Smart AppLayout automatically handles:
 * - component.getLayout (custom layouts)
 * - component.layoutMode (force specific layout)
 * - Automatic route-based detection
 *
 * Just pass component and pageProps - AppLayout does the rest!
 */
export default function App({ Component, pageProps }: AppPropsWithLayout) {
  // AppLayout handles getLayout automatically - just render the page
  const getLayout = Component.getLayout ?? ((page) => page);

  return (
    <AppLayout
      config={appLayoutConfig}
      component={Component}
      pageProps={pageProps}
      fontFamily={inter.style.fontFamily}
    >
      <CentrifugoProvider enabled={true} autoConnect={true}>
        {getLayout(<Component {...pageProps} />)}
      </CentrifugoProvider>
    </AppLayout>
  );
}
