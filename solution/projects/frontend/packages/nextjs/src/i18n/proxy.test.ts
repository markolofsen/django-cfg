import assert from 'node:assert/strict';
import { test } from 'node:test';
import { NextRequest, NextResponse } from 'next/server';
import { createProxy, shareLocaleCookie } from './proxy';
import { createRouting } from './routing';

const page = (url: string, cookie: string) =>
  new NextRequest(url, { headers: { cookie, 'sec-fetch-dest': 'document', 'accept-language': 'en-US,en;q=0.9', 'x-forwarded-proto': 'https' } });

test('a host without the reader\'s locale leaves the shared cookie alone', () => {
  // reforms.ai serves English only; the reader picked Russian on my.reforms.ai.
  const proxy = createProxy(createRouting({ locales: ['en'], defaultLocale: 'en' }));
  const out = proxy(page('https://reforms.ai/', 'NEXT_LOCALE=ru'));
  assert.equal(out.headers.getSetCookie().filter((l) => l.startsWith('NEXT_LOCALE=')).length, 0);
});

test('a host with the reader\'s locale still follows the cookie', () => {
  const proxy = createProxy(createRouting({ locales: ['en', 'ru'], defaultLocale: 'en' }));
  const out = proxy(page('https://my.reforms.ai/', 'NEXT_LOCALE=ru'));
  assert.equal(out.status, 307);
  assert.equal(new URL(out.headers.get('location')!).pathname, '/ru');
});

test('a switch the server sees is remembered for a year, not the session', () => {
  const routing = createRouting({ locales: ['en', 'ru'], defaultLocale: 'en' });
  assert.deepEqual(routing.localeCookie, { maxAge: 60 * 60 * 24 * 365 });
  const out = createProxy(routing)(page('https://my.reforms.ai/ru', 'NEXT_LOCALE=en'));
  assert.ok(out.headers.getSetCookie().some((l) => l.startsWith('NEXT_LOCALE=ru') && l.includes('Max-Age=31536000')));
});

test('rewrites the cookie onto the registrable domain', () => {
  const request = new NextRequest('https://hub.example.com/ru', { headers: { 'x-forwarded-proto': 'https' } });
  const response = NextResponse.next();
  response.cookies.set('NEXT_LOCALE', 'ru', { path: '/' });
  const out = shareLocaleCookie(request, response);
  const lines = out.headers.getSetCookie();
  assert.ok(lines.some((l) => l.startsWith('NEXT_LOCALE=ru') && l.includes('Domain=example.com')));
  assert.ok(lines.some((l) => l.startsWith('NEXT_LOCALE=;') && l.includes('Max-Age=0') && !l.includes('Domain')));
});

test('localhost is left alone', () => {
  const request = new NextRequest('http://localhost:3211/ru');
  const response = NextResponse.next();
  response.cookies.set('NEXT_LOCALE', 'ru', { path: '/' });
  const out = shareLocaleCookie(request, response);
  assert.equal(out.headers.getSetCookie().length, 1);
});
