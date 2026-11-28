import { join } from 'node:path';

import { checkDictionaries } from '@djangocfg/i18n/copy/testing';
import { describe, expect, it } from 'vitest';

import { MCP_DICTIONARIES } from './index';

/** `tsc` holds the keys; this holds what typing cannot: registration, blanks and placeholders. */
describe('MCP dictionaries', () => {
  it('covers every locale, every file, every key and placeholder', () => {
    expect(checkDictionaries(MCP_DICTIONARIES, join(import.meta.dirname, 'locales'))).toEqual([]);
  });
});
