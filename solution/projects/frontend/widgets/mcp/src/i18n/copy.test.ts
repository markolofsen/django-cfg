import { describe, expect, it } from 'vitest';

import { MCP_DICTIONARIES } from './index';

const locales = Object.keys(MCP_DICTIONARIES) as (keyof typeof MCP_DICTIONARIES)[];
const keys = Object.keys(MCP_DICTIONARIES.en.connect);

describe('connect copy', () => {
  it('ships English, Russian and every other locale with every key present and non-blank', () => {
    expect(locales).toEqual(expect.arrayContaining(['en', 'ru']));
    for (const locale of locales) {
      const connect = MCP_DICTIONARIES[locale].connect as unknown as Record<string, string>;
      for (const key of keys) expect(connect[key]?.trim(), `${locale}.${key}`).toBeTruthy();
      expect(Object.keys(connect).sort(), locale).toEqual([...keys].sort());
    }
  });

  it('translates the new screens (Russian differs from English)', () => {
    const en = MCP_DICTIONARIES.en.connect as unknown as Record<string, string>;
    const ru = MCP_DICTIONARIES.ru.connect as unknown as Record<string, string>;
    for (const key of ['otherApp', 'back', 'stepUrl1', 'stepCmd2', 'copyPrompt', 'promptBody']) {
      expect(ru[key], key).not.toBe(en[key]);
    }
  });

  it('keeps the same placeholders in every locale', () => {
    const holes = (text: string) => (text.match(/\{\w+\}/g) ?? []).sort().join();
    const en = MCP_DICTIONARIES.en.connect as unknown as Record<string, string>;
    for (const locale of locales) {
      const connect = MCP_DICTIONARIES[locale].connect as unknown as Record<string, string>;
      for (const key of ['stepUrl2', 'promptBody', 'promptKeyLine']) expect(holes(connect[key] ?? ''), `${locale}.${key}`).toBe(holes(en[key] ?? ''));
    }
  });

  it('translates the quick-connect strings in every locale (none is a copy of English)', () => {
    const quick = Object.keys(MCP_DICTIONARIES.en.connect).filter((k) => k.startsWith('quick') || k === 'view');
    expect(quick).toHaveLength(10);
    const en = MCP_DICTIONARIES.en.connect as unknown as Record<string, string>;
    for (const locale of locales.filter((l) => l !== 'en')) {
      const connect = MCP_DICTIONARIES[locale].connect as unknown as Record<string, string>;
      for (const key of quick) expect(connect[key], `${locale}.${key}`).not.toBe(en[key]);
    }
  });
});
