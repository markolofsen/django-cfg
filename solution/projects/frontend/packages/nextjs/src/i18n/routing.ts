/**
 * i18n Routing Configuration
 *
 * Creates routing configuration for next-intl
 * Used by proxy and navigation components
 */

import { defineRouting } from 'next-intl/routing';

import { LOCALE_COOKIE_MAX_AGE } from './shared-locale';

import type { I18nConfig, LocaleCode } from './types';

// ─────────────────────────────────────────────────────────────────────────────
// Default Configuration
// ─────────────────────────────────────────────────────────────────────────────

export const DEFAULT_LOCALES: LocaleCode[] = ['en', 'ru', 'ko', 'ja', 'de', 'fr', 'zh', 'it', 'es', 'nl', 'ar', 'tr', 'pt-BR', 'pl', 'sv', 'no', 'da'];
export const DEFAULT_LOCALE: LocaleCode = 'en';

// ─────────────────────────────────────────────────────────────────────────────
// Routing Factory
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create routing configuration for next-intl
 *
 * @example
 * ```ts
 * // i18n/routing.ts
 * import { createRouting } from '@djangocfg/nextjs/i18n';
 *
 * export const routing = createRouting({
 *   locales: ['en', 'ru', 'ko'],
 *   defaultLocale: 'en',
 * });
 * ```
 */
export function createRouting(config?: Partial<I18nConfig>) {
  const locales = config?.locales ?? DEFAULT_LOCALES;
  const defaultLocale = config?.defaultLocale ?? DEFAULT_LOCALE;
  const localePrefix = config?.localePrefix ?? 'as-needed';

  return defineRouting({
    locales,
    defaultLocale,
    localePrefix,
    // next-intl 4 writes a session cookie: a closed browser forgot the reader's choice. Apps that call next-intl's
    // `createMiddleware` directly (not `createProxy`) get the year too.
    localeCookie: { maxAge: LOCALE_COOKIE_MAX_AGE },
  });
}

/**
 * Default routing configuration
 * Can be overridden by app-specific configuration
 */
export const routing = createRouting();

// ─────────────────────────────────────────────────────────────────────────────
// Locale Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Check if a locale is supported
 */
export function isValidLocale(
  locale: string,
  supportedLocales: readonly string[] = DEFAULT_LOCALES
): locale is LocaleCode {
  return supportedLocales.includes(locale as LocaleCode);
}

/**
 * Get locale from params (handles async params in Next.js 15+)
 */
export async function getLocaleFromParams(
  params: Promise<{ locale: string }> | { locale: string }
): Promise<LocaleCode> {
  const resolved = await params;
  return resolved.locale as LocaleCode;
}

/**
 * Generate static params for all locales
 * Use in generateStaticParams for locale pages
 */
export function generateLocaleParams(locales: readonly string[] = DEFAULT_LOCALES) {
  return locales.map((locale) => ({ locale }));
}
