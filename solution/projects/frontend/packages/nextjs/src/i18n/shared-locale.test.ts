import assert from 'node:assert/strict';
import { test } from 'node:test';

import { expireHostOnlyLocaleCookie, localeCookieHeader, sharedCookieDomain } from './shared-locale';

test('the registrable domain of a subdomain host', () => {
  assert.equal(sharedCookieDomain('hub.example.com'), 'example.com');
  assert.equal(sharedCookieDomain('team.hub.example.com:3000'), 'example.com');
  assert.equal(sharedCookieDomain('example.com'), 'example.com');
});

test('two-label public suffixes keep three labels', () => {
  assert.equal(sharedCookieDomain('hub.example.co.uk'), 'example.co.uk');
});

test('hosts that cannot share get no domain', () => {
  assert.equal(sharedCookieDomain('localhost:3211'), null);
  assert.equal(sharedCookieDomain('127.0.0.1'), null);
  assert.equal(sharedCookieDomain('[::1]'), null);
});

test('the override wins', () => {
  assert.equal(sharedCookieDomain('hub.example.org', '.corp.example.org'), 'corp.example.org');
  assert.equal(sharedCookieDomain('localhost', 'dev.test'), 'dev.test');
});

test('cookie headers', () => {
  assert.equal(
    localeCookieHeader('ru', 'example.com', true),
    'NEXT_LOCALE=ru; Path=/; Max-Age=31536000; SameSite=Lax; Domain=example.com; Secure',
  );
  assert.equal(localeCookieHeader('ru', null, false), 'NEXT_LOCALE=ru; Path=/; Max-Age=31536000; SameSite=Lax');
  assert.equal(expireHostOnlyLocaleCookie(false), 'NEXT_LOCALE=; Path=/; Max-Age=0; SameSite=Lax');
});
