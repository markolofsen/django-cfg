#!/usr/bin/env node
/**
 * i18n CLI - Unified tool for managing translations
 *
 * Usage:
 *   pnpm i18n list [pattern]     - List/search keys
 *   pnpm i18n check              - Find missing keys
 *   pnpm i18n add <key> <json>   - Add key to all locales
 *
 * Can work with:
 *   - Package locales (default): packages/i18n/src/locales
 *   - App locales: --dir apps/studio/i18n/locales
 */

import { defineCommand, runMain } from 'citty';
import { consola } from 'consola';

import { listCommand } from './commands/list';
import { checkCommand } from './commands/check';
import { addCommand } from './commands/add';

const main = defineCommand({
  meta: {
    name: 'i18n',
    version: '1.0.0',
    description: 'CLI for managing i18n translations',
  },
  subCommands: {
    list: listCommand,
    check: checkCommand,
    add: addCommand,
  },
  setup() {
    consola.box('i18n CLI');
  },
});

runMain(main);
