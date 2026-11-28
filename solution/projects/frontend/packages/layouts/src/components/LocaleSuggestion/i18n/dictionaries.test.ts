import { join } from 'node:path';
import { checkDictionaries } from '@djangocfg/i18n/copy/testing';
import { describe, expect, it } from 'vitest';

import { LOCALE_SUGGESTION_DICTIONARIES } from './index';
import { en } from './locales/en';

describe('locale suggestion dictionaries', () => {
  it('covers every locale, file, key and placeholder', () => {
    expect(checkDictionaries(LOCALE_SUGGESTION_DICTIONARIES, join(import.meta.dirname, 'locales'))).toEqual([]);
  });

  it('is translated, not a copy of English', () => {
    const same = Object.entries(LOCALE_SUGGESTION_DICTIONARIES)
      .filter(([locale]) => locale !== 'en')
      .flatMap(([locale, copy]) =>
        (Object.keys(en) as (keyof typeof en)[])
          .filter((key) => copy[key] === en[key])
          .map((key) => `${locale}.${key}`),
      );
    expect(same).toEqual([]);
  });

  it('resolves pt-BR to Portuguese', () => {
    expect(LOCALE_SUGGESTION_DICTIONARIES['pt-BR'].dismiss).toBe('Fechar');
  });
});
