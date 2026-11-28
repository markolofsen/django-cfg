import assert from 'node:assert/strict';
import { test } from 'vitest';

import { resolveLanguage, toSpeechTag, WEB_SPEECH_LANGUAGES } from '@djangocfg/ui-core/lib/speech-language';

import { ASSISTANT_DICTIONARIES } from '../../../../i18n/assistant';

const LOCALES = Object.keys(ASSISTANT_DICTIONARIES);
const KNOWN = new Set(WEB_SPEECH_LANGUAGES.flatMap((language) => language.dialects.map((d) => d.code)));

test('the dictation list covers every bundled locale: each resolves to a tag the picker lists', () => {
  assert.equal(LOCALES.length, 17);
  for (const locale of LOCALES) {
    const tag = toSpeechTag(locale);
    assert.ok(tag && KNOWN.has(tag), `${locale} -> ${tag}`);
  }
});

test('with no pick the page language leads when the browser also speaks it, else the browser, else English', () => {
  assert.equal(resolveLanguage({ uiLocale: 'ru', browserLanguages: ['en-US', 'ru'], browserLanguage: 'en-US' }), 'ru-RU');
  assert.equal(resolveLanguage({ uiLocale: 'ru', browserLanguages: ['en-US'], browserLanguage: 'en-US' }), 'en-US');
  assert.equal(resolveLanguage({}), 'en-US');
});

test('a remembered pick wins over the page language', () => {
  assert.equal(resolveLanguage({ picked: 'de-DE', uiLocale: 'ru', browserLanguages: ['ru'], browserLanguage: 'ru' }), 'de-DE');
});
