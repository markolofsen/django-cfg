import assert from 'node:assert/strict';
import { test } from 'node:test';

import { createCrawlerMatcher, inCidr, isPreviewBot, parseCidr, parseIp, parseRanges } from './crawlers';

test('CIDR matching, v4 and v6', () => {
  const c4 = parseCidr('66.249.64.0/27')!;
  assert.ok(inCidr(parseIp('66.249.64.10')!, c4));
  assert.ok(!inCidr(parseIp('66.249.64.200')!, c4));
  const c6 = parseCidr('2001:4860:4801::/48')!;
  assert.ok(inCidr(parseIp('2001:4860:4801:1::5')!, c6));
  assert.ok(!inCidr(parseIp('2001:4860:4802::1')!, c6));
  assert.ok(inCidr(parseIp('::ffff:66.249.64.10')!, c4), 'v4-mapped v6 is treated as v4');
  assert.equal(parseIp('999.1.1.1'), null);
  assert.equal(parseCidr('1.2.3.4/40'), null);
});

test('parseRanges reads the published format and skips junk', () => {
  const r = parseRanges({ prefixes: [{ ipv4Prefix: '1.2.3.0/24' }, { ipv6Prefix: '2001:db8::/32' }, { nope: 1 }] });
  assert.equal(r.length, 2);
});

const json = (o: unknown) => ({ ok: true, status: 200, json: async () => o }) as Response;
const LIST = { prefixes: [{ ipv4Prefix: '66.249.64.0/27' }] };

test('verified IP passes; fake Googlebot UA from a foreign IP is spoofed; plain browser is none', async () => {
  const m = createCrawlerMatcher({ sources: ['u'], fetch: (async () => json(LIST)) as typeof fetch });
  assert.equal(await m.check('66.249.64.10', 'Googlebot/2.1'), 'verified');
  assert.equal(await m.check('203.0.113.9', 'Mozilla/5.0 (compatible; Googlebot/2.1)'), 'spoofed');
  assert.equal(await m.check('203.0.113.9', 'Mozilla/5.0 Chrome'), 'none');
});

test('list never loaded: a crawler claim is "unknown", not a silent pass for plain UAs', async () => {
  const m = createCrawlerMatcher({ sources: ['u'], fetch: (async () => { throw new Error('down'); }) as typeof fetch });
  assert.equal(await m.check('203.0.113.9', 'Googlebot/2.1'), 'unknown');
  assert.equal(await m.check('203.0.113.9', 'Mozilla/5.0'), 'none');
});

test('a failed refresh keeps the last good list; staleness raises the alert once', async () => {
  let t = 1; // 0 would read as "never loaded"
  let ok = true;
  const alerts: number[] = [];
  const m = createCrawlerMatcher({
    sources: ['u'],
    ttlMs: 10,
    staleAfterMs: 1000,
    now: () => t,
    fetch: (async () => { if (!ok) throw new Error('down'); return json(LIST); }) as typeof fetch,
    onStale: (age) => alerts.push(age),
  });
  assert.equal(await m.check('66.249.64.10', null), 'verified');
  ok = false;
  t = 500;
  assert.equal(await m.check('66.249.64.10', null), 'verified', 'last good list still used');
  assert.equal(alerts.length, 0);
  t = 5000;
  await m.check('66.249.64.10', null);
  await m.check('66.249.64.10', null);
  assert.equal(alerts.length, 1);
});

test('link-preview UAs', () => {
  for (const ua of ['TelegramBot (like TwitterBot)', 'Slackbot-LinkExpanding 1.0', 'facebookexternalhit/1.1', 'LinkedInBot/1.0', 'WhatsApp/2']) assert.ok(isPreviewBot(ua), ua);
  assert.ok(!isPreviewBot('Mozilla/5.0 Chrome'));
});
