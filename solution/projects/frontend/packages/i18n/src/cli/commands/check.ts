/**
 * Check for missing translation keys
 */

import { defineCommand } from 'citty';
import { consola } from 'consola';
import * as path from 'node:path';
import {
  detectLocaleConfig,
  getDefaultLocalesDir,
  loadLocale,
  getAllKeys,
  getValueAtPath,
} from '../utils';

export const checkCommand = defineCommand({
  meta: {
    name: 'check',
    description: 'Find missing translation keys across locales',
  },
  args: {
    dir: {
      type: 'string',
      alias: 'd',
      description: 'Locales directory',
    },
    base: {
      type: 'string',
      alias: 'b',
      description: 'Base locale to compare against',
      default: 'en',
    },
    fix: {
      type: 'boolean',
      description: 'Show suggested fixes',
      default: false,
    },
  },
  async run({ args }) {
    const localesDir = args.dir
      ? path.resolve(process.cwd(), args.dir)
      : getDefaultLocalesDir();

    try {
      const config = detectLocaleConfig(localesDir);
      const baseLocale = args.base || 'en';

      if (!config.locales.includes(baseLocale)) {
        consola.error(`Base locale "${baseLocale}" not found.`);
        return;
      }

      consola.info(`Checking locales in ${localesDir}`);
      consola.info(`Base locale: ${baseLocale}`);
      consola.log('');

      // Load base locale
      const baseTranslations = await loadLocale(config, baseLocale);
      const baseKeys = getAllKeys(baseTranslations);

      let totalMissing = 0;
      const missingByLocale: Record<string, string[]> = {};

      // Check each locale
      for (const locale of config.locales) {
        if (locale === baseLocale) continue;

        const translations = await loadLocale(config, locale);
        const missing: string[] = [];

        for (const { path: keyPath } of baseKeys) {
          const value = getValueAtPath(translations, keyPath);
          if (value === undefined) {
            missing.push(keyPath);
          }
        }

        if (missing.length > 0) {
          missingByLocale[locale] = missing;
          totalMissing += missing.length;
        }
      }

      // Report
      if (totalMissing === 0) {
        consola.success('All locales have all keys!');
        return;
      }

      consola.warn(`Found ${totalMissing} missing keys`);
      consola.log('');

      for (const [locale, missing] of Object.entries(missingByLocale)) {
        consola.log(`${locale} (${missing.length} missing):`);
        for (const key of missing.slice(0, 10)) {
          consola.log(`  - ${key}`);
        }
        if (missing.length > 10) {
          consola.log(`  ... and ${missing.length - 10} more`);
        }
        consola.log('');
      }

      // Summary
      consola.box({
        title: 'Summary',
        message: [
          `Base: ${baseLocale} (${baseKeys.length} keys)`,
          `Checked: ${config.locales.length - 1} locales`,
          `Missing: ${totalMissing} total`,
        ].join('\n'),
      });
    } catch (error) {
      consola.error(error);
    }
  },
});
