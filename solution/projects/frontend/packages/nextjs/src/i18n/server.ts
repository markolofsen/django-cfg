/**
 * Server-side i18n Utilities
 *
 * For use in Server Components, Server Actions, and Route Handlers
 *
 * @example
 * ```tsx
 * // In a Server Component
 * import { getTranslations, getLocale } from '@djangocfg/nextjs/i18n/server';
 *
 * export default async function Page() {
 *   const t = await getTranslations('HomePage');
 *   const locale = await getLocale();
 *
 *   return <h1>{t('title')}</h1>;
 * }
 * ```
 */

import {
    getFormatter, getLocale as getNextIntlLocale, getMessages as getNextIntlMessages, getNow,
    getTimeZone, getTranslations as getNextIntlTranslations
} from 'next-intl/server';

import { generateLocaleParams, isValidLocale } from './routing';

import type { LocaleCode, Messages, LocaleParams } from './types';
// Re-export routing utilities for convenience
export { isValidLocale, generateLocaleParams };

// ─────────────────────────────────────────────────────────────────────────────
// Core Server Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Get translations for Server Components
 *
 * @example
 * ```tsx
 * const t = await getTranslations('HomePage');
 * return <h1>{t('title')}</h1>;
 *
 * // Or without namespace
 * const t = await getTranslations();
 * return <h1>{t('HomePage.title')}</h1>;
 * ```
 */
export async function getTranslations<Namespace extends string = never>(
  namespace?: Namespace
) {
  return getNextIntlTranslations(namespace);
}

/**
 * Get current locale in Server Components
 */
export async function getLocale(): Promise<LocaleCode> {
  return (await getNextIntlLocale()) as LocaleCode;
}

/**
 * Get all messages for the current request
 * Useful for passing to I18nProvider in layouts
 */
export async function getMessages(): Promise<Messages> {
  return (await getNextIntlMessages()) as Messages;
}

/**
 * Get current time for the request
 * Useful for consistent time-based formatting
 */
export { getNow };

/**
 * Get timezone for the request
 */
export { getTimeZone };

/**
 * Get formatter for dates, numbers, etc.
 */
export { getFormatter };

// ─────────────────────────────────────────────────────────────────────────────
// Locale Extraction Helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Extract locale from page/layout params
 *
 * @example
 * ```tsx
 * // app/[locale]/page.tsx
 * export default async function Page({ params }) {
 *   const locale = await getLocaleFromParams(params);
 *   // ...
 * }
 * ```
 */
export async function getLocaleFromParams(
  params: Promise<LocaleParams> | LocaleParams
): Promise<LocaleCode> {
  const resolved = await params;
  return resolved.locale as LocaleCode;
}

/**
 * Shorthand for getting locale from params
 * Alias for getLocaleFromParams
 */
export const extractLocale = getLocaleFromParams;

// ─────────────────────────────────────────────────────────────────────────────
// Typed Translation Helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Get typed translations for a specific namespace
 *
 * @example
 * ```tsx
 * const t = await getNamespacedTranslations('payments');
 * return <span>{t('balance.available')}</span>;
 * ```
 */
export async function getNamespacedTranslations(namespace: string) {
  return getNextIntlTranslations(namespace);
}

// ─────────────────────────────────────────────────────────────────────────────
// Metadata Helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Generate localized metadata for pages
 *
 * @example
 * ```tsx
 * // app/[locale]/about/page.tsx
 * import { generateLocalizedMetadata } from '@djangocfg/nextjs/i18n/server';
 *
 * export async function generateMetadata({ params }) {
 *   return generateLocalizedMetadata(params, {
 *     titleKey: 'AboutPage.meta.title',
 *     descriptionKey: 'AboutPage.meta.description',
 *   });
 * }
 * ```
 */
export async function generateLocalizedMetadata(
  params: Promise<LocaleParams> | LocaleParams,
  options: {
    titleKey?: string;
    descriptionKey?: string;
    namespace?: string;
  } = {}
) {
  const locale = await getLocaleFromParams(params);
  const t = await getTranslations(options.namespace);

  return {
    title: options.titleKey ? t(options.titleKey as never) : undefined,
    description: options.descriptionKey ? t(options.descriptionKey as never) : undefined,
    // Add locale to alternate languages
    alternates: {
      languages: {
        [locale]: `/${locale}`,
      },
    },
  };
}
