/**
 * i18n Request Configuration
 *
 * Merges base translations from @djangocfg/i18n with app-specific
 * translations under the `app` namespace. The demo ships en/ru/ko;
 * the framework supports more — add the locale here + a matching file
 * under `./locales/` to enable it.
 */

import { getRequestConfig } from 'next-intl/server';

import { en as baseEn, ko as baseKo, ru as baseRu } from '@djangocfg/i18n/locales';
import { mergeTranslations } from '@djangocfg/i18n/utils';

import { AppTranslations, en as appEn, ko as appKo, ru as appRu } from './locales';

type AppNamespace = { app: AppTranslations };

const locales = {
  en: mergeTranslations<AppNamespace>(baseEn, { app: appEn }),
  ru: mergeTranslations<AppNamespace>(baseRu, { app: appRu }),
  ko: mergeTranslations<AppNamespace>(baseKo, { app: appKo }),
} as const;

type LocaleKey = keyof typeof locales;

export const supportedLocales = ['en', 'ru', 'ko'] as const;
export type SupportedLocale = (typeof supportedLocales)[number];

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  if (!locale || !(locale in locales)) {
    locale = 'en';
  }

  return {
    locale,
    messages: locales[locale as LocaleKey],
    timeZone: 'UTC',
  };
});
