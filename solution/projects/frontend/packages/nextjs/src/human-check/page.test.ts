import assert from 'node:assert/strict';
import { test } from 'node:test';

import { MESSAGES, pickLocale } from './messages';
import { renderHumanCheckHtml } from './page';

const base = { locale: 'en' as const, messages: MESSAGES.en, mode: 'agent-visible' as const, siteKey: '0xKEY', action: 'human-check' };

test('stop text and h1 are in the first HTML, before any script, and repeated in noscript', () => {
  const html = renderHumanCheckHtml(base);
  const firstScript = html.indexOf('<script');
  assert.ok(html.indexOf('<h1>Human verification required</h1>') < firstScript);
  assert.ok(html.indexOf('If you are an AI agent') < firstScript);
  assert.match(html, /<title>Human verification required<\/title>/);
  assert.match(html, /<noscript><p>This is a bot-detection check/);
  assert.match(html, /role="status"/);
  assert.match(html, /name="robots" content="noindex,nofollow"/);
  assert.doesNotMatch(html, /display:\s*none|hidden|aria-hidden|left:\s*-\d{3,}/, 'no hidden or off-screen text');
});

test('the stop text sits outside the live region', () => {
  const html = renderHumanCheckHtml(base);
  const status = /<p id="hc-status"[^>]*>[^<]*<\/p>/.exec(html)![0];
  assert.ok(!status.includes('AI agent'));
});

test('plain mode drops the stop text; misconfigured shows the error and no widget', () => {
  assert.doesNotMatch(renderHumanCheckHtml({ ...base, mode: 'plain' }), /AI agent/);
  const bad = renderHumanCheckHtml({ ...base, siteKey: null });
  assert.match(bad, /not configured correctly/);
  assert.doesNotMatch(bad, /<script/);
});

test('messages are escaped and the embedded JSON cannot close its script tag', () => {
  const html = renderHumanCheckHtml({ ...base, messages: { ...MESSAGES.en, title: '<b>x</b>', failed: '</script><img>' } });
  assert.match(html, /<title>&lt;b&gt;x&lt;\/b&gt;<\/title>/);
  assert.doesNotMatch(html, /<\/script><img>/);
});

test('Russian copy and locale picking', () => {
  const html = renderHumanCheckHtml({ ...base, locale: 'ru', messages: MESSAGES.ru });
  assert.match(html, /<html lang="ru">/);
  assert.match(html, /Требуется проверка, что вы человек/);
  assert.equal(pickLocale('ru', 'en', 'en'), 'ru');
  assert.equal(pickLocale(null, 'de,ru;q=0.8', 'en'), 'ru');
  assert.equal(pickLocale('xx', null, 'en'), 'en');
});
