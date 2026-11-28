/**
 * Auth error resolution tests (auth/utils/errors.ts).
 *
 * Turns whatever the auth layer throws (string, Error, DRF `{detail}`, axios-ish
 * nested `response.data.detail`, an `APIError`-shaped object) into a user-facing
 * string, with a stable fallback. The precedence order matters: server prose >
 * status-code copy > fallback, and it must never throw on null/odd shapes.
 */

import { describe, expect, it } from 'vitest';

import { AUTH_ERROR_KEYS, formatAuthError, resolveAuthError } from '../utils/errors';

describe('formatAuthError', () => {
  it('returns a plain string as-is', () => {
    expect(formatAuthError('Something broke')).toBe('Something broke');
  });

  it('prefers error.message (Error instances)', () => {
    expect(formatAuthError(new Error('boom'))).toBe('boom');
  });

  it('reads DRF-style { detail }', () => {
    expect(formatAuthError({ detail: 'Token is blacklisted' })).toBe('Token is blacklisted');
  });

  it('reads nested response.data.detail', () => {
    expect(formatAuthError({ response: { data: { detail: 'nested detail' } } })).toBe('nested detail');
  });

  it('message wins over detail when both present', () => {
    expect(formatAuthError({ message: 'msg', detail: 'det' })).toBe('msg');
  });

  it('detail wins over nested detail', () => {
    expect(
      formatAuthError({ detail: 'top', response: { data: { detail: 'deep' } } }),
    ).toBe('top');
  });

  it('falls back for null / undefined / empty object', () => {
    const FALLBACK = 'Something went wrong';
    expect(formatAuthError(null)).toBe(FALLBACK);
    expect(formatAuthError(undefined)).toBe(FALLBACK);
    expect(formatAuthError({})).toBe(FALLBACK);
    expect(formatAuthError(42)).toBe(FALLBACK);
  });

  it("prefers the caller's fallback when nothing else identifies the failure", () => {
    expect(formatAuthError({}, 'Failed to send OTP')).toBe('Failed to send OTP');
  });
});

/*
 * The regression this module exists for: a bare `HTTP 404:` under a sign-in
 * field. `APIError` builds that string itself when the response carries no
 * message, and `statusText` is empty under HTTP/2 — so it is a status line
 * wearing a message's clothes, and every extractor used to hand it straight to
 * the UI.
 */
describe('resolveAuthError — transport strings never reach the UI', () => {
  it('rejects the bare HTTP fallback and explains the status instead', () => {
    const err = { message: 'HTTP 404: ', statusCode: 404, name: 'APIError' };
    const { message, key } = resolveAuthError(err);

    expect(message).not.toMatch(/HTTP/);
    expect(key).toBe(AUTH_ERROR_KEYS.serverUnavailable);
  });

  it('HTTP 0 (no response: network, CORS, API restarting) is a network error, not "HTTP 0:"', () => {
    const { message, key } = resolveAuthError({ message: 'HTTP 0: ', statusCode: 0, name: 'APIError' });

    expect(message).not.toMatch(/HTTP/);
    expect(key).toBe(AUTH_ERROR_KEYS.networkError);
  });

  it('rejects it even when statusText filled it in', () => {
    expect(formatAuthError({ message: 'HTTP 500: Internal Server Error', statusCode: 500 }))
      .not.toMatch(/HTTP/);
  });

  it("outranks the caller's fallback with status-derived copy", () => {
    // A 404 reported as "Failed to send the code" blames the code, not the
    // endpoint that is missing.
    const { key } = resolveAuthError({ message: 'HTTP 404: ', statusCode: 404 }, 'Failed to send OTP');
    expect(key).toBe(AUTH_ERROR_KEYS.serverUnavailable);
  });
});

describe('resolveAuthError — status codes', () => {
  it.each([
    [401, AUTH_ERROR_KEYS.invalidCredentials],
    [403, AUTH_ERROR_KEYS.invalidCredentials],
    [404, AUTH_ERROR_KEYS.serverUnavailable],
    [429, AUTH_ERROR_KEYS.rateLimited],
    [500, AUTH_ERROR_KEYS.serverUnavailable],
    [503, AUTH_ERROR_KEYS.serverUnavailable],
  ])('maps %i to its key', (statusCode, expected) => {
    expect(resolveAuthError({ statusCode }).key).toBe(expected);
  });

  it('reads a Response-shaped `status` too', () => {
    expect(resolveAuthError({ status: 429 }).key).toBe(AUTH_ERROR_KEYS.rateLimited);
  });

  it('server prose outranks the status code', () => {
    const err = { response: { detail: 'This code has expired' }, statusCode: 400 };
    const { message, key } = resolveAuthError(err);

    expect(message).toBe('This code has expired');
    // No key: the backend already chose the words, in the caller's locale.
    expect(key).toBeUndefined();
  });

  it('reads the APIError body spellings the auth endpoints actually use', () => {
    expect(formatAuthError({ response: { error: 'Too many attempts' } })).toBe('Too many attempts');
    expect(formatAuthError({ response: { message: 'Account locked' } })).toBe('Account locked');
  });
});
