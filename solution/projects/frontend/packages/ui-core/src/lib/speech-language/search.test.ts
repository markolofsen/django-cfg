import { describe, expect, it } from 'vitest';

import { expandQueryLayouts, matchesLanguageQuery } from './search';
import { buildLanguageRows } from './languages';

const russian = buildLanguageRows().find((r) => r.tag === 'ru-RU')!;
const english = buildLanguageRows().find((r) => r.tag === 'en-US')!;

describe('expandQueryLayouts', () => {
  it('includes the query itself, lowercased', () => {
    expect(expandQueryLayouts('RUS')).toContain('rus');
  });

  it('maps QWERTY keys to ЙЦУКЕН', () => {
    // h-e-c-c on EN keys = р-у-с-с on the RU layout.
    expect(expandQueryLayouts('hecc')).toContain('русс');
  });

  it('maps ЙЦУКЕН characters to QWERTY', () => {
    // кгы typed on RU layout while meaning r-u-s.
    expect(expandQueryLayouts('кгы')).toContain('rus');
  });

  it('returns nothing for a blank query', () => {
    expect(expandQueryLayouts('   ')).toEqual([]);
  });
});

describe('matchesLanguageQuery — every spelling finds Русский', () => {
  it('native prefix «рус»', () => {
    expect(matchesLanguageQuery(russian.search, 'рус')).toBe(true);
  });

  it('english prefix "rus"', () => {
    expect(matchesLanguageQuery(russian.search, 'rus')).toBe(true);
  });

  it('full english name "russian"', () => {
    expect(matchesLanguageQuery(russian.search, 'russian')).toBe(true);
  });

  it('wrong layout "hecc" (=русс on EN keys)', () => {
    expect(matchesLanguageQuery(russian.search, 'hecc')).toBe(true);
  });

  it('wrong layout «утпдшыр» (=english on RU keys)', () => {
    expect(matchesLanguageQuery(english.search, 'утпдшыр')).toBe(true);
  });

  it('tag and iso match too', () => {
    expect(matchesLanguageQuery(russian.search, 'ru-RU')).toBe(true);
    expect(matchesLanguageQuery(english.search, 'en')).toBe(true);
  });

  it('does not match unrelated rows', () => {
    expect(matchesLanguageQuery(english.search, 'русск')).toBe(false);
  });

  it('empty query matches everything (no filter)', () => {
    expect(matchesLanguageQuery(russian.search, '')).toBe(true);
  });
});
