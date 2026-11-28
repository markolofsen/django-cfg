import { describe, expect, it } from 'vitest';

import {
  decideSuggestion,
  dismissPair,
  emptyMemory,
  isAutomated,
  isExcludedPath,
  matchSiteLocale,
  MAX_PAIRS,
  reconcileMemory,
  suggestLocale,
} from './decide';

const DAY = 24 * 60 * 60 * 1000;
const NOW = Date.UTC(2026, 10, 14);
const SITE = ['en', 'ru', 'de', 'pt-BR'];

const decide = (over: Partial<Parameters<typeof decideSuggestion>[0]> = {}) =>
  decideSuggestion({ browserLanguages: ['de'], siteLocales: SITE, current: 'en', memory: emptyMemory(), now: NOW, ...over });

describe('matchSiteLocale', () => {
  it.each([
    ['de', 'de', true],
    ['DE', 'de', true],
    ['pt-br', 'pt-BR', true],
    ['de-AT', 'de', false],
    ['pt', 'pt-BR', false],
    ['pt-PT', 'pt-BR', false],
    ['nb', null, false],
    ['fi', null, false],
    ['', null, false],
  ])('%s -> %s', (tag, locale, exact) => {
    const hit = matchSiteLocale(tag, SITE);
    expect(hit?.locale ?? null).toBe(locale);
    if (hit) expect(hit.exact).toBe(exact);
  });

  it('maps nb and nn to the site no', () => {
    expect(matchSiteLocale('nb-NO', ['en', 'no'])?.locale).toBe('no');
    expect(matchSiteLocale('nn', ['en', 'no'])?.locale).toBe('no');
  });

  it('never turns Traditional Chinese into Simplified', () => {
    expect(matchSiteLocale('zh-TW', ['en', 'zh-CN'])).toBeNull();
    expect(matchSiteLocale('zh', ['en', 'zh-CN'])?.locale).toBe('zh-CN');
  });
});

describe('suggestLocale', () => {
  it('offers the first browser language the site speaks', () => {
    expect(decide()).toBe('de');
    expect(decide({ browserLanguages: ['fi', 'ru', 'de'] })).toBe('ru');
  });

  it('says nothing when the top supported language is already the page', () => {
    expect(decide({ browserLanguages: ['en', 'de'] })).toBeNull();
    expect(decide({ browserLanguages: ['fi', 'en', 'de'] })).toBeNull();
  });

  it('says nothing when the site has none of the browser languages', () => {
    expect(decide({ browserLanguages: ['fi', 'sv'] })).toBeNull();
    expect(decide({ browserLanguages: [] })).toBeNull();
  });

  it('says nothing for a one-language site', () => {
    expect(decide({ siteLocales: ['en'], current: 'en' })).toBeNull();
    expect(decide({ siteLocales: [], current: 'en' })).toBeNull();
  });

  it('maps a regional browser tag to the site language (de-AT -> de)', () => {
    expect(decide({ browserLanguages: ['de-AT'] })).toBe('de');
  });

  it('does not interrupt for a regional variant of the page language', () => {
    expect(decide({ browserLanguages: ['en-GB'] })).toBeNull();
    expect(decide({ browserLanguages: ['pt-PT'], current: 'pt-BR' })).toBeNull();
  });

  it('offers a regional variant the site itself has', () => {
    const site = ['en-US', 'en-GB', 'ru'];
    expect(suggestLocale({ browserLanguages: ['en-GB'], siteLocales: site, current: 'en-US' })).toBe('en-GB');
  });
});

describe('memory', () => {
  it('a dismissed pair stays silent', () => {
    const memory = dismissPair(emptyMemory(), 'de', 'en', NOW);
    expect(decide({ memory, now: NOW + DAY })).toBeNull();
  });

  it('a dismissal is per pair: another current locale or another browser language asks again', () => {
    const memory = dismissPair(emptyMemory(), 'de', 'en', NOW);
    expect(decide({ memory, current: 'ru' })).toBe('de');
    expect(decide({ memory, browserLanguages: ['ru'] })).toBe('ru');
  });

  it('a dismissal expires after the ttl', () => {
    const memory = dismissPair(emptyMemory(), 'de', 'en', NOW);
    expect(decide({ memory, now: NOW + 179 * DAY })).toBeNull();
    expect(decide({ memory, now: NOW + 181 * DAY })).toBe('de');
    expect(decide({ memory, now: NOW + 8 * DAY, ttlDays: 7 })).toBe('de');
  });

  it('records the locale shown; the first visit closes nothing', () => {
    const next = reconcileMemory(emptyMemory(), { current: 'en', candidate: 'de', now: NOW });
    expect(next).toEqual({ v: 1, seen: 'en', dismissed: {} });
  });

  it('a locale change by the visitor counts as consent', () => {
    // Was on en, now on ru while the browser prefers de: they picked ru, do not nag.
    const next = reconcileMemory({ v: 1, seen: 'en', dismissed: {} }, { current: 'ru', candidate: 'de', now: NOW });
    expect(next.dismissed['de>ru']).toBe(NOW);
    expect(decide({ memory: next, current: 'ru' })).toBeNull();
  });

  it('staying on the same locale closes nothing', () => {
    const next = reconcileMemory({ v: 1, seen: 'en', dismissed: {} }, { current: 'en', candidate: 'de', now: NOW });
    expect(next.dismissed).toEqual({});
  });

  it('drops expired pairs and keeps the newest MAX_PAIRS', () => {
    const dismissed: Record<string, number> = { 'old>x': NOW - 400 * DAY };
    for (let i = 0; i < MAX_PAIRS + 5; i += 1) dismissed[`p${i}>x`] = NOW - i * 1000;
    const next = reconcileMemory({ v: 1, seen: 'en', dismissed }, { current: 'en', candidate: null, now: NOW });
    expect(Object.keys(next.dismissed)).toHaveLength(MAX_PAIRS);
    expect(next.dismissed['old>x']).toBeUndefined();
    expect(next.dismissed['p0>x']).toBe(NOW);
  });
});

describe('guards', () => {
  it('recognises crawlers and automation', () => {
    expect(isAutomated('Mozilla/5.0 (compatible; Googlebot/2.1)', false)).toBe(true);
    expect(isAutomated('HeadlessChrome/120', false)).toBe(true);
    expect(isAutomated('Mozilla/5.0 Safari', true)).toBe(true);
    expect(isAutomated('Mozilla/5.0 (iPhone; CPU iPhone OS 18_0) Safari/605.1', false)).toBe(false);
    expect(isAutomated(undefined, undefined)).toBe(false);
  });

  it('matches excluded paths by prefix or pattern', () => {
    expect(isExcludedPath('/en/legal/terms', ['/en/legal'])).toBe(true);
    expect(isExcludedPath('/en/pricing', ['/en/legal'])).toBe(false);
    expect(isExcludedPath('/ru/legal', [/^\/[a-z]{2}\/legal/g])).toBe(true);
    expect(isExcludedPath('/ru/legal', [/^\/[a-z]{2}\/legal/g])).toBe(true);
    expect(isExcludedPath('/x', undefined)).toBe(false);
  });
});
