import './_core/globals.css';

import { Manrope } from 'next/font/google';
import type { Metadata } from 'next';
import { AppLayout } from '@layouts/AppLayout';
import { settings } from '@core/settings';
import { generateMetadata } from '@core/metadata';

import { AIChatWidget } from '@djangocfg/layouts/snippets';

// Base metadata - will be inherited by all pages
// Pages can override with their own generateMetadata call
export const metadata: Metadata = generateMetadata({
  title: {
    default: settings.app.name,
    template: `%s | ${settings.app.name}`,
  },
  description: settings.app.description,
});

const manrope = Manrope({
  subsets: ['latin', 'cyrillic'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-manrope',
  display: 'swap',
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning className="dark">
      <body className={manrope.className} style={{ fontFamily: manrope.style.fontFamily }}>
        <AppLayout>
          {children}
        </AppLayout>
        <AIChatWidget />
      </body>
    </html>
  );
}

