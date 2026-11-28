/**
 * i18n Module for Next.js App Router
 *
 * IMPORTANT: This module only exports types and non-React utilities.
 * For React components and hooks, use subpath imports:
 *
 * - `@djangocfg/nextjs/i18n/client` - I18nProvider, hooks (use client)
 * - `@djangocfg/nextjs/i18n/routing` - routing, createRouting, generateLocaleParams
 * - `@djangocfg/nextjs/i18n/server` - getMessages, getLocale
 * - `@djangocfg/nextjs/i18n/navigation` - Link, redirect, usePathname, useRouter
 * - `@djangocfg/nextjs/i18n/proxy` - createProxy
 * - `@djangocfg/nextjs/i18n/request` - createRequestConfig
 * - `@djangocfg/nextjs/i18n/components` - LocaleSwitcher
 *
 * @example
 * ```tsx
 * // app/[locale]/layout.tsx
 * import { I18nProvider } from '@djangocfg/nextjs/i18n/client';
 * import { routing, generateLocaleParams } from '@djangocfg/nextjs/i18n/routing';
 * import { getMessages } from 'next-intl/server';
 *
 * // proxy.ts
 * import { routing } from '@djangocfg/nextjs/i18n/routing';
 *
 * // i18n/request.ts
 * import { createRequestConfig } from '@djangocfg/nextjs/i18n/request';
 * ```
 */

// ─────────────────────────────────────────────────────────────────────────────
// Types only - safe to import anywhere
// ─────────────────────────────────────────────────────────────────────────────

export type {
  I18nConfig,
  I18nPluginOptions,
  I18nProviderProps,
  Messages,
  MessagesLoader,
  ExtensionMessages,
  LocaleParams,
  LocaleLayoutProps,
  LocalePageProps,
  LocaleCode,
  I18nTranslations,
} from './types';

export type { LinkProps } from './navigation';
export type { RequestConfigOptions } from './request';
export type { LocaleSwitcherProps } from './components';

export { sharedCookieDomain, localeCookieHeader, expireHostOnlyLocaleCookie, LOCALE_COOKIE } from './shared-locale';
