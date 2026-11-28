/**
 * i18n Plugin for Next.js Configuration
 *
 * Wraps next-intl plugin for use with createBaseNextConfig
 *
 * @example
 * ```ts
 * // next.config.ts
 * import { createBaseNextConfig } from '@djangocfg/nextjs/config';
 *
 * export default createBaseNextConfig({
 *   i18n: {
 *     locales: ['en', 'ru', 'ko'],
 *     defaultLocale: 'en',
 *   },
 * });
 * ```
 */

import createNextIntlPlugin from 'next-intl/plugin';

import type { NextConfig } from 'next';
import type { I18nPluginOptions } from './types';

export type { I18nPluginOptions } from './types';

// ─────────────────────────────────────────────────────────────────────────────
// Plugin Factory
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create next-intl plugin wrapper
 *
 * @param options - i18n configuration options
 * @returns Next.js config wrapper function
 */
export function createI18nPlugin(options?: I18nPluginOptions) {
  // Determine request config path
  const requestConfigPath = options?.requestConfig
    ?? './i18n/request.ts';

  // Create next-intl plugin
  const withNextIntl = createNextIntlPlugin(requestConfigPath);

  return withNextIntl;
}

/**
 * Apply i18n plugin to Next.js config
 *
 * @param config - Base Next.js config
 * @param options - i18n options
 * @returns Modified Next.js config
 */
export function withI18n(
  config: NextConfig,
  options?: I18nPluginOptions
): NextConfig {
  const plugin = createI18nPlugin(options);
  return plugin(config);
}

// ─────────────────────────────────────────────────────────────────────────────
// Export for direct use
// ─────────────────────────────────────────────────────────────────────────────

export { createNextIntlPlugin };
