import '@core/globals.css';

import { getMessages } from 'next-intl/server';
import '@fontsource-variable/plus-jakarta-sans';
import { notFound } from 'next/navigation';

import { settings } from '@core/settings';
import { AppLayout } from '@layouts/AppLayout';
import { I18nProvider } from '@djangocfg/nextjs/i18n/client';
import { generateLocaleParams, routing } from '@djangocfg/nextjs/i18n/routing';

import type { Messages } from '@djangocfg/nextjs/i18n';
import type { Metadata, Viewport } from 'next';
import type { ReactNode } from 'react';

import { supportedLocales } from '../../i18n/request';

export function generateStaticParams() {
  return generateLocaleParams(supportedLocales);
}

/**
 * `interactive-widget=resizes-content`: when the on-screen keyboard opens, the
 * *layout* viewport shrinks (rather than the visual viewport sliding over a
 * fixed layout). That keeps `visualViewport.height` — and our `--dvh` var, and
 * the navbar's fixed anchoring — honest on mobile. `viewport-fit=cover` lets
 * content extend under the notch / home indicator so `dvh` means the true edge.
 */
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  interactiveWidget: 'resizes-content',
};

interface LocaleLayoutProps {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}

export async function generateMetadata({ params }: LocaleLayoutProps): Promise<Metadata> {
  const { locale } = await params;
  return {
    metadataBase: settings.app.siteUrl ? new URL(settings.app.siteUrl) : undefined,
    title: {
      default: settings.app.name,
      template: `%s | ${settings.app.name}`,
    },
    description: settings.app.description,
    openGraph: {
      type: 'website',
      locale,
      siteName: settings.app.name,
    },
    robots: { index: true, follow: true },
  };
}

export default async function LocaleLayout({ children, params }: LocaleLayoutProps) {
  const { locale } = await params;

  if (!routing.locales.includes(locale)) {
    notFound();
  }

  const messages = (await getMessages()) as Messages;

  return (
    <html
      lang={locale}
      dir="ltr"
      suppressHydrationWarning
    >
      <body className="font-sans antialiased">
        <I18nProvider locale={locale} messages={messages} locales={[...supportedLocales]}>
          <AppLayout>{children}</AppLayout>
        </I18nProvider>
      </body>
    </html>
  );
}
