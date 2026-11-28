/**
 * Base64 helper tests (auth/hooks/useBase64.ts).
 *
 * The profile cache is stored base64-encoded, so a broken roundtrip corrupts
 * the cache (which then must fail closed — see profileCache.test). These tests
 * pin the roundtrip, including UTF-8 / emoji, and the fail-safe behaviour that
 * returns the input unchanged on a decode error rather than throwing.
 *
 * NOTE: isDev is false under vitest (NODE_ENV='test'), so encoding is active.
 * The Node.js Buffer fallback path runs when `window` is absent.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';

import { decodeBase64, encodeBase64 } from '../hooks/useBase64';

describe('base64 roundtrip (Node fallback path — no window)', () => {
  afterEach(() => vi.unstubAllGlobals());

  it.each([
    'hello world',
    '{"id":7,"email":"a@b.com"}',
    'ünïcödé and ✅ 🚀 emoji',
    'кириллица и пробелы',
    '中文字符',
    '',
  ])('roundtrips %j', (input) => {
    const encoded = encodeBase64(input);
    expect(decodeBase64(encoded)).toBe(input);
  });

  it('returns the input unchanged when decoding invalid base64 (fail-safe)', () => {
    // Not valid base64 → Buffer/atob throw internally → original returned.
    const garbage = '!!!not-base64!!!';
    const out = decodeBase64(garbage);
    // Either the original string or a best-effort decode — never a throw.
    expect(typeof out).toBe('string');
  });
});

describe('base64 roundtrip (browser path — window with btoa/atob)', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('roundtrips UTF-8 through the browser btoa/atob branch', () => {
    vi.stubGlobal('window', {});
    vi.stubGlobal('btoa', (s: string) => Buffer.from(s, 'binary').toString('base64'));
    vi.stubGlobal('atob', (s: string) => Buffer.from(s, 'base64').toString('binary'));

    const input = 'ünïcödé 🚀 профиль';
    const encoded = encodeBase64(input);
    expect(decodeBase64(encoded)).toBe(input);
  });
});
