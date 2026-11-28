import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { HumanCheckScope } from './types';
import { inScope, matchHost, matchPath, safeNext } from './scope';

test('path patterns: exact, prefix, star suffix', () => {
  assert.ok(matchPath('/app/*', '/app'));
  assert.ok(matchPath('/app/*', '/app/x/y'));
  assert.ok(!matchPath('/app/*', '/apple'));
  assert.ok(matchPath('/sitemap*', '/sitemap-1.xml'));
  assert.ok(matchPath('/pricing', '/pricing'));
  assert.ok(!matchPath('/pricing', '/pricing/x'));
});

test('host patterns', () => {
  assert.ok(matchHost('app.example.com', 'APP.example.com'));
  assert.ok(matchHost('*.example.com', 'a.example.com'));
  assert.ok(!matchHost('*.example.com', 'example.com'));
  assert.ok(!matchHost('*.example.com', 'evilexample.com'));
});

test('site, routes and hosts scopes; marketing open, cabinet gated', () => {
  assert.ok(inScope({ kind: 'site' }, 'x.com', '/anything'));
  const routes: HumanCheckScope = { kind: 'routes', include: ['/cabinet/*'], exclude: ['/cabinet/public/*'] };
  assert.ok(inScope(routes, 'x.com', '/cabinet/a'));
  assert.ok(!inScope(routes, 'x.com', '/cabinet/public/a'));
  assert.ok(!inScope(routes, 'x.com', '/pricing'));
  const hosts: HumanCheckScope = { kind: 'hosts', hosts: { 'app.x.com': 'site', 'x.com': { include: ['/admin/*'] } } };
  assert.ok(inScope(hosts, 'app.x.com', '/'));
  assert.ok(inScope(hosts, 'x.com', '/admin/u'));
  assert.ok(!inScope(hosts, 'x.com', '/'));
  assert.ok(!inScope(hosts, 'other.com', '/'), 'unlisted host is not gated');
});

test('next must be a same-origin relative path', () => {
  const g = '/__human-check';
  assert.equal(safeNext('/a?b=1', g), '/a?b=1');
  for (const bad of ['https://evil.example', '//evil.example', '/\\evil.example', 'javascript:1', '/a\r\nb', '', null, undefined, '/__human-check?next=/']) {
    assert.equal(safeNext(bad as string, g), '/', String(bad));
  }
});
