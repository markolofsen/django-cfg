/**
 * Type-safe translation helpers for the demo app.
 *
 * @example
 *   const { t, app } = useAppTranslations();
 *   t('ui.form.save');   // base translation
 *   app('nav.home');     // app translation
 */

import { useTranslations } from 'next-intl';

import type { AppTranslations } from './locales';

type AppNamespacedKey<T, P extends string = ''> = {
  [K in keyof T]: T[K] extends Record<string, unknown>
    ? AppNamespacedKey<T[K], `${P}${K & string}.`>
    : `${P}${K & string}`;
}[keyof T];

export type AppTranslationKey = AppNamespacedKey<AppTranslations>;

export function useAppTranslations() {
  const t = useTranslations();
  const app = useTranslations('app');
  return { t, app: app as (key: AppTranslationKey) => string };
}
