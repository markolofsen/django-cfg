/**
 * i18n Request Configuration
 *
 * Merges base translations from @djangocfg/i18n with admin-specific translations
 * @see https://next-intl.dev/docs/getting-started/app-router
 */

import { getRequestConfig } from 'next-intl/server';

import { en as baseEn, ko as baseKo, ru as baseRu } from '@djangocfg/i18n/locales';
import { mergeTranslations } from '@djangocfg/i18n/utils';

import { type AdminTranslations, en as adminEn, ko as adminKo, ru as adminRu } from './locales';

// Type for admin namespace
type AdminNamespace = { admin: AdminTranslations };

// Merge base translations with admin-specific translations under 'admin' namespace
const locales = {
  en: mergeTranslations<AdminNamespace>(baseEn, { admin: adminEn }),
  ru: mergeTranslations<AdminNamespace>(baseRu, { admin: adminRu }),
  ko: mergeTranslations<AdminNamespace>(baseKo, { admin: adminKo }),
} as const;

type LocaleKey = keyof typeof locales;

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  // Validate and fallback to default
  if (!locale || !(locale in locales)) {
    locale = 'en';
  }

  return {
    locale,
    messages: locales[locale as LocaleKey],
    timeZone: 'UTC',
  };
});
