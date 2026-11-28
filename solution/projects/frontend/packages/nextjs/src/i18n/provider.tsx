/**
 * i18n Provider for Next.js App Router
 *
 * Bridges next-intl with @djangocfg/i18n
 * Provides translations to both Server and Client components
 *
 * @example
 * ```tsx
 * // app/[locale]/layout.tsx
 * import { I18nProvider } from '@djangocfg/nextjs/i18n';
 * import { getMessages, getLocale } from '@djangocfg/nextjs/i18n/server';
 *
 * export default async function LocaleLayout({ children, params }) {
 *   const locale = await getLocale(params);
 *   const messages = await getMessages();
 *
 *   return (
 *     <I18nProvider locale={locale} messages={messages}>
 *       {children}
 *     </I18nProvider>
 *   );
 * }
 * ```
 */

'use client';

import { createContext, useContext } from 'react';
import { NextIntlClientProvider } from 'next-intl';
import { I18nProvider as DjangoCfgI18nProvider } from '@djangocfg/i18n';
import type { I18nProviderProps, LocaleCode } from './types';

const DeclaredLocalesContext = createContext<LocaleCode[] | null>(null);

/** Locales the app passed to its provider, or null when it passed none. */
export const useDeclaredLocales = (): LocaleCode[] | null => useContext(DeclaredLocalesContext);

// ─────────────────────────────────────────────────────────────────────────────
// Provider Component
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Unified i18n Provider
 *
 * Wraps both NextIntlClientProvider and @djangocfg/i18n's I18nProvider
 * This ensures both next-intl hooks and @djangocfg/i18n hooks work correctly
 */
export function I18nProvider({
  locale,
  messages,
  locales,
  timeZone = 'UTC',
  now,
  children,
}: I18nProviderProps) {
  return (
    <NextIntlClientProvider
      locale={locale}
      messages={messages}
      timeZone={timeZone}
      now={now}
    >
      <DjangoCfgI18nProvider
        locale={locale as LocaleCode}
        translations={messages}
      >
        <DeclaredLocalesContext.Provider value={locales ?? null}>
          {children}
        </DeclaredLocalesContext.Provider>
      </DjangoCfgI18nProvider>
    </NextIntlClientProvider>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Lightweight Provider (next-intl only)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Next-intl only provider (without @djangocfg/i18n context)
 * Use if you only need next-intl hooks
 */
export function NextIntlProvider({
  locale,
  messages,
  locales,
  timeZone = 'UTC',
  now,
  children,
}: I18nProviderProps) {
  return (
    <NextIntlClientProvider
      locale={locale}
      messages={messages}
      timeZone={timeZone}
      now={now}
    >
      <DeclaredLocalesContext.Provider value={locales ?? null}>
        {children}
      </DeclaredLocalesContext.Provider>
    </NextIntlClientProvider>
  );
}
