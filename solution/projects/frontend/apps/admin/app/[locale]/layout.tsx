import '@core/globals.css';

import { getMessages } from 'next-intl/server';
import { Manrope } from 'next/font/google';
import { notFound } from 'next/navigation';

import { generateMetadata } from '@core/metadata';
import { settings } from '@core/settings';
import { I18nProvider } from '@djangocfg/nextjs/i18n/client';
import { generateLocaleParams, routing } from '@djangocfg/nextjs/i18n/routing';
import { AppLayout } from '@layouts/AppLayout';

import type { Messages } from '@djangocfg/nextjs/i18n';
import type { Metadata } from 'next';
import type { ReactNode } from 'react';

// Generate static params for all locales
export function generateStaticParams() {
  return generateLocaleParams();
}

// Base metadata - will be inherited by all pages
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

interface LocaleLayoutProps {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}

export default async function LocaleLayout({
  children,
  params,
}: LocaleLayoutProps) {
  const { locale } = await params;

  // Validate locale
  if (!routing.locales.includes(locale)) {
    notFound();
  }

  const messages = await getMessages() as Messages;

  return (
    <html lang={locale} dir="ltr" suppressHydrationWarning className="dark">
      <body className={manrope.className} style={{ fontFamily: manrope.style.fontFamily }}>
        <I18nProvider locale={locale} messages={messages}>
          <AppLayout>
            {children}
          </AppLayout>
        </I18nProvider>
      </body>
    </html>
  );
}
