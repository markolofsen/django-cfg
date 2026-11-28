/**
 * Add translation key to all locales
 */

import { defineCommand } from 'citty';
import { consola } from 'consola';
import * as path from 'node:path';
import {
  detectLocaleConfig,
  getDefaultLocalesDir,
  readLocaleFile,
  writeLocaleFile,
  getValueAtPath,
  setValueAtPath,
  renderTsLocale,
  loadLocale,
} from '../utils';

export const addCommand = defineCommand({
  meta: {
    name: 'add',
    description: 'Add a translation key to all locales',
  },
  args: {
    key: {
      type: 'positional',
      description: 'Key path (e.g., "tools.tour.next")',
      required: true,
    },
    translations: {
      type: 'positional',
      description: 'JSON object with translations (e.g., \'{"en":"Next","ru":"Далее"}\')',
      required: true,
    },
    dir: {
      type: 'string',
      alias: 'd',
      description: 'Locales directory',
    },
    force: {
      type: 'boolean',
      alias: 'f',
      description: 'Overwrite existing keys',
      default: false,
    },
  },
  async run({ args }) {
    const localesDir = args.dir
      ? path.resolve(process.cwd(), args.dir)
      : getDefaultLocalesDir();

    try {
      const config = detectLocaleConfig(localesDir);
      const keyPath = args.key;

      // Parse translations
      let translations: Record<string, string>;
      try {
        translations = JSON.parse(args.translations);
      } catch {
        consola.error('Invalid JSON for translations');
        consola.log('Example: \'{"en":"Next","ru":"Далее"}\'');
        return;
      }

      consola.info(`Adding key: ${keyPath}`);
      consola.info(`Directory: ${localesDir}`);
      consola.log('');

      let updated = 0;
      let skipped = 0;

      for (const locale of config.locales) {
        const translation = translations[locale];

        if (!translation) {
          consola.warn(`  ${locale}: No translation provided, skipping`);
          skipped++;
          continue;
        }

        // Check if key exists
        const existing = await loadLocale(config, locale);
        const existingValue = getValueAtPath(existing, keyPath);

        if (existingValue !== undefined && !args.force) {
          consola.warn(`  ${locale}: Key exists, use --force to overwrite`);
          skipped++;
          continue;
        }

        // Read and update file
        const { content, exportName } = readLocaleFile(config, locale);

        if (config.fileExtension === '.json') {
          const json = JSON.parse(content);
          setValueAtPath(json, keyPath, translation);
          writeLocaleFile(config, locale, JSON.stringify(json, null, 2));
        } else {
          // `existing` is the same file, already parsed by `loadLocale` above
          // for the key-exists check. Editing that object and re-serialising is
          // what makes nested keys work: the old text-splicing path inserted a
          // duplicate parent block and lost its siblings.
          setValueAtPath(existing, keyPath, translation);
          writeLocaleFile(config, locale, renderTsLocale(content, exportName, existing));
        }

        consola.success(`  ${locale}: Added "${translation}"`);
        updated++;
      }

      consola.log('');
      consola.box({
        title: 'Result',
        message: `Updated: ${updated}, Skipped: ${skipped}`,
      });
    } catch (error) {
      consola.error(error);
    }
  },
});
