import { afterEach, describe, expect, it, vi } from 'vitest';

import { normalizeImageUrl, normalizeImageUrls } from './normalizeUrl';

/**
 * This is the gallery's Mixed Content guard. On an HTTPS page the browser
 * refuses to load an `http://` image and shows a broken tile with only a
 * console warning — so a regression here looks like "the images stopped
 * working" with nothing in the app to point at.
 *
 * The behaviour is environment-dependent (it reads `window.location`), so both
 * halves need asserting: the upgrade on a secure page, and the pass-through
 * everywhere else — including SSR, where touching `window` would throw.
 */

/** Install a fake `window.location.protocol` for the duration of a case. */
function stubProtocol(protocol: string): void {
  vi.stubGlobal('window', { location: { protocol } });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('normalizeImageUrl — on an HTTPS page', () => {
  it('upgrades an http URL to https', () => {
    stubProtocol('https:');
    expect(normalizeImageUrl('http://cdn.example.com/a.png'))
      .toBe('https://cdn.example.com/a.png');
  });

  it('leaves an https URL untouched', () => {
    stubProtocol('https:');
    expect(normalizeImageUrl('https://cdn.example.com/a.png'))
      .toBe('https://cdn.example.com/a.png');
  });

  it('leaves a protocol-relative URL alone — it already inherits https', () => {
    stubProtocol('https:');
    expect(normalizeImageUrl('//cdn.example.com/a.png')).toBe('//cdn.example.com/a.png');
  });

  it('leaves a relative path alone', () => {
    stubProtocol('https:');
    expect(normalizeImageUrl('/static/a.png')).toBe('/static/a.png');
  });

  it('leaves a data URI alone', () => {
    stubProtocol('https:');
    expect(normalizeImageUrl('data:image/png;base64,AAA')).toBe('data:image/png;base64,AAA');
  });

  it('rewrites only the leading scheme, not an http:// that appears in a query', () => {
    // A proxied or signed URL commonly carries the origin as a parameter.
    // `String.replace` with a string needle replaces the FIRST occurrence,
    // which here is the scheme — the embedded one must survive verbatim or
    // the proxy resolves the wrong upstream.
    stubProtocol('https:');
    expect(normalizeImageUrl('http://proxy.test/?src=http://origin.test/a.png'))
      .toBe('https://proxy.test/?src=http://origin.test/a.png');
  });
});

describe('normalizeImageUrl — on an HTTP page', () => {
  it('does not upgrade, because there is no Mixed Content problem to solve', () => {
    // Upgrading here would break local and intranet setups that have no TLS.
    stubProtocol('http:');
    expect(normalizeImageUrl('http://cdn.example.com/a.png'))
      .toBe('http://cdn.example.com/a.png');
  });
});

describe('normalizeImageUrl — outside the browser', () => {
  it('returns the URL unchanged during SSR rather than throwing on window', () => {
    vi.stubGlobal('window', undefined);
    expect(normalizeImageUrl('http://cdn.example.com/a.png'))
      .toBe('http://cdn.example.com/a.png');
  });
});

describe('normalizeImageUrl — empty input', () => {
  it('maps undefined and empty string to an empty string, never to "undefined"', () => {
    // A literal "undefined" in `src` sends a real request to a bogus path.
    stubProtocol('https:');
    expect(normalizeImageUrl(undefined)).toBe('');
    expect(normalizeImageUrl('')).toBe('');
  });
});

describe('normalizeImageUrls', () => {
  it('normalizes each entry and drops the ones that resolve to empty', () => {
    stubProtocol('https:');
    expect(normalizeImageUrls([
      'http://a.test/1.png',
      undefined,
      '',
      'https://b.test/2.png',
    ])).toEqual(['https://a.test/1.png', 'https://b.test/2.png']);
  });

  it('returns an empty array for an empty input', () => {
    stubProtocol('https:');
    expect(normalizeImageUrls([])).toEqual([]);
  });

  it('returns an empty array when every entry is blank', () => {
    stubProtocol('https:');
    expect(normalizeImageUrls([undefined, ''])).toEqual([]);
  });
});
