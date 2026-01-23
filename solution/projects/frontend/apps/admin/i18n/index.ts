/**
 * Admin i18n exports
 *
 * Provides type-safe translation utilities for the admin app.
 * Admin translations are namespaced under 'admin.' prefix.
 *
 * @example
 * ```tsx
 * import { useAppTranslations } from '@i18n';
 *
 * function MyComponent() {
 *   const { t, admin } = useAppTranslations();
 *   return (
 *     <>
 *       <span>{t('ui.form.save')}</span>     // Base translations
 *       <span>{admin('nav.home')}</span>     // Admin translations
 *     </>
 *   );
 * }
 * ```
 */

'use client';

import { useTranslations } from 'next-intl';
import { useCallback, useMemo } from 'react';

import type { AdminTranslations } from './locales';

export { adminLocales, type AdminTranslations, type AdminLocaleKey } from './locales';

/**
 * Admin namespace for translations
 */
export const ADMIN_NAMESPACE = 'admin' as const;

/**
 * Type-safe admin translation keys
 */
type PathKeys<T, Prefix extends string = ''> = T extends string
  ? Prefix
  : T extends object
    ? {
        [K in keyof T & string]: PathKeys<T[K], Prefix extends '' ? K : `${Prefix}.${K}`>;
      }[keyof T & string]
    : never;

export type AdminTranslationKeys = PathKeys<AdminTranslations>;

/**
 * Consolidated hook for all app translations
 *
 * Returns both base translations (t) and admin-specific translations (admin)
 *
 * @example
 * ```tsx
 * const { t, admin } = useAppTranslations();
 *
 * t('ui.form.save');          // Base: "Save"
 * t('ui.select.placeholder'); // Base: "Select..."
 *
 * admin('nav.home');          // Admin: "Home" / "Главная" / "홈"
 * admin('pages.home.title');  // Admin: "Welcome"
 * ```
 */
export function useAppTranslations() {
  const baseT = useTranslations();
  const adminT = useTranslations(ADMIN_NAMESPACE);

  const admin = useCallback(
    (key: AdminTranslationKeys, params?: Record<string, string | number>) => {
      return adminT(key as string, params);
    },
    [adminT]
  );

  return useMemo(
    () => ({
      /** Base translations from @djangocfg/i18n (ui.*, layouts.*, api.*) */
      t: baseT,
      /** Admin-specific translations (nav.*, pages.*, common.*) */
      admin,
    }),
    [baseT, admin]
  );
}

/**
 * Type-safe hook for admin translations only
 *
 * @example
 * ```tsx
 * const t = useAdminT();
 * t('nav.home');           // Returns translation for 'admin.nav.home'
 * t('pages.home.title');   // Returns translation for 'admin.pages.home.title'
 * ```
 */
export function useAdminT() {
  const t = useTranslations(ADMIN_NAMESPACE);

  return useCallback(
    (key: AdminTranslationKeys, params?: Record<string, string | number>) => {
      return t(key as string, params);
    },
    [t]
  );
}

/**
 * Type-safe hook for admin translations with namespace access
 *
 * @example
 * ```tsx
 * const t = useAdminNamespace('pages.home');
 * t('title');    // Returns translation for 'admin.pages.home.title'
 * t('subtitle'); // Returns translation for 'admin.pages.home.subtitle'
 * ```
 */
export function useAdminNamespace<NS extends string>(namespace: NS) {
  const t = useTranslations(`${ADMIN_NAMESPACE}.${namespace}`);
  return t;
}

/**
 * Translate route label
 *
 * Routes store translation keys in metadata.label.
 * This hook returns a function to translate those keys.
 *
 * @example
 * ```tsx
 * const tRoute = useRouteLabel();
 * const label = tRoute(routes.admin.dashboard.metadata.label); // "Dashboard"
 * ```
 */
export function useRouteLabel() {
  const t = useTranslations(ADMIN_NAMESPACE);

  return useCallback(
    (labelKey: string) => {
      return t(labelKey as string);
    },
    [t]
  );
}
