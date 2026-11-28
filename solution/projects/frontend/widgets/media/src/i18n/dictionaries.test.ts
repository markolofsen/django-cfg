import { join } from 'node:path';

import { checkDictionaries } from '@djangocfg/i18n/copy/testing';
import { describe, expect, it } from 'vitest';

import { MEDIA_DICTIONARIES } from './index';

describe('media dictionaries', () => {
  it('covers every locale, every file, every key and placeholder', () => {
    expect(checkDictionaries(MEDIA_DICTIONARIES, join(import.meta.dirname, 'locales'))).toEqual([]);
  });
});
