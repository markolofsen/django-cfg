/**
 * Client-side i18n Hooks
 *
 * For use in Client Components ('use client')
 *
 * @example
 * ```tsx
 * 'use client';
 *
 * import { useTranslations, useLocale } from '@djangocfg/nextjs/i18n/client';
 *
 * export function MyComponent() {
 *   const t = useTranslations('HomePage');
 *   const locale = useLocale();
 *
 *   return <h1>{t('title')}</h1>;
 * }
 * ```
 */

'use client';

import {
    useFormatter, useLocale as useNextIntlLocale, useMessages, useNow, useTimeZone,
    useTranslations as useNextIntlTranslations
} from 'next-intl';

import { usePathname } from './navigation';
import { I18nProvider, NextIntlProvider, useDeclaredLocales } from './provider';
import { routing } from './routing';
import { expireHostOnlyLocaleCookie, localeCookieHeader, sharedCookieDomain } from './shared-locale';

// Re-export providers
export { I18nProvider, NextIntlProvider };

import type { LocaleCode } from './types';

// ─────────────────────────────────────────────────────────────────────────────
// Core Client Hooks
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Get translations in Client Components
 *
 * @example
 * ```tsx
 * const t = useTranslations('HomePage');
 * return <h1>{t('title')}</h1>;
 *
 * // With interpolation
 * return <p>{t('greeting', { name: 'John' })}</p>;
 * ```
 */
export function useTranslations<Namespace extends string = never>(
  namespace?: Namespace
) {
  return useNextIntlTranslations(namespace);
}

/**
 * Get current locale in Client Components
 */
export function useLocale(): LocaleCode {
  return useNextIntlLocale() as LocaleCode;
}

/**
 * Get all messages
 * Useful for passing to child providers
 */
export { useMessages };

/**
 * Get current time
 */
export { useNow };

/**
 * Get timezone
 */
export { useTimeZone };

/**
 * Get formatter for dates, numbers, etc.
 */
export { useFormatter };

// ─────────────────────────────────────────────────────────────────────────────
// Convenience Hooks
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Shorthand for useTranslations
 * Alias for compatibility with @djangocfg/i18n
 */
export const useT = useTranslations;

/**
 * Get namespaced translations
 *
 * @example
 * ```tsx
 * const pt = useNamespacedTranslations('payments');
 * return <span>{pt('balance.available')}</span>;
 * ```
 */
export function useNamespacedTranslations(namespace: string) {
  return useNextIntlTranslations(namespace);
}

// ─────────────────────────────────────────────────────────────────────────────
// Formatting Hooks
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Format a date according to locale
 *
 * @example
 * ```tsx
 * const formatDate = useDateFormatter();
 * return <span>{formatDate(new Date())}</span>;
 * ```
 */
export function useDateFormatter() {
  const formatter = useFormatter();
  return (date: Date | number, options?: Parameters<typeof formatter.dateTime>[1]) =>
    formatter.dateTime(date, options);
}

/**
 * Format a number according to locale
 *
 * @example
 * ```tsx
 * const formatNumber = useNumberFormatter();
 * return <span>{formatNumber(1234.56)}</span>;
 * ```
 */
export function useNumberFormatter() {
  const formatter = useFormatter();
  return (number: number, options?: Parameters<typeof formatter.number>[1]) =>
    formatter.number(number, options);
}

/**
 * Format relative time
 *
 * @example
 * ```tsx
 * const formatRelative = useRelativeTimeFormatter();
 * return <span>{formatRelative(new Date())}</span>;
 * ```
 */
export function useRelativeTimeFormatter() {
  const formatter = useFormatter();
  return (date: Date | number, options?: Parameters<typeof formatter.relativeTime>[1]) =>
    formatter.relativeTime(date, options);
}

// ─────────────────────────────────────────────────────────────────────────────
// Locale Switching Hooks
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Locales the app declared on `I18nProvider`; the built-in routing list only
 * when it declared none.
 *
 * @example
 * ```tsx
 * const locales = useLocales();
 * // ['en', 'ru', 'ko']
 * ```
 */
export function useLocales(): LocaleCode[] {
  const declared = useDeclaredLocales();
  return declared ?? (routing.locales as LocaleCode[]);
}

/**
 * Get default locale from routing config
 */
export function useDefaultLocale(): LocaleCode {
  return routing.defaultLocale as LocaleCode;
}

/**
 * Hook to change current locale
 *
 * @example
 * ```tsx
 * const changeLocale = useChangeLocale();
 *
 * <button onClick={() => changeLocale('ru')}>
 *   Switch to Russian
 * </button>
 * ```
 */
export function useChangeLocale() {
  const pathname = usePathname();

  return (locale: LocaleCode) => {
    // Set NEXT_LOCALE so middleware remembers the choice, on the registrable domain so every host of the family
    // reads it (see ./shared-locale); the host-only twin is expired so it cannot shadow the shared one.
    const secure = window.location.protocol === 'https:';
    const domain = sharedCookieDomain(window.location.hostname, process.env.NEXT_PUBLIC_COOKIE_DOMAIN);
    document.cookie = localeCookieHeader(locale, domain, secure);
    if (domain) document.cookie = expireHostOnlyLocaleCookie(secure);

    // Hard navigation to force full page reload with new locale
    // (ensures server components re-render with updated translations)
    window.location.href = `/${locale}${pathname}`;
  };
}

/**
 * Combined hook for locale switching
 * Returns current locale, available locales, and change function
 *
 * @example
 * ```tsx
 * const { locale, locales, changeLocale } = useLocaleSwitcher();
 *
 * <select value={locale} onChange={(e) => changeLocale(e.target.value)}>
 *   {locales.map(l => <option key={l} value={l}>{l}</option>)}
 * </select>
 * ```
 */
export function useLocaleSwitcher() {
  const locale = useLocale();
  const locales = useLocales();
  const changeLocale = useChangeLocale();

  return { locale, locales, changeLocale };
}
