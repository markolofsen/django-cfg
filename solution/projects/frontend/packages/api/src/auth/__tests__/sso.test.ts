/**
 * Single sign-in host (utils/sso.ts): the `next` gate, the host decision, the sign-in URL.
 * The bypass table is the contract; the Python twin (`safe_next_url`) runs the same rows.
 */
import { afterEach, describe, expect, it } from 'vitest';

import {
  __resetSsoForTests,
  buildSsoLoginUrl,
  deriveAuthHost,
  configureSso,
  getSsoState,
  hasReturnMarker,
  markReturn,
  stripReturnMarker,
  isAuthRoute,
  parseSsoHost,
  registrableDomain,
  resolveSso,
  safeNext,
} from '../utils/sso';

const APEX = 'reforms.ai';

describe('safeNext', () => {
  it.each([
    ['https://reforms.ai/', 'https://reforms.ai/'],
    ['https://my.reforms.ai/private/x?y=1#z', 'https://my.reforms.ai/private/x?y=1#z'],
    ['https://HUB.Reforms.AI/a', 'https://hub.reforms.ai/a'],
    ['/private/orders?id=3', '/private/orders?id=3'],
  ])('accepts %s', (input, out) => {
    expect(safeNext(input, APEX)).toBe(out);
  });

  it.each([
    'https://evil.com/',
    'https://evil.com/https://reforms.ai',
    'https://evilreforms.ai/',
    'https://reforms.ai.evil.com/',
    'https://reforms.ai@evil.com/',
    'https://evil.com@reforms.ai/', // userinfo: browsers resolve it to reforms.ai, but never trust a credential-looking URL
    'https://user:pass@my.reforms.ai/',
    'https://my.reforms.ai:8443/',
    'https://my.reforms.ai.:8443/',
    'http://my.reforms.ai/',
    '//evil.com',
    '//my.reforms.ai/x',
    '/\\evil.com',
    '\\\\evil.com',
    'https:\\\\evil.com',
    'https://evil.com\\@reforms.ai/',
    'javascript:alert(1)',
    'JaVaScRiPt:alert(1)',
    'data:text/html,<script>1</script>',
    'vbscript:x',
    'ftp://reforms.ai/',
    'reforms.ai/x',
    'my.reforms.ai',
    ' https://evil.com',
    'https://my.reforms.ai/\n',
    'https://my.reforms.ai/%0d%0aSet-Cookie:x',
    '/%5cevil.com',
    '/%2fevil.com',
    '/%2f%2fevil.com',
    'https://my.reforms.ai%2f@evil.com/',
    'https://my.reforms.ai%2fevil.com/',
    'https://auth.reforms.ai/auth?next=%2f%2fevil.com',
    '/\t/evil.com',
    'https://my.reforms.ai/ x',
    'https://',
    'https://my..reforms.ai/',
    'https://xn--.reforms.ai/'.replace('xn--', '-'),
    // nested redirects: the sign-in page is never a target
    'https://reforms.ai/auth?next=https://evil.com',
    'https://reforms.ai/auth',
    'https://my.reforms.ai/ru/auth/',
    '/auth?next=//evil.com',
    '/auth',
    '',
    '   ',
  ])('refuses %j', (input) => {
    expect(safeNext(input, APEX)).toBeNull();
  });

  it('refuses non-strings and oversized values', () => {
    expect(safeNext(undefined, APEX)).toBeNull();
    expect(safeNext(null, APEX)).toBeNull();
    expect(safeNext(['https://reforms.ai'] as unknown, APEX)).toBeNull();
    expect(safeNext(`https://reforms.ai/${'a'.repeat(3000)}`, APEX)).toBeNull();
  });

  it('refuses every absolute URL when there is no apex (SSO off)', () => {
    expect(safeNext('https://reforms.ai/', null)).toBeNull();
    expect(safeNext('/private', null)).toBe('/private');
  });

  it('keeps a lookalike out of a shared host', () => {
    expect(safeNext('https://other.vercel.app/', 'mine.vercel.app')).toBeNull();
    expect(safeNext('https://x.mine.vercel.app/', 'mine.vercel.app')).toBe('https://x.mine.vercel.app/');
  });
});

describe('registrableDomain / parseSsoHost', () => {
  it('takes the registrable part', () => {
    expect(registrableDomain('my.reforms.ai')).toBe('reforms.ai');
    expect(registrableDomain('a.b.example.co.uk')).toBe('example.co.uk');
    expect(registrableDomain('foo.vercel.app')).toBe('foo.vercel.app');
    expect(registrableDomain('vercel.app')).toBeNull();
    expect(registrableDomain('localhost')).toBeNull();
    expect(registrableDomain('127.0.0.1')).toBeNull();
  });
  it('accepts a bare host or an https origin, nothing else', () => {
    expect(parseSsoHost('reforms.ai')?.origin).toBe('https://reforms.ai');
    expect(parseSsoHost('https://Reforms.ai/')?.hostname).toBe('reforms.ai');
    for (const bad of ['http://reforms.ai', 'https://reforms.ai/auth', 'https://a@reforms.ai', 'https://reforms.ai:444', 'localhost', '', 'a b.com', 'https://reforms.ai?x=1']) {
      expect(parseSsoHost(bad)).toBeNull();
    }
  });
});

describe('resolveSso', () => {
  const cfg = { host: 'reforms.ai' };
  it('is off and quiet without config', () => {
    expect(resolveSso(undefined, { hostname: 'my.reforms.ai' })).toMatchObject({ enabled: false, reason: 'not-configured' });
  });
  it('a subdomain is a follower, the host is the auth host', () => {
    expect(resolveSso(cfg, { hostname: 'my.reforms.ai', protocol: 'https:' })).toMatchObject({
      enabled: true, isAuthHost: false, authOrigin: 'https://reforms.ai', authPath: '/auth', apex: 'reforms.ai',
    });
    expect(resolveSso(cfg, { hostname: 'reforms.ai', protocol: 'https:' })).toMatchObject({ enabled: true, isAuthHost: true });
  });
  it('localhost and foreign hosts fall back to the per-host sign-in, with a reason', () => {
    expect(resolveSso(cfg, { hostname: 'localhost', protocol: 'http:' })).toMatchObject({ enabled: false, reason: 'outside-apex' });
    expect(resolveSso(cfg, { hostname: 'preview-1.vercel.app', protocol: 'https:' })).toMatchObject({ enabled: false });
    expect(resolveSso(cfg, { hostname: 'evilreforms.ai', protocol: 'https:' })).toMatchObject({ enabled: false });
  });
  it('an invalid host disables it', () => {
    expect(resolveSso({ host: 'https://reforms.ai/x' }, { hostname: 'reforms.ai' })).toMatchObject({ enabled: false, reason: 'invalid-host' });
  });
});

describe('dedicated auth host (auth.reforms.ai)', () => {
  const cfg = { authHost: 'auth.reforms.ai' };
  it('the apex site and every subdomain follow; only auth. is the host', () => {
    expect(resolveSso(cfg, { hostname: 'reforms.ai', protocol: 'https:' })).toMatchObject({ enabled: true, isAuthHost: false, apex: 'reforms.ai', authOrigin: 'https://auth.reforms.ai' });
    expect(resolveSso(cfg, { hostname: 'my.reforms.ai', protocol: 'https:' })).toMatchObject({ enabled: true, isAuthHost: false });
    expect(resolveSso(cfg, { hostname: 'auth.reforms.ai', protocol: 'https:' })).toMatchObject({ enabled: true, isAuthHost: true });
  });
  it('next may point to the apex site and to other subdomains, never to the sign-in page', () => {
    expect(safeNext('https://reforms.ai/pricing', 'reforms.ai')).toBe('https://reforms.ai/pricing');
    expect(safeNext('https://auth.reforms.ai/auth', 'reforms.ai')).toBeNull();
  });
  it('builds the url on the auth host', () => {
    const st = resolveSso(cfg, { hostname: 'reforms.ai', protocol: 'https:' });
    expect(buildSsoLoginUrl(st, 'https://reforms.ai/x')).toBe(`https://auth.reforms.ai/auth?next=${encodeURIComponent('https://reforms.ai/x')}`);
  });
});

describe('buildSsoLoginUrl', () => {
  const state = resolveSso({ host: 'reforms.ai' }, { hostname: 'my.reforms.ai', protocol: 'https:' });
  it('carries a safe next, encoded', () => {
    expect(buildSsoLoginUrl(state, 'https://my.reforms.ai/private?a=1&b=2')).toBe(
      `https://reforms.ai/auth?next=${encodeURIComponent('https://my.reforms.ai/private?a=1&b=2')}`,
    );
  });
  it('drops an unsafe next instead of forwarding it', () => {
    expect(buildSsoLoginUrl(state, 'https://evil.com/')).toBe('https://reforms.ai/auth');
    expect(buildSsoLoginUrl(state, null)).toBe('https://reforms.ai/auth');
  });
  it('is null when SSO is off', () => {
    expect(buildSsoLoginUrl(resolveSso(undefined, { hostname: 'x.com' }), '/a')).toBeNull();
  });
});

describe('isAuthRoute / registry', () => {
  afterEach(() => __resetSsoForTests());
  it('matches the auth route with locale and trailing slash', () => {
    expect(isAuthRoute('/auth', '/auth')).toBe(true);
    expect(isAuthRoute('/ru/auth/?x=1', '/auth')).toBe(true);
    expect(isAuthRoute('/private', '/auth')).toBe(false);
    expect(isAuthRoute('https://reforms.ai/auth', '/auth')).toBe(false);
  });
  it('getSsoState is off on the server', () => {
    configureSso({ host: 'reforms.ai' });
    expect(getSsoState().enabled).toBe(false);
  });
});

describe('deriveAuthHost (from NEXT_PUBLIC_SITE_URL)', () => {
  it('auth. + the registrable domain, whatever host the site url names', () => {
    expect(deriveAuthHost('https://reforms.ai')).toBe('auth.reforms.ai');
    expect(deriveAuthHost('https://my.reforms.ai/x')).toBe('auth.reforms.ai');
    expect(deriveAuthHost('https://app.example.co.uk')).toBe('auth.example.co.uk');
    expect(deriveAuthHost('https://reforms.ai', 'id')).toBe('id.reforms.ai');
  });
  it('nothing for localhost, an IP, or garbage', () => {
    for (const v of ['http://localhost:3000', 'http://127.0.0.1:3000', '', undefined, null, 'http://']) expect(deriveAuthHost(v)).toBeNull();
  });
});

describe('return marker (cycle breaker)', () => {
  const state = resolveSso({ authHost: 'auth.reforms.ai' }, { hostname: 'my.reforms.ai', protocol: 'https:' });

  it('marks and strips an absolute URL and a path, keeping the rest', () => {
    expect(markReturn('https://my.reforms.ai/private?a=1#z')).toBe('https://my.reforms.ai/private?a=1&sso_ret=1#z');
    expect(markReturn('/private/x')).toBe('/private/x?sso_ret=1');
    expect(stripReturnMarker('https://my.reforms.ai/private?a=1&sso_ret=1')).toBe('https://my.reforms.ai/private?a=1');
    expect(hasReturnMarker('https://my.reforms.ai/p?sso_ret=1')).toBe(true);
    expect(hasReturnMarker('https://my.reforms.ai/p')).toBe(false);
  });

  it('a marked next is still accepted by safeNext (marker is a plain query param)', () => {
    expect(safeNext(markReturn('https://my.reforms.ai/private'), APEX)).toBe('https://my.reforms.ai/private?sso_ret=1');
  });

  it('first hop has no error; a hop made after a return carries sso_error=cookie and a clean next', () => {
    expect(buildSsoLoginUrl(state, 'https://my.reforms.ai/private')).toBe(
      `https://auth.reforms.ai/auth?next=${encodeURIComponent('https://my.reforms.ai/private')}`,
    );
    expect(buildSsoLoginUrl(state, 'https://my.reforms.ai/private?sso_ret=1', true)).toBe(
      `https://auth.reforms.ai/auth?next=${encodeURIComponent('https://my.reforms.ai/private')}&sso_error=cookie`,
    );
  });
});
