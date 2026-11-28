/**
 * Auth path normalization tests (auth/utils/path.ts).
 *
 * These gate whether the magic-link / OTP-in-URL auto-auth fires on the current
 * page. A locale prefix (`/ru/auth`) or trailing slash must NOT stop `/auth`
 * from matching — otherwise a localized magic link silently does nothing. And a
 * 2-letter path segment that is actually a route (not a locale) must not be
 * eaten (edge case documented below).
 */

import { describe, expect, it } from 'vitest';

import { isAllowedAuthPath, normalizePath } from '../utils/path';

describe('normalizePath', () => {
  it.each([
    ['/auth', '/auth'],
    ['/auth/', '/auth'],
    ['/ru/auth', '/auth'],
    ['/en/auth/', '/auth'],
    ['/ru/auth/callback', '/auth/callback'],
    ['/', '/'],
    ['', ''],
    ['/dashboard', '/dashboard'],
    ['/ru/', '/'],
  ])('normalizes %j → %j', (input, expected) => {
    expect(normalizePath(input)).toBe(expected);
  });

  it('returns empty string for null / undefined', () => {
    expect(normalizePath(null)).toBe('');
    expect(normalizePath(undefined)).toBe('');
  });

  it('strips only a leading 2-letter segment, not longer ones', () => {
    // '/abc/auth' — 'abc' is 3 letters, not a locale, so it stays.
    expect(normalizePath('/abc/auth')).toBe('/abc/auth');
  });
});

describe('isAllowedAuthPath', () => {
  it('matches the exact allowed path', () => {
    expect(isAllowedAuthPath('/auth', ['/auth'])).toBe(true);
  });
  it('matches with a locale prefix', () => {
    expect(isAllowedAuthPath('/ru/auth', ['/auth'])).toBe(true);
  });
  it('matches with a trailing slash', () => {
    expect(isAllowedAuthPath('/auth/', ['/auth'])).toBe(true);
  });
  it('matches a nested path under an allowed root', () => {
    expect(isAllowedAuthPath('/ru/auth/callback', ['/auth'])).toBe(true);
  });
  it('does NOT match an unrelated page', () => {
    expect(isAllowedAuthPath('/dashboard/device', ['/auth'])).toBe(false);
  });
  it('does NOT match a path that merely starts with the same letters', () => {
    // '/authentication' must not match allow-list entry '/auth'.
    expect(isAllowedAuthPath('/authentication', ['/auth'])).toBe(false);
  });
  it('honors multiple allowed paths', () => {
    expect(isAllowedAuthPath('/login', ['/auth', '/login'])).toBe(true);
  });
  it('returns false for null pathname', () => {
    expect(isAllowedAuthPath(null, ['/auth'])).toBe(false);
  });
});
