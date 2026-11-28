import assert from 'node:assert/strict';
import { test } from 'node:test';

import { NextRequest } from 'next/server';

import { createSsoMiddleware } from './middleware';

const HOST = 'auth.reforms.ai';
const mw = createSsoMiddleware({ authHost: HOST, protect: ['/private'], allow: ['/private/public-help'] });
const SESSION = 'cfg.auth.access_token=abc';

function req(url: string, init: { cookie?: string; headers?: Record<string, string> } = {}) {
  const headers: Record<string, string> = { ...(init.headers ?? {}) };
  if (init.cookie) headers.cookie = init.cookie;
  return new NextRequest(url, { headers });
}
const passes = (r: Response) => r.headers.get('x-middleware-next') === '1';
const location = (r: Response) => r.headers.get('location');

test('follower, no session, protected path: 307 to the host with next', () => {
  const r = mw(req('https://my.reforms.ai/private/orders?id=3'));
  assert.equal(r.status, 307);
  assert.equal(
    location(r),
    `https://auth.reforms.ai/auth?next=${encodeURIComponent('https://my.reforms.ai/private/orders?id=3')}`,
  );
});

test('follower with a session, a public path, or an allowed path: passes', () => {
  assert.ok(passes(mw(req('https://my.reforms.ai/private', { cookie: SESSION }))));
  assert.ok(passes(mw(req('https://my.reforms.ai/pricing'))));
  assert.ok(passes(mw(req('https://my.reforms.ai/private/public-help'))));
  assert.ok(passes(mw(req('https://my.reforms.ai/private', { cookie: 'cfg.auth.refresh_token=r' }))));
});

test('locale prefix does not hide a protected path', () => {
  assert.equal(mw(req('https://my.reforms.ai/ru/private/x')).status, 307);
});

test('behind a proxy the visitor host (x-forwarded-*) decides, not the container address', () => {
  const r = mw(req('http://10.0.0.5:3000/private', { headers: { 'x-forwarded-host': 'hub.reforms.ai', 'x-forwarded-proto': 'https' } }));
  assert.equal(r.status, 307);
  assert.equal(location(r), `https://auth.reforms.ai/auth?next=${encodeURIComponent('https://hub.reforms.ai/private')}`);
});

test('the host itself never redirects to itself', () => {
  assert.ok(passes(mw(req('https://auth.reforms.ai/private'))));
  assert.ok(passes(mw(req('https://auth.reforms.ai/auth?next=https%3A%2F%2Fmy.reforms.ai%2Fx'))));
});

test('host, signed in, /auth?next=: goes straight back to a valid next', () => {
  const r = mw(req(`https://auth.reforms.ai/auth?next=${encodeURIComponent('https://tutor.reforms.ai/lesson/1')}`, { cookie: SESSION }));
  assert.equal(r.status, 307);
  assert.equal(location(r), 'https://tutor.reforms.ai/lesson/1?sso_ret=1');
});

test('host, signed in: an open-redirect attempt is ignored, the page renders', () => {
  for (const bad of ['https://evil.com/', '//evil.com', 'https://reforms.ai.evil.com/', 'https://reforms.ai@evil.com/', 'javascript:alert(1)', 'https://reforms.ai/auth?next=https://evil.com']) {
    const r = mw(req(`https://auth.reforms.ai/auth?next=${encodeURIComponent(bad)}`, { cookie: SESSION }));
    assert.ok(passes(r), `${bad} must not redirect`);
  }
});

test('localhost and foreign hosts: off, nothing is blocked', () => {
  assert.ok(passes(mw(req('http://localhost:3000/private'))));
  assert.ok(passes(mw(req('https://evilreforms.ai/private'))));
});

test('no host configured: does nothing', () => {
  const off = createSsoMiddleware({ host: undefined });
  assert.ok(passes(off(req('https://my.reforms.ai/private'))));
});

test('the public apex site is a follower: public pages open, protected ones go to auth.', () => {
  assert.ok(passes(mw(req('https://reforms.ai/'))));
  assert.ok(passes(mw(req('https://reforms.ai/pricing'))));
  assert.equal(mw(req('https://reforms.ai/private')).status, 307);
});

// ── no cycle when the shared cookie does not reach the follower ──────────────
test('host: a signed-in visitor is sent back to next WITH the return marker', () => {
  const r = mw(req(`https://auth.reforms.ai/auth?next=${encodeURIComponent('https://my.reforms.ai/private')}`, { cookie: SESSION }));
  assert.equal(r.status, 307);
  assert.equal(location(r), 'https://my.reforms.ai/private?sso_ret=1');
});

test('follower: back from the host (sso_ret) and still no cookie -> host with sso_error, marker removed', () => {
  const r = mw(req('https://my.reforms.ai/private?sso_ret=1'));
  assert.equal(r.status, 307);
  assert.equal(
    location(r),
    `https://auth.reforms.ai/auth?next=${encodeURIComponent('https://my.reforms.ai/private')}&sso_error=cookie`,
  );
});

test('host: sso_error stops the send-back, the form is shown (end of the cycle)', () => {
  const r = mw(req(`https://auth.reforms.ai/auth?sso_error=cookie&next=${encodeURIComponent('https://my.reforms.ai/private')}`, { cookie: SESSION }));
  assert.ok(passes(r));
});

test('follower with the cookie and the marker: passes (the client strips the marker)', () => {
  assert.ok(passes(mw(req('https://my.reforms.ai/private?sso_ret=1', { cookie: SESSION }))));
});
