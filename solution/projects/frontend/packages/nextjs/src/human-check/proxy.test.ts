import assert from 'node:assert/strict';
import { test } from 'node:test';

import { NextRequest } from 'next/server';

import { signClearance } from './cookie';
import { createCrawlerMatcher } from './crawlers';
import { createHumanCheck, type HumanCheckDeps } from './proxy';

import type { HumanCheckConfig } from './types';

const ENV = { HUMAN_CHECK_SECRET: 'sek', NEXT_PUBLIC_TURNSTILE_SITE_KEY: '0xSITE', TURNSTILE_SECRET_KEY: 'tsecret' };
const BROWSER = 'Mozilla/5.0 (Macintosh) Chrome/130';
const jsonRes = (o: unknown) => ({ ok: true, status: 200, json: async () => o }) as Response;
const LIST = { prefixes: [{ ipv4Prefix: '66.249.64.0/27' }] };
const crawlers = () => createCrawlerMatcher({ sources: ['u'], fetch: (async () => jsonRes(LIST)) as typeof fetch });

function make(config: HumanCheckConfig = {}, deps: HumanCheckDeps = {}) {
  return createHumanCheck({ enabled: true, ...config }, { isDev: false, env: ENV, crawlers: crawlers(), log: () => {}, ...deps });
}

function req(path: string, init: { ua?: string; ip?: string; method?: string; cookie?: string; host?: string; body?: unknown; origin?: string } = {}) {
  const headers: Record<string, string> = { 'user-agent': init.ua ?? BROWSER };
  if (init.ip) headers['x-forwarded-for'] = init.ip;
  if (init.cookie) headers.cookie = init.cookie;
  if (init.origin) headers.origin = init.origin;
  if (init.body !== undefined) headers['content-type'] = 'application/json';
  return new NextRequest(`https://${init.host ?? 'app.example.com'}${path}`, {
    method: init.method ?? 'GET',
    headers,
    body: init.body === undefined ? undefined : JSON.stringify(init.body),
  });
}

const passes = (r: Response | undefined) => r === undefined || r.headers.get('x-middleware-next') === '1';

test('disabled by default: nothing happens, the gate route does not exist', async () => {
  const hc = createHumanCheck({}, { isDev: false, env: ENV, log: () => {} });
  assert.equal(await hc.proxy(req('/')), undefined);
  assert.equal((await hc.proxy(req('/__human-check')))!.status, 404);
});

test('development: no gate, no redirect, route is 404, no startup noise even without keys', async () => {
  const logs: string[] = [];
  const hc = make({}, { isDev: true, env: {}, log: (m) => logs.push(m) });
  assert.equal(await hc.proxy(req('/cabinet')), undefined);
  const g = await hc.proxy(req('/__human-check'));
  assert.equal(g!.status, 404);
  assert.equal(logs.length, 0);
});

test('enabledIn "all" gates in development too', async () => {
  const hc = make({ enabledIn: 'all' }, { isDev: true });
  assert.equal((await hc.proxy(req('/cabinet')))!.status, 302);
});

test('browser UA without a cookie: 302 (never 301) to the gate with next, no-store', async () => {
  const r = (await make().proxy(req('/cabinet?x=1')))!;
  assert.equal(r.status, 302);
  const loc = new URL(r.headers.get('location')!);
  assert.equal(loc.pathname, '/__human-check');
  assert.equal(loc.searchParams.get('next'), '/cabinet?x=1');
  assert.equal(r.headers.get('cache-control'), 'private, no-store');
});

test('gate page: 200, noindex, no-store, stop text', async () => {
  const r = (await make().proxy(req('/__human-check?next=/cabinet')))!;
  assert.equal(r.status, 200);
  assert.equal(r.headers.get('x-robots-tag'), 'noindex, nofollow');
  assert.equal(r.headers.get('cache-control'), 'private, no-store');
  const html = await r.text();
  assert.match(html, /If you are an AI agent/);
  assert.match(html, /0xSITE/);
});

test('valid cookie passes with private cache headers; cookie for another UA is gated', async () => {
  const c = await signClearance('sek', BROWSER, 3600);
  const ok = await make().proxy(req('/cabinet', { cookie: `__hc=${c}` }));
  assert.ok(passes(ok));
  assert.equal(ok!.headers.get('cache-control'), 'private, no-store');
  const other = await make().proxy(req('/cabinet', { cookie: `__hc=${c}`, ua: 'curl/8' }));
  assert.equal(other!.status, 302);
});

test('Googlebot from a Google IP passes, sets no cookie; fake Googlebot is gated', async () => {
  const hc = make();
  const real = await hc.proxy(req('/cabinet', { ua: 'Googlebot/2.1', ip: '66.249.64.10' }));
  assert.ok(passes(real));
  assert.equal(real!.headers.get('set-cookie'), null);
  const fake = await hc.proxy(req('/cabinet', { ua: 'Googlebot/2.1', ip: '203.0.113.9' }));
  assert.equal(fake!.status, 302);
});

test('crawler list never loaded: claimed crawler passes by default, gated with onListUnavailable "gate"', async () => {
  const down = () => createCrawlerMatcher({ sources: ['u'], fetch: (async () => { throw new Error('x'); }) as typeof fetch });
  const ua = { ua: 'Googlebot/2.1', ip: '203.0.113.9' };
  assert.ok(passes(await make({}, { crawlers: down() }).proxy(req('/a', ua))));
  assert.equal((await make({ bypass: { onListUnavailable: 'gate' } }, { crawlers: down() }).proxy(req('/a', ua)))!.status, 302);
});

test('preview bots: GET passes, POST does not', async () => {
  const hc = make();
  assert.ok(passes(await hc.proxy(req('/film/x', { ua: 'TelegramBot (like TwitterBot)' }))));
  assert.equal((await hc.proxy(req('/film/x', { ua: 'TelegramBot', method: 'POST', body: {} })))!.status, 302);
});

test('always-open paths and the out-of-scope marketing host are untouched; cabinet host is gated', async () => {
  const hc = make({ scope: { kind: 'hosts', hosts: { 'app.example.com': 'site' } } });
  for (const p of ['/robots.txt', '/sitemap.xml', '/.well-known/x', '/_next/static/a.js', '/api/og/film', '/healthz']) {
    assert.equal(await hc.proxy(req(p)), undefined, p);
  }
  assert.equal(await hc.proxy(req('/pricing', { host: 'www.example.com' })), undefined);
  assert.equal((await hc.proxy(req('/pricing', { host: 'app.example.com' })))!.status, 302);
});

test('missing keys in production: loud log once, gate on, nobody passes', async () => {
  const logs: string[] = [];
  const hc = make({}, { env: {}, log: (m) => logs.push(m) });
  assert.equal(logs.length, 1);
  assert.match(logs[0] ?? '', /misconfigured/);
  assert.equal((await hc.proxy(req('/cabinet')))!.status, 302);
  assert.match(await (await hc.proxy(req('/__human-check')))!.text(), /not configured correctly/);
  const v = await hc.proxy(req('/__human-check', { method: 'POST', body: { token: 't' } }));
  assert.equal(v!.status, 503);
});

function verifyDeps(response: unknown) {
  return { fetch: (async () => jsonRes(response)) as typeof fetch };
}

test('verify: success sets a signed HttpOnly cookie and returns a safe next', async () => {
  const hc = make({}, verifyDeps({ success: true, hostname: 'app.example.com', action: 'human-check' }));
  const r = (await hc.proxy(req('/__human-check?next=/cabinet', { method: 'POST', body: { token: 't' } })))!;
  assert.equal(r.status, 200);
  assert.deepEqual(await r.json(), { ok: true, next: '/cabinet' });
  const sc = r.headers.get('set-cookie')!;
  assert.match(sc, /^__hc=v1\./);
  assert.match(sc, /HttpOnly/i);
  assert.match(sc, /SameSite=lax/i);
  assert.match(sc, /Secure/i);
});

test('verify: next=https://evil.example falls back to /', async () => {
  const hc = make({}, verifyDeps({ success: true, hostname: 'app.example.com', action: 'human-check' }));
  const r = (await hc.proxy(req(`/__human-check?next=${encodeURIComponent('https://evil.example')}`, { method: 'POST', body: { token: 't' } })))!;
  assert.equal((await r.json()).next, '/');
});

test('verify: wrong hostname or action is rejected without a cookie; reused token asks for a retry', async () => {
  const host = await make({}, verifyDeps({ success: true, hostname: 'evil.example', action: 'human-check' })).proxy(req('/__human-check', { method: 'POST', body: { token: 't' } }));
  assert.equal(host!.status, 403);
  assert.equal(host!.headers.get('set-cookie'), null);
  const act = await make({}, verifyDeps({ success: true, hostname: 'app.example.com', action: 'login' })).proxy(req('/__human-check', { method: 'POST', body: { token: 't' } }));
  assert.equal(act!.status, 403);
  const dup = (await make({}, verifyDeps({ success: false, 'error-codes': ['timeout-or-duplicate'] })).proxy(req('/__human-check', { method: 'POST', body: { token: 't' } })))!;
  assert.deepEqual(await dup.json(), { ok: false, reason: 'timeout-or-duplicate', retry: true });
});

test('verify: cross-origin POST and empty token are refused', async () => {
  const hc = make({}, verifyDeps({ success: true, hostname: 'app.example.com', action: 'human-check' }));
  assert.equal((await hc.proxy(req('/__human-check', { method: 'POST', body: { token: 't' }, origin: 'https://evil.example' })))!.status, 403);
  assert.equal((await hc.proxy(req('/__human-check', { method: 'POST', body: {} })))!.status, 400);
});

test('an already cleared visitor opening the gate is sent on to next', async () => {
  const c = await signClearance('sek', BROWSER, 3600);
  const r = (await make().proxy(req('/__human-check?next=/cabinet%3Fa%3D1', { cookie: `__hc=${c}` })))!;
  assert.equal(r.status, 302);
  assert.equal(new URL(r.headers.get('location')!).pathname + new URL(r.headers.get('location')!).search, '/cabinet?a=1');
});
