/**
 * List/search translation keys
 */

import { defineCommand } from 'citty';
import { consola } from 'consola';
import * as path from 'node:path';
import {
  detectLocaleConfig,
  getDefaultLocalesDir,
  loadLocale,
  getAllKeys,
} from '../utils';

export const listCommand = defineCommand({
  meta: {
    name: 'list',
    description: 'List and search translation keys',
  },
  args: {
    pattern: {
      type: 'positional',
      description: 'Search pattern (optional)',
      required: false,
    },
    dir: {
      type: 'string',
      alias: 'd',
      description: 'Locales directory',
    },
    locale: {
      type: 'string',
      alias: 'l',
      description: 'Locale to inspect (default: en)',
      default: 'en',
    },
    values: {
      type: 'boolean',
      alias: 'v',
      description: 'Show values',
      default: false,
    },
  },
  async run({ args }) {
    const localesDir = args.dir
      ? path.resolve(process.cwd(), args.dir)
      : getDefaultLocalesDir();

    try {
      const config = detectLocaleConfig(localesDir);
      const locale = args.locale || 'en';

      if (!config.locales.includes(locale)) {
        consola.error(`Locale "${locale}" not found. Available: ${config.locales.join(', ')}`);
        return;
      }

      consola.info(`Loading ${locale} from ${localesDir}`);
      const translations = await loadLocale(config, locale);
      const allKeys = getAllKeys(translations);

      // Filter by pattern
      const pattern = args.pattern?.toLowerCase();
      const filtered = pattern
        ? allKeys.filter(
            (k) =>
              k.path.toLowerCase().includes(pattern) ||
              String(k.value).toLowerCase().includes(pattern)
          )
        : allKeys;

      // Display
      consola.log('');
      consola.info(`Found ${filtered.length} keys${pattern ? ` matching "${pattern}"` : ''}`);
      consola.log('');

      for (const { path: keyPath, value } of filtered) {
        if (args.values) {
          consola.log(`  ${keyPath}: ${JSON.stringify(value)}`);
        } else {
          consola.log(`  ${keyPath}`);
        }
      }

      consola.log('');
      consola.info(`Total: ${filtered.length} / ${allKeys.length} keys`);
    } catch (error) {
      consola.error(error);
    }
  },
});
