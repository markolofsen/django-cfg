/**
 * i18n Request Configuration for Server Components
 *
 * Provides translations to server components via next-intl's request scope
 *
 * @example
 * ```ts
 * // i18n/request.ts in your app
 * import { createRequestConfig } from '@djangocfg/nextjs/i18n';
 * import { en, ru, ko } from '@djangocfg/i18n';
 *
 * export default createRequestConfig({
 *   locales: { en, ru, ko },
 * });
 * ```
 */

import { getRequestConfig } from 'next-intl/server';

import { en, ko, mergeTranslations, ru } from '@djangocfg/i18n';

import { routing } from './routing';

import type { I18nTranslations, LocaleCode } from '@djangocfg/i18n';
import type { Messages } from './types';
// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export interface RequestConfigOptions {
  /** Base locale translations from @djangocfg/i18n */
  locales?: Record<LocaleCode, I18nTranslations>;
  /** Extension i18n instances to merge */
  extensions?: Array<{
    namespace: string;
    locales: Record<string, Record<string, unknown>>;
  }>;
  /** Custom message loader (overrides locales) */
  loadMessages?: (locale: LocaleCode) => Promise<Messages> | Messages;
  /** Time zone for date/time formatting */
  timeZone?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Locales
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_LOCALES: Record<LocaleCode, I18nTranslations> = {
  en,
  ru,
  ko,
};

// ─────────────────────────────────────────────────────────────────────────────
// Message Loading
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Load and merge messages for a locale
 */
function loadMessages(
  locale: LocaleCode,
  options: RequestConfigOptions
): Messages {
  // Get base translations
  const locales = options.locales ?? DEFAULT_LOCALES;
  const baseMessages = locales[locale] ?? locales.en ?? en;

  // If no extensions, return base
  if (!options.extensions?.length) {
    return baseMessages as Messages;
  }

  // Merge extension translations
  let mergedMessages = { ...baseMessages } as Messages;

  for (const extension of options.extensions) {
    const extMessages = extension.locales[locale] ?? extension.locales.en;
    if (extMessages) {
      mergedMessages = mergeTranslations(mergedMessages, {
        [extension.namespace]: extMessages,
      }) as Messages;
    }
  }

  return mergedMessages;
}

// ─────────────────────────────────────────────────────────────────────────────
// Request Config Factory
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create request configuration for next-intl
 *
 * This is used in your app's `i18n/request.ts` file
 *
 * @example
 * ```ts
 * // i18n/request.ts
 * import { createRequestConfig } from '@djangocfg/nextjs/i18n';
 *
 * // `extensions` merges extra namespaced translation bundles, each shaped
 * // as `{ namespace: string, locales: Record<LocaleCode, Messages> }`.
 * export default createRequestConfig({
 *   extensions: [myFeatureI18n],
 * });
 * ```
 */
export function createRequestConfig(options: RequestConfigOptions = {}) {
  return getRequestConfig(async ({ requestLocale }) => {
    // Get locale from request or default
    let locale = await requestLocale;

    // Validate and fallback to default
    if (!locale || !routing.locales.includes(locale as LocaleCode)) {
      locale = routing.defaultLocale;
    }

    // Load messages
    const messages = options.loadMessages
      ? await options.loadMessages(locale as LocaleCode)
      : loadMessages(locale as LocaleCode, options);

    return {
      locale,
      messages,
      timeZone: options.timeZone ?? 'UTC',
    };
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Export
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Default request config with base @djangocfg/i18n translations
 * Can be used directly if no extensions are needed
 */
export default createRequestConfig();
